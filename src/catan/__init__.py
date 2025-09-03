"""
Catan Settlement Optimization Package
====================================

A comprehensive toolkit for optimal settlement placement in Settlers of Catan.
"""

from .hex_coords import HexCoord, generate_radius_2_board
from .board import CatanBoard, ResourceType, Tile
from .harbors import HarborManager, Harbor, HarborType
from .vertices import VertexManager, Vertex
from .scoring import SettlementScorer, ScoreBreakdown
from .state import GameState
from .recommend import SettlementRecommender, RecommendationResult
from .visualize import CatanVisualizer
from .io_utils import save_board_json, load_board_json, save_recommendations_csv

__version__ = "1.0.0"
__author__ = "Catan Analytics Team"

__all__ = [
    'HexCoord',
    'generate_radius_2_board',
    'CatanBoard',
    'ResourceType',
    'Tile',
    'HarborManager',
    'Harbor', 
    'HarborType',
    'VertexManager',
    'Vertex',
    'SettlementScorer',
    'ScoreBreakdown',
    'GameState',
    'SettlementRecommender',
    'RecommendationResult',
    'CatanVisualizer',
    'save_board_json',
    'load_board_json',
    'save_recommendations_csv'
]

__version__ = "1.0.0"
