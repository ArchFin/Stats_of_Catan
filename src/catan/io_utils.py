"""
Input/Output Utilities
=====================

Load and save JSON/CSV artifacts for board data and analysis results.
"""

import json
import csv
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .board import CatanBoard, ResourceType, Tile
from .hex_coords import HexCoord
from .state import GameState
from .recommend import RecommendationResult


def save_board_json(board: CatanBoard, filepath: str) -> None:
    """
    Save board configuration to JSON file.
    
    Args:
        board: The Catan board to save
        filepath: Path to save the JSON file
    """
    data = {
        'metadata': {
            'seed': board.seed,
            'total_tiles': len(board.tiles),
            'is_valid': board.validate_board()
        },
        'tiles': []
    }
    
    for hex_coord, tile in board.tiles.items():
        tile_data = {
            'q': hex_coord.q,
            'r': hex_coord.r,
            'resource': tile.resource.value,
            'number': tile.number,
            'has_robber': tile.has_robber,
            'probability': tile.probability,
            'pips': tile.pips,
            'is_high_probability': tile.is_high_probability
        }
        data['tiles'].append(tile_data)
    
    # Add robber position
    if board.robber_position:
        data['robber_position'] = {
            'q': board.robber_position.q,
            'r': board.robber_position.r
        }
    
    # Add harbor data
    data['harbors'] = board.harbors.export_harbors_to_dict()
    
    # Add board summary
    data['summary'] = board.get_board_summary()
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_board_json(filepath: str) -> CatanBoard:
    """
    Load board configuration from JSON file.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        CatanBoard instance
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Create board
    seed = data['metadata'].get('seed')
    board = CatanBoard(seed=seed)
    board.hexes = set()
    board.tiles = {}
    
    # Load tiles
    for tile_data in data['tiles']:
        hex_coord = HexCoord(tile_data['q'], tile_data['r'])
        board.hexes.add(hex_coord)
        
        tile = Tile(
            coord=hex_coord,
            resource=ResourceType(tile_data['resource']),
            number=tile_data['number'],
            has_robber=tile_data['has_robber']
        )
        board.tiles[hex_coord] = tile
    
    # Set robber position
    if 'robber_position' in data:
        robber_data = data['robber_position']
        board.robber_position = HexCoord(robber_data['q'], robber_data['r'])
    
    # Load harbor data if available
    if 'harbors' in data:
        from .harbors import HarborManager
        board.harbors = HarborManager.from_dict(data['harbors'])
    
    return board


def save_vertices_csv(vertex_manager, filepath: str) -> None:
    """
    Save vertex information to CSV file.
    
    Args:
        vertex_manager: VertexManager instance
        filepath: Path to save the CSV file
    """
    data = vertex_manager.get_vertices_csv_data()
    
    fieldnames = ['vertex_id', 'x', 'y', 'incident_hexes', 'hex_count', 'is_boundary', 'legal_flag']
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_vertices_csv(filepath: str) -> List[Dict]:
    """
    Load vertex information from CSV file.
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        List of vertex data dictionaries
    """
    vertices = []
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['vertex_id'] = int(row['vertex_id'])
            row['x'] = float(row['x'])
            row['y'] = float(row['y'])
            row['hex_count'] = int(row['hex_count'])
            row['is_boundary'] = row['is_boundary'].lower() == 'true'
            row['legal_flag'] = row['legal_flag'].lower() == 'true'
            vertices.append(row)
    
    return vertices


def save_game_state_json(game_state: GameState, filepath: str) -> None:
    """
    Save game state to JSON file.
    
    Args:
        game_state: GameState instance
        filepath: Path to save the JSON file
    """
    data = game_state.to_dict()
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_game_state_json(filepath: str) -> GameState:
    """
    Load game state from JSON file.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        GameState instance
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return GameState.from_dict(data)


