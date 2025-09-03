"""
Vertex Discovery and Settlement Position Management
==================================================

Handles vertex enumeration, deduplication, distance rule checks, and settlement placement logic.
"""

import math
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

from .hex_coords import HexCoord, hex_corners, axial_to_pixel
from .board import CatanBoard


@dataclass(frozen=True)
class Vertex:
    """A vertex where settlements can be placed."""
    id: int
    position: Tuple[float, float]  # (x, y) pixel coordinates
    incident_hexes: Tuple[HexCoord, ...]  # Hex coordinates that share this vertex
    
    def __hash__(self):
        return hash(self.id)


class VertexManager:
    """Manages all vertices on the Catan board and settlement placement rules."""
    
    def __init__(self, board: CatanBoard, tolerance: float = 1e-6):
        """
        Initialize vertex manager for a board.
        
        Args:
            board: The Catan board
            tolerance: Tolerance for considering two points the same
        """
        self.board = board
        self.tolerance = tolerance
        self.vertices: Dict[int, Vertex] = {}
        self.position_to_vertex: Dict[Tuple[float, float], int] = {}
        self.adjacency: Dict[int, Set[int]] = {}  # vertex_id -> set of adjacent vertex_ids
        
        self._discover_vertices()
        self._build_adjacency()
    
    def _discover_vertices(self) -> None:
        """Discover all unique vertices from hex corners."""
        vertex_id = 0
        
        for hex_coord in self.board.hexes:
            corners = hex_corners(hex_coord, size=1.0)
            
            for corner in corners:
                # Round coordinates to handle floating point precision
                rounded_pos = (round(corner[0] / self.tolerance) * self.tolerance,
                             round(corner[1] / self.tolerance) * self.tolerance)
                
                if rounded_pos not in self.position_to_vertex:
                    # New vertex
                    self.position_to_vertex[rounded_pos] = vertex_id
                    self.vertices[vertex_id] = Vertex(
                        id=vertex_id,
                        position=rounded_pos,
                        incident_hexes=(hex_coord,)
                    )
                    vertex_id += 1
                else:
                    # Existing vertex - add this hex to its incident hexes
                    existing_id = self.position_to_vertex[rounded_pos]
                    existing_vertex = self.vertices[existing_id]
                    
                    # Update with new incident hex
                    updated_hexes = existing_vertex.incident_hexes + (hex_coord,)
                    self.vertices[existing_id] = Vertex(
                        id=existing_id,
                        position=existing_vertex.position,
                        incident_hexes=updated_hexes
                    )
    
    def _build_adjacency(self) -> None:
        """Build adjacency graph between vertices (for distance rule)."""
        for vertex_id in self.vertices:
            self.adjacency[vertex_id] = set()
        
        # Two vertices are adjacent if they share an edge of a hex
        for hex_coord in self.board.hexes:
            corners = hex_corners(hex_coord, size=1.0)
            vertex_ids = []
            
            # Find vertex IDs for this hex's corners
            for corner in corners:
                rounded_pos = (round(corner[0] / self.tolerance) * self.tolerance,
                             round(corner[1] / self.tolerance) * self.tolerance)
                vertex_ids.append(self.position_to_vertex[rounded_pos])
            
            # Connect adjacent corners around the hex
            for i in range(6):
                next_i = (i + 1) % 6
                v1, v2 = vertex_ids[i], vertex_ids[next_i]
                self.adjacency[v1].add(v2)
                self.adjacency[v2].add(v1)
    
    def get_vertex_count(self) -> int:
        """Get total number of vertices."""
        return len(self.vertices)
    
    def get_legal_vertices(self, occupied_vertices: Set[int] = None) -> Set[int]:
        """
        Get all vertices where settlements can be legally placed.
        
        Args:
            occupied_vertices: Set of vertex IDs that already have settlements
        
        Returns:
            Set of vertex IDs where new settlements can be placed
        """
        if occupied_vertices is None:
            occupied_vertices = set()
        
        legal = set()
        
        for vertex_id in self.vertices:
            if vertex_id in occupied_vertices:
                continue
            
            # Check distance rule: no settlements on adjacent vertices
            is_legal = True
            for adjacent_id in self.adjacency[vertex_id]:
                if adjacent_id in occupied_vertices:
                    is_legal = False
                    break
            
            if is_legal:
                legal.add(vertex_id)
        
        return legal
    
    def is_valid_placement(self, vertex_id: int, occupied_vertices: Set[int] = None) -> bool:
        """
        Check if a settlement can be placed at the given vertex.
        
        Args:
            vertex_id: ID of the vertex to check
            occupied_vertices: Set of vertex IDs that already have settlements
        
        Returns:
            True if placement is valid, False otherwise
        """
        if occupied_vertices is None:
            occupied_vertices = set()
        
        if vertex_id not in self.vertices:
            return False
        
        if vertex_id in occupied_vertices:
            return False
        
        # Check distance rule
        for adjacent_id in self.adjacency[vertex_id]:
            if adjacent_id in occupied_vertices:
                return False
        
        return True
    
    def get_vertex_info(self, vertex_id: int) -> Optional[Dict]:
        """
        Get detailed information about a vertex.
        
        Args:
            vertex_id: ID of the vertex
        
        Returns:
            Dictionary with vertex information, or None if vertex doesn't exist
        """
        if vertex_id not in self.vertices:
            return None
        
        vertex = self.vertices[vertex_id]
        
        # Get resource information from incident hexes
        resources = {}
        total_probability = 0.0
        total_pips = 0
        
        for hex_coord in vertex.incident_hexes:
            if hex_coord in self.board.tiles:
                tile = self.board.tiles[hex_coord]
                if tile.resource.value not in resources:
                    resources[tile.resource.value] = {
                        'probability': 0.0,
                        'pips': 0,
                        'numbers': []
                    }
                
                resources[tile.resource.value]['probability'] += tile.probability
                resources[tile.resource.value]['pips'] += tile.pips
                if tile.number > 0:
                    resources[tile.resource.value]['numbers'].append(tile.number)
                
                total_probability += tile.probability
                total_pips += tile.pips
        
        return {
            'vertex_id': vertex_id,
            'position': vertex.position,
            'incident_hexes': [(h.q, h.r) for h in vertex.incident_hexes],
            'resources': resources,
            'total_probability': total_probability,
            'total_pips': total_pips,
            'adjacent_vertices': list(self.adjacency[vertex_id])
        }
    
    def get_vertices_csv_data(self) -> List[Dict]:
        """
        Get vertex data in format suitable for CSV export.
        
        Returns:
            List of dictionaries with vertex information
        """
        data = []
        
        for vertex_id in sorted(self.vertices.keys()):
            vertex = self.vertices[vertex_id]
            
            # Calculate if this vertex is on the board boundary
            # (vertices with fewer than 3 incident hexes are on the boundary)
            is_boundary = len(vertex.incident_hexes) < 3
            
            data.append({
                'vertex_id': vertex_id,
                'x': vertex.position[0],
                'y': vertex.position[1],
                'incident_hexes': ','.join(f"({h.q},{h.r})" for h in vertex.incident_hexes),
                'hex_count': len(vertex.incident_hexes),
                'is_boundary': is_boundary,
                'legal_flag': True  # All vertices are theoretically legal until occupied
            })
        
        return data
    
    def calculate_vertex_distances(self) -> Dict[Tuple[int, int], int]:
        """
        Calculate distances between all pairs of vertices (for analysis).
        
        Returns:
            Dictionary mapping (vertex1_id, vertex2_id) to distance
        """
        distances = {}
        
        # Use BFS to calculate shortest path distances
        from collections import deque
        
        for start_vertex in self.vertices:
            visited = {start_vertex: 0}
            queue = deque([start_vertex])
            
            while queue:
                current = queue.popleft()
                current_dist = visited[current]
                
                for neighbor in self.adjacency[current]:
                    if neighbor not in visited:
                        visited[neighbor] = current_dist + 1
                        queue.append(neighbor)
            
            for end_vertex, distance in visited.items():
                if start_vertex <= end_vertex:  # Only store each pair once
                    distances[(start_vertex, end_vertex)] = distance
        
        return distances
