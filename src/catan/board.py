"""
Catan Board Generation and Management
====================================

This module handles the creation and management of Catan boards with proper
tile distributions, number tokens, harbors, and validation.
"""

import random
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from .hex_coords import HexCoord, generate_radius_2_board
from .harbors import HarborManager


class ResourceType(Enum):
    """Resource types in Catan."""
    WOOD = "wood"
    BRICK = "brick" 
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"
    DESERT = "desert"


@dataclass
class Tile:
    """A hex tile on the Catan board."""
    coord: HexCoord
    resource: ResourceType
    number: int  # 0 for desert, 2-12 for others
    has_robber: bool = False
    
    @property
    def probability(self) -> float:
        """Dice roll probability for this tile."""
        if self.number == 0 or self.has_robber:
            return 0.0
        
        # Probability of rolling each number (2-12, excluding 7)
        probs = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
        return probs.get(self.number, 0) / 36.0
    
    @property
    def pips(self) -> int:
        """Number of pips (dots) on the number token."""
        if self.number == 0:
            return 0
        return 6 - abs(7 - self.number)
    
    @property
    def is_high_probability(self) -> bool:
        """Whether this is a high-probability number (6 or 8)."""
        return self.number in (6, 8)


class CatanBoard:
    """Represents a complete Catan board with tiles and number tokens."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a Catan board.
        
        Args:
            seed: Random seed for deterministic board generation
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        self.hexes: Set[HexCoord] = generate_radius_2_board()
        self.tiles: Dict[HexCoord, Tile] = {}
        self.harbors = HarborManager()
        self.robber_position: Optional[HexCoord] = None
        
    def create_standard_board(self, randomize: bool = False) -> None:
        """
        Create a standard Catan board with official tile and number distribution.
        
        Args:
            randomize: If True, shuffle tiles and numbers randomly. If False, use deterministic layout.
        """
        # Official base game tile distribution
        tile_types = [
            ResourceType.WOOD,    # 4 forest tiles
            ResourceType.WOOD,
            ResourceType.WOOD,
            ResourceType.WOOD,
            ResourceType.BRICK,   # 3 hills tiles
            ResourceType.BRICK,
            ResourceType.BRICK,
            ResourceType.SHEEP,   # 4 pasture tiles
            ResourceType.SHEEP,
            ResourceType.SHEEP,
            ResourceType.SHEEP,
            ResourceType.WHEAT,   # 4 fields tiles
            ResourceType.WHEAT,
            ResourceType.WHEAT,
            ResourceType.WHEAT,
            ResourceType.ORE,     # 3 mountains tiles
            ResourceType.ORE,
            ResourceType.ORE,
            ResourceType.DESERT,  # 1 desert tile
        ]
        
        # Official number token distribution (no 7)
        numbers = [
            2,           # 1 token
            3, 3,        # 2 tokens
            4, 4,        # 2 tokens
            5, 5,        # 2 tokens
            6, 6,        # 2 tokens
            8, 8,        # 2 tokens
            9, 9,        # 2 tokens
            10, 10,      # 2 tokens
            11, 11,      # 2 tokens
            12,          # 1 token
        ]
        
        assert len(tile_types) == 19, f"Expected 19 tiles, got {len(tile_types)}"
        assert len(numbers) == 18, f"Expected 18 numbers, got {len(numbers)}"
        
        if randomize:
            random.shuffle(tile_types)
            random.shuffle(numbers)
        
        # Convert hex coordinates to a sorted list for deterministic placement
        hex_coords = sorted(self.hexes, key=lambda h: (h.r, h.q))
        
        # Assign tiles to hex coordinates
        number_idx = 0
        for i, coord in enumerate(hex_coords):
            resource = tile_types[i]
            
            if resource == ResourceType.DESERT:
                number = 0
                self.robber_position = coord
            else:
                number = numbers[number_idx]
                number_idx += 1
            
            self.tiles[coord] = Tile(
                coord=coord,
                resource=resource,
                number=number,
                has_robber=(resource == ResourceType.DESERT)
            )
    
    def get_harbor_at_vertex(self, vertex_id: int):
        """Get harbor accessible from a vertex."""
        return self.harbors.get_harbor_at_vertex(vertex_id)
    
    def is_harbor_vertex(self, vertex_id: int) -> bool:
        """Check if vertex has harbor access."""
        return self.harbors.is_harbor_vertex(vertex_id)
    
    def get_harbor_bonus(self, vertex_id: int, resource: ResourceType) -> float:
        """Get harbor trading bonus for vertex and resource."""
        return self.harbors.get_harbor_bonus(vertex_id, resource)
    
    def get_all_harbors(self):
        """Get all harbors on the board."""
        return self.harbors.get_all_harbors()
    
    def validate_board(self) -> bool:
        """
        Validate that the board follows official Catan rules.
        
        Returns:
            True if board is valid, False otherwise
        """
        # Check hex count
        if len(self.tiles) != 19:
            return False
        
        # Check resource distribution
        resource_counts = {}
        number_counts = {}
        desert_count = 0
        
        for tile in self.tiles.values():
            # Count resources
            resource_counts[tile.resource] = resource_counts.get(tile.resource, 0) + 1
            
            # Count numbers
            if tile.number > 0:
                number_counts[tile.number] = number_counts.get(tile.number, 0) + 1
            else:
                desert_count += 1
        
        # Validate resource distribution
        expected_resources = {
            ResourceType.WOOD: 4,
            ResourceType.BRICK: 3,
            ResourceType.SHEEP: 4,
            ResourceType.WHEAT: 4,
            ResourceType.ORE: 3,
            ResourceType.DESERT: 1
        }
        
        if resource_counts != expected_resources:
            return False
        
        # Validate number distribution
        expected_numbers = {
            2: 1, 3: 2, 4: 2, 5: 2, 6: 2,
            8: 2, 9: 2, 10: 2, 11: 2, 12: 1
        }
        
        if number_counts != expected_numbers:
            return False
        
        # Validate desert has no number
        if desert_count != 1:
            return False
        
        # Check that robber is on desert
        if self.robber_position is None:
            return False
        
        desert_tile = self.tiles.get(self.robber_position)
        if not desert_tile or desert_tile.resource != ResourceType.DESERT:
            return False
        
        return True
    
    def check_adjacent_high_numbers(self) -> List[Tuple[HexCoord, HexCoord]]:
        """
        Check for adjacent 6s and 8s (which should be avoided in setup).
        
        Returns:
            List of (coord1, coord2) pairs where adjacent tiles both have 6 or 8
        """
        from .hex_coords import hex_neighbors
        
        adjacent_pairs = []
        
        for coord, tile in self.tiles.items():
            if tile.number in (6, 8):
                for neighbor_coord in hex_neighbors(coord):
                    if neighbor_coord in self.tiles:
                        neighbor_tile = self.tiles[neighbor_coord]
                        if neighbor_tile.number in (6, 8):
                            # Sort to avoid duplicates
                            pair = tuple(sorted([coord, neighbor_coord], key=lambda h: (h.q, h.r)))
                            if pair not in adjacent_pairs:
                                adjacent_pairs.append(pair)
        
        return adjacent_pairs
    
    def get_board_summary(self) -> Dict:
        """Get a summary of the board configuration."""
        resource_counts = {}
        number_counts = {}
        
        for tile in self.tiles.values():
            resource_counts[tile.resource.value] = resource_counts.get(tile.resource.value, 0) + 1
            if tile.number > 0:
                number_counts[tile.number] = number_counts.get(tile.number, 0) + 1
        
        harbor_summary = self.harbors.get_harbor_summary()
        
        return {
            "total_tiles": len(self.tiles),
            "resource_distribution": resource_counts,
            "number_distribution": number_counts,
            "robber_position": (self.robber_position.q, self.robber_position.r) if self.robber_position else None,
            "adjacent_high_numbers": len(self.check_adjacent_high_numbers()),
            "harbor_summary": harbor_summary,
            "is_valid": self.validate_board()
        }
