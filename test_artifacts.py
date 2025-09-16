#!/usr/bin/env python3
"""
Test Artifacts Generation
========================

Test if the artifacts generation is now working after the fix.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from catan import CatanBoard, VertexManager, SettlementRecommender, SettlementScorer, GameState

def test_artifacts():
    """Test artifact generation after the fix."""
    print("🧪 Testing artifact generation after fix...")
    
    # Create a standard board
    board = CatanBoard()
    board.create_standard_board()
    
    # Create vertex manager
    vertex_manager = VertexManager(board)
    
    # Create empty game state
    game_state = GameState()
    
    # Create scorer and recommender
    scorer = SettlementScorer(board, vertex_manager)
    recommender = SettlementRecommender(board, vertex_manager, scorer)
    
    # Test getting recommendations (this was failing before)
    print("🎯 Getting recommendations...")
    recommendations = recommender.recommend_settlements(game_state, strategy="balanced", top_k=5)
    
    print(f"✅ Successfully got {len(recommendations)} recommendations!")
    
    # Print top 3 recommendations
    for i, rec in enumerate(recommendations[:3]):
        print(f"   {i+1}. Vertex {rec.vertex_id}: Score {rec.score:.2f}")
    
    print("🎉 Test passed! Artifact generation should now work.")

if __name__ == "__main__":
    test_artifacts()