def save_recommendations_json(recommendations: List[RecommendationResult], filepath: str,
                            metadata: Optional[Dict] = None) -> None:
    """
    Save settlement recommendations to JSON file.
    
    Args:
        recommendations: List of RecommendationResult objects
        filepath: Path to save the JSON file
        metadata: Optional metadata to include
    """
    data = {
        'recommendations': [rec.to_dict() for rec in recommendations],
        'metadata': metadata or {}
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_recommendations_json(filepath: str) -> Tuple[List[Dict], Dict]:
    """
    Load settlement recommendations from JSON file.
    
    Args:
        filepath: Path to the JSON file
    
    Returns:
        Tuple of (recommendations list, metadata dict)
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return data['recommendations'], data.get('metadata', {})


def save_recommendations_csv(recommendations: List[RecommendationResult], filepath: str) -> None:
    """
    Save settlement recommendations to CSV file.
    
    Args:
        recommendations: List of RecommendationResult objects
        filepath: Path to save the CSV file
    """
    fieldnames = [
        'rank', 'vertex_id', 'total_score', 
        'production_score', 'balance_score', 'road_score', 
        'dev_score', 'robber_penalty', 'blocking_score',
        'justification'
    ]
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for rec in recommendations:
            sb = rec.score_breakdown
            writer.writerow({
                'rank': rec.rank,
                'vertex_id': rec.vertex_id,
                'total_score': f"{rec.score:.2f}",
                'production_score': f"{sb.production_score:.2f}",
                'balance_score': f"{sb.balance_score:.2f}",
                'road_score': f"{sb.road_score:.2f}",
                'dev_score': f"{sb.dev_score:.2f}",
                'robber_penalty': f"{sb.robber_penalty:.2f}",
                'blocking_score': f"{sb.blocking_score:.2f}",
                'justification': rec.justification
            })


def create_example_state_file(filepath: str, num_players: int = 4) -> None:
    """
    Create an example game state file for testing.
    
    Args:
        filepath: Path to save the example file
        num_players: Number of players in the example game
    """
    state = GameState(num_players)
    
    # Add some example settlements and roads
    state.add_settlement(3, 0)   # Player 0 settlement at vertex 3
    state.add_settlement(15, 1)  # Player 1 settlement at vertex 15
    state.add_settlement(32, 2)  # Player 2 settlement at vertex 32
    
    if num_players >= 4:
        state.add_settlement(45, 3)  # Player 3 settlement at vertex 45
    
    # Add some roads
    state.add_road(3, 7, 0)      # Player 0 road
    state.add_road(15, 20, 1)    # Player 1 road
    
    save_game_state_json(state, filepath)


def ensure_artifacts_directory(base_path: str = "artifacts") -> Path:
    """
    Ensure the artifacts directory exists.
    
    Args:
        base_path: Base path for artifacts directory
    
    Returns:
        Path object for the artifacts directory
    """
    artifacts_dir = Path(base_path)
    artifacts_dir.mkdir(exist_ok=True)
    return artifacts_dir


def get_artifact_path(filename: str, base_path: str = "artifacts") -> str:
    """
    Get full path for an artifact file.
    
    Args:
        filename: Name of the artifact file
        base_path: Base path for artifacts directory
    
    Returns:
        Full path to the artifact file
    """
    artifacts_dir = ensure_artifacts_directory(base_path)
    return str(artifacts_dir / filename)


def save_analysis_summary(board: CatanBoard, vertex_manager, recommendations: List[RecommendationResult],
                         strategy: str, filepath: str) -> None:
    """
    Save a comprehensive analysis summary to JSON.
    
    Args:
        board: The Catan board
        vertex_manager: VertexManager instance
        recommendations: List of recommendations
        strategy: Strategy used for analysis
        filepath: Path to save the summary
    """
    summary = {
        'analysis_metadata': {
            'strategy': strategy,
            'timestamp': str(Path(__file__).stat().st_mtime),  # Simple timestamp
            'board_valid': board.validate_board(),
            'total_vertices': vertex_manager.get_vertex_count(),
            'total_recommendations': len(recommendations)
        },
        'board_summary': board.get_board_summary(),
        'top_recommendations': [rec.to_dict() for rec in recommendations[:10]],
        'vertex_statistics': {
            'total_vertices': len(vertex_manager.vertices),
            'boundary_vertices': len([v for v in vertex_manager.get_vertices_csv_data() if v['is_boundary']]),
            'interior_vertices': len([v for v in vertex_manager.get_vertices_csv_data() if not v['is_boundary']])
        }
    }
    
    with open(filepath, 'w') as f:
        json.dump(summary, f, indent=2)
