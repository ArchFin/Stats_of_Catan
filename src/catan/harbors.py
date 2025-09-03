"""
Harbor System for Catan
========================

Manages harbor placement, types, and trading bonuses.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .hex_coords import HexCoord, axial_to_pixel


class ResourceType(Enum):
    """Resource types in Catan (copy to avoid circular import)."""
    WOOD = "wood"
    BRICK = "brick" 
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"
    DESERT = "desert"


class HarborType(Enum):
    """Types of harbors in Catan."""
    GENERIC = "3:1"     # 3:1 any resource harbor
    WOOD = "2:1_wood"   # 2:1 wood harbor
    BRICK = "2:1_brick" # 2:1 brick harbor
    SHEEP = "2:1_sheep" # 2:1 sheep harbor
    WHEAT = "2:1_wheat" # 2:1 wheat harbor
    ORE = "2:1_ore"     # 2:1 ore harbor


@dataclass
class Harbor:
    """A harbor on the Catan board."""
    type: HarborType
    vertices: List[int]  # Vertex IDs where this harbor can be accessed
    position: Tuple[float, float]  # (x, y) pixel coordinates for visualization
    resource: Optional[ResourceType] = None  # Resource type for 2:1 harbors
    ratio: int = 3  # Trading ratio (2 or 3)
    
    def __post_init__(self):
        """Set resource and ratio based on harbor type."""
        if self.type == HarborType.GENERIC:
            self.resource = None
            self.ratio = 3
        else:
            # Extract resource from 2:1 harbor type
            resource_name = self.type.value.split('_')[1]
            self.resource = ResourceType(resource_name)
            self.ratio = 2


class HarborManager:
    """Manages harbor placement and access on the Catan board."""
    
    def __init__(self):
        """Initialize harbor manager with standard Catan harbor configuration."""
        self.harbors: Dict[int, Harbor] = {}  # harbor_id -> Harbor
        self.vertex_to_harbor: Dict[int, int] = {}  # vertex_id -> harbor_id
        self._setup_standard_harbors()
    
    def _setup_standard_harbors(self) -> None:
        """Set up the standard 9 harbors for a Catan board with correct positions."""
        # Harbor configurations with vertices - positions will be calculated dynamically
        # Using the ORIGINAL correct vertex pairs (reverting the "fix")
        harbor_configs = [
            # (harbor_type, vertex_ids)
            (HarborType.BRICK, [39, 52]),     # ✅ Already correct
            (HarborType.WOOD, [41, 36]),      # ✅ Already correct
            (HarborType.SHEEP, [21, 22]),     # � Back to original
            (HarborType.WHEAT, [49, 0]),      # � Back to original
            (HarborType.ORE, [3, 53]),        # � Back to original
            (HarborType.GENERIC, [50, 51]),   # � Back to original
            (HarborType.GENERIC, [46, 47]),   # � Back to original
            (HarborType.GENERIC, [33, 34]),   # � Back to original
            (HarborType.GENERIC, [15, 16]),   # � Back to original
        ]
        
        for harbor_id, (harbor_type, vertex_ids) in enumerate(harbor_configs):
            # Calculate position dynamically based on vertex locations
            position = self._calculate_harbor_position(vertex_ids)
            
            harbor = Harbor(
                type=harbor_type,
                vertices=vertex_ids,
                position=position
            )
            
            self.harbors[harbor_id] = harbor
            
            # Map vertices to harbor
            for vertex_id in vertex_ids:
                self.vertex_to_harbor[vertex_id] = harbor_id
    
    def _calculate_harbor_position(self, vertex_ids: List[int]) -> Tuple[float, float]:
        """Calculate harbor position based on vertex locations."""
        # For now, return a placeholder - this will be overridden by vertex manager
        # The actual calculation will happen in the visualization layer
        return (0.0, 0.0)
    
    def get_harbor_at_vertex(self, vertex_id: int) -> Optional[Harbor]:
        """
        Get the harbor accessible from a vertex.
        
        Args:
            vertex_id: ID of the vertex
        
        Returns:
            Harbor object if vertex has harbor access, None otherwise
        """
        harbor_id = self.vertex_to_harbor.get(vertex_id)
        if harbor_id is not None:
            return self.harbors[harbor_id]
        return None
    
    def is_harbor_vertex(self, vertex_id: int) -> bool:
        """Check if a vertex has harbor access."""
        return vertex_id in self.vertex_to_harbor
    
    def get_harbor_bonus(self, vertex_id: int, resource: ResourceType) -> float:
        """
        Calculate harbor trading bonus for a vertex and resource.
        
        Args:
            vertex_id: ID of the vertex
            resource: Resource type being traded
        
        Returns:
            Trading bonus multiplier (1.0 = no bonus, 1.5 = 2:1 harbor, 1.33 = 3:1 harbor)
        """
        harbor = self.get_harbor_at_vertex(vertex_id)
        if not harbor:
            return 1.0  # No harbor bonus
        
        if harbor.type == HarborType.GENERIC:
            return 1.33  # 3:1 generic harbor (33% bonus)
        elif harbor.resource == resource:
            return 1.5   # 2:1 specific resource harbor (50% bonus)
        else:
            return 1.0   # Harbor doesn't match resource
    
    def get_harbor_score(self, vertex_id: int, strategy: str = 'balanced') -> float:
        """
        Calculate harbor access score for settlement scoring.
        
        Args:
            vertex_id: ID of the vertex
            strategy: Strategy preference
        
        Returns:
            Harbor score (0-30 points)
        """
        harbor = self.get_harbor_at_vertex(vertex_id)
        if not harbor:
            return 0.0
        
        if harbor.type == HarborType.GENERIC:
            base_score = 15.0  # 3:1 harbors are generally useful
        else:
            base_score = 25.0  # 2:1 harbors are more valuable
            
            # Strategy-specific bonuses
            if strategy == 'road_focused' and harbor.resource in (ResourceType.WOOD, ResourceType.BRICK):
                base_score += 5.0
            elif strategy == 'dev_focused' and harbor.resource in (ResourceType.ORE, ResourceType.WHEAT, ResourceType.SHEEP):
                base_score += 5.0
            elif strategy == 'city_focused' and harbor.resource in (ResourceType.ORE, ResourceType.WHEAT):
                base_score += 5.0
        
        return base_score
    
    def get_all_harbors(self) -> Dict[int, Harbor]:
        """Get all harbors on the board."""
        return self.harbors.copy()
    
    def get_harbor_summary(self) -> Dict:
        """Get summary information about harbors."""
        harbor_types = {}
        vertex_count = 0
        
        for harbor in self.harbors.values():
            harbor_types[harbor.type.value] = harbor_types.get(harbor.type.value, 0) + 1
            vertex_count += len(harbor.vertices)
        
        return {
            'total_harbors': len(self.harbors),
            'harbor_types': harbor_types,
            'total_harbor_vertices': vertex_count,
            'generic_harbors': sum(1 for h in self.harbors.values() if h.type == HarborType.GENERIC),
            'resource_harbors': sum(1 for h in self.harbors.values() if h.type != HarborType.GENERIC)
        }
    
    def export_harbors_to_dict(self) -> Dict:
        """Export harbor data for JSON serialization."""
        harbors_data = {}
        
        for harbor_id, harbor in self.harbors.items():
            harbors_data[str(harbor_id)] = {
                'type': harbor.type.value,
                'vertices': harbor.vertices,
                'position': harbor.position,
                'resource': harbor.resource.value if harbor.resource else None,
                'ratio': harbor.ratio
            }
        
        return harbors_data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HarborManager':
        """Create harbor manager from dictionary data."""
        manager = cls.__new__(cls)  # Create without calling __init__
        manager.harbors = {}
        manager.vertex_to_harbor = {}
        
        for harbor_id_str, harbor_data in data.items():
            harbor_id = int(harbor_id_str)
            
            harbor_type = HarborType(harbor_data['type'])
            resource = ResourceType(harbor_data['resource']) if harbor_data['resource'] else None
            
            harbor = Harbor(
                type=harbor_type,
                vertices=harbor_data['vertices'],
                position=tuple(harbor_data['position']),
                resource=resource,
                ratio=harbor_data['ratio']
            )
            
            manager.harbors[harbor_id] = harbor
            
            for vertex_id in harbor.vertices:
                manager.vertex_to_harbor[vertex_id] = harbor_id
        
        return manager
