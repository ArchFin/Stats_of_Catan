"""
Current Game State Management
============================

Handles occupied vertices, roads, and player state information.
"""

from typing import Dict, Set, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class StructureType(Enum):
    """Types of structures that can be placed on the board."""
    SETTLEMENT = "settlement"
    CITY = "city"
    ROAD = "road"


@dataclass
class Structure:
    """A structure placed on the board."""
    type: StructureType
    player_id: int
    vertex_id: Optional[int] = None  # For settlements/cities
    edge: Optional[tuple] = None     # For roads: (vertex1_id, vertex2_id)


class GameState:
    """Represents the current state of a Catan game."""
    
    def __init__(self, num_players: int = 4):
        """
        Initialize game state.
        
        Args:
            num_players: Number of players in the game
        """
        self.num_players = num_players
        self.occupied_vertices: Set[int] = set()
        self.settlements: Dict[int, int] = {}  # vertex_id -> player_id
        self.cities: Dict[int, int] = {}       # vertex_id -> player_id
        self.roads: Set[Tuple[int, int]] = set()  # Set of (vertex1_id, vertex2_id) edges
        self.player_roads: Dict[int, Set[Tuple[int, int]]] = {i: set() for i in range(num_players)}
        
        # Turn information
        self.current_player: int = 0
        self.turn_number: int = 0
        self.is_initial_placement: bool = True
    
    def add_settlement(self, vertex_id: int, player_id: int) -> bool:
        """
        Add a settlement at the given vertex.
        
        Args:
            vertex_id: ID of the vertex
            player_id: ID of the player (0-based)
        
        Returns:
            True if settlement was added successfully
        """
        if vertex_id in self.occupied_vertices:
            return False
        
        if player_id < 0 or player_id >= self.num_players:
            return False
        
        self.settlements[vertex_id] = player_id
        self.occupied_vertices.add(vertex_id)
        return True
    
    def add_city(self, vertex_id: int, player_id: int) -> bool:
        """
        Upgrade a settlement to a city.
        
        Args:
            vertex_id: ID of the vertex
            player_id: ID of the player (0-based)
        
        Returns:
            True if city was added successfully
        """
        if vertex_id not in self.settlements:
            return False
        
        if self.settlements[vertex_id] != player_id:
            return False
        
        # Move from settlement to city
        del self.settlements[vertex_id]
        self.cities[vertex_id] = player_id
        return True
    
    def add_road(self, vertex1_id: int, vertex2_id: int, player_id: int) -> bool:
        """
        Add a road between two vertices.
        
        Args:
            vertex1_id: ID of first vertex
            vertex2_id: ID of second vertex
            player_id: ID of the player (0-based)
        
        Returns:
            True if road was added successfully
        """
        if player_id < 0 or player_id >= self.num_players:
            return False
        
        # Normalize edge representation
        edge = tuple(sorted([vertex1_id, vertex2_id]))
        
        if edge in self.roads:
            return False  # Road already exists
        
        self.roads.add(edge)
        self.player_roads[player_id].add(edge)
        return True
    
    def remove_settlement(self, vertex_id: int) -> bool:
        """Remove a settlement from the given vertex."""
        if vertex_id in self.settlements:
            del self.settlements[vertex_id]
            self.occupied_vertices.discard(vertex_id)
            return True
        return False
    
    def remove_city(self, vertex_id: int) -> bool:
        """Remove a city from the given vertex."""
        if vertex_id in self.cities:
            del self.cities[vertex_id]
            self.occupied_vertices.discard(vertex_id)
            return True
        return False
    
    def remove_road(self, vertex1_id: int, vertex2_id: int) -> bool:
        """Remove a road between two vertices."""
        edge = tuple(sorted([vertex1_id, vertex2_id]))
        
        if edge in self.roads:
            self.roads.remove(edge)
            
            # Remove from player roads
            for player_id in range(self.num_players):
                self.player_roads[player_id].discard(edge)
            
            return True
        return False
    
    def get_player_structures(self, player_id: int) -> Dict:
        """
        Get all structures for a specific player.
        
        Args:
            player_id: ID of the player
        
        Returns:
            Dictionary with settlements, cities, and roads for the player
        """
        player_settlements = {v: p for v, p in self.settlements.items() if p == player_id}
        player_cities = {v: p for v, p in self.cities.items() if p == player_id}
        player_roads = self.player_roads.get(player_id, set())
        
        return {
            'settlements': player_settlements,
            'cities': player_cities, 
            'roads': list(player_roads),
            'total_structures': len(player_settlements) + len(player_cities) + len(player_roads)
        }
    
    def get_structure_at_vertex(self, vertex_id: int) -> Optional[Dict]:
        """
        Get information about the structure at a vertex.
        
        Args:
            vertex_id: ID of the vertex
        
        Returns:
            Dictionary with structure info, or None if no structure
        """
        if vertex_id in self.settlements:
            return {
                'type': StructureType.SETTLEMENT,
                'player_id': self.settlements[vertex_id]
            }
        elif vertex_id in self.cities:
            return {
                'type': StructureType.CITY,
                'player_id': self.cities[vertex_id]
            }
        return None
    
    def is_vertex_occupied(self, vertex_id: int) -> bool:
        """Check if a vertex is occupied by any structure."""
        return vertex_id in self.occupied_vertices
    
    def get_game_summary(self) -> Dict:
        """Get a summary of the current game state."""
        summary = {
            'num_players': self.num_players,
            'current_player': self.current_player,
            'turn_number': self.turn_number,
            'is_initial_placement': self.is_initial_placement,
            'total_settlements': len(self.settlements),
            'total_cities': len(self.cities),
            'total_roads': len(self.roads),
            'players': {}
        }
        
        for player_id in range(self.num_players):
            summary['players'][player_id] = self.get_player_structures(player_id)
        
        return summary
    
    def to_dict(self) -> Dict:
        """Convert game state to dictionary for JSON serialization."""
        return {
            'num_players': self.num_players,
            'current_player': self.current_player,
            'turn_number': self.turn_number,
            'is_initial_placement': self.is_initial_placement,
            'settlements': self.settlements,
            'cities': self.cities,
            'roads': list(self.roads),
            'player_roads': {str(k): list(v) for k, v in self.player_roads.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """Create game state from dictionary (for JSON deserialization)."""
        state = cls(data['num_players'])
        state.current_player = data['current_player']
        state.turn_number = data['turn_number']
        state.is_initial_placement = data['is_initial_placement']
        state.settlements = data['settlements']
        state.cities = data['cities']
        state.occupied_vertices = set(state.settlements.keys()) | set(state.cities.keys())
        state.roads = set(tuple(road) for road in data['roads'])
        state.player_roads = {
            int(k): set(tuple(road) for road in v) 
            for k, v in data['player_roads'].items()
        }
        return state
