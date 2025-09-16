#!/usr/bin/env python3
"""
Test Harbor Implementation
=========================

Quick test to verify harbor system is working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from catan import CatanBoard, VertexManager, CatanVisualizer, SettlementScorer, GameState
from catan.harbors import HarborType

def test_harbors():
    """Test harbor functionality."""
    print("🧪 Testing Harbor Implementation")
    print("=" * 50)
    
    # Create board with harbors
    board = CatanBoard(seed=42)
    board.create_standard_board(randomize=False)
    
    # Test harbor manager
    harbors = board.get_all_harbors()
    print(f"✅ Found {len(harbors)} harbors")
    
    # Print harbor details
    for harbor_id, harbor in harbors.items():
        print(f"   Harbor {harbor_id}: {harbor.type.value} at vertices {harbor.vertices}")
    
    # Test harbor access
    harbor_vertices = []
    for vertex_id in range(54):  # Test first few vertices
        if board.is_harbor_vertex(vertex_id):
            harbor = board.get_harbor_at_vertex(vertex_id)
            harbor_vertices.append(vertex_id)
            print(f"   Vertex {vertex_id}: {harbor.type.value} harbor")
    
    print(f"✅ Found {len(harbor_vertices)} harbor-accessible vertices")
    
    # Test scoring with harbors
    vertex_manager = VertexManager(board)
    scorer = SettlementScorer(board, vertex_manager)
    
    # Test harbor scoring
    game_state = GameState()
    
    if harbor_vertices:
        test_vertex = harbor_vertices[0]
        score = scorer.score_vertex(test_vertex, game_state, 'balanced')
        print(f"✅ Harbor vertex {test_vertex} scored: {score.total_score:.1f} (harbor: {score.harbor_score:.1f})")
    
    # Test visualization with harbors
    visualizer = CatanVisualizer(board, vertex_manager)
    output_path = "test_harbors_board.png"
    visualizer.render_board(output_path, show_harbors=True)
    print(f"✅ Saved harbor visualization to {output_path}")
    
    print("\n🎉 All harbor tests passed!")

if __name__ == "__main__":
    test_harbors()
