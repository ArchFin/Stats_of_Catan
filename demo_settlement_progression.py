#!/usr/bin/env python3
"""
Demo: Settlement Progression System
==================================

Test the enhanced settlement tracking capabilities with 1st vs 2nd settlement recommendations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from catan import (
    CatanBoard, VertexManager, SettlementScorer, 
    SettlementRecommender, GameState
)


def demo_settlement_progression():
    """Demonstrate the enhanced settlement tracking system."""
    print("🏆 SETTLEMENT PROGRESSION DEMO")
    print("=" * 50)
    print("Showcasing intelligent settlement tracking!")
    print()
    
    # Create a standard board
    board = CatanBoard(seed=42)
    board.create_standard_board(randomize=False)
    
    vertex_manager = VertexManager(board)
    scorer = SettlementScorer(board, vertex_manager)
    recommender = SettlementRecommender(board, vertex_manager, scorer)
    
    # Initialize game state
    game_state = GameState()
    
    print("🥇 FIRST SETTLEMENT RECOMMENDATIONS:")
    print("-" * 40)
    
    # Get recommendations for first settlement
    first_recs = recommender.recommend_settlements(
        game_state, strategy='balanced', player_id=0, top_k=3, settlement_number=1
    )
    
    for i, rec in enumerate(first_recs, 1):
        print(f"#{i} | Vertex {rec.vertex_id:2d} | Score: {rec.score:5.1f}")
        print(f"    {rec.justification}")
        print()
    
    # Place the first settlement
    if first_recs:
        chosen_vertex = first_recs[0].vertex_id
        game_state.place_settlement_enhanced(0, chosen_vertex)
        print(f"✅ Placed first settlement at vertex {chosen_vertex}")
        print()
    
    print("🥈 SECOND SETTLEMENT RECOMMENDATIONS:")
    print("-" * 40)
    print("Notice how synergy with the first settlement affects recommendations!")
    print()
    
    # Get recommendations for second settlement (with synergy)
    second_recs = recommender.recommend_settlements(
        game_state, strategy='balanced', player_id=0, top_k=3, settlement_number=2
    )
    
    for i, rec in enumerate(second_recs, 1):
        print(f"#{i} | Vertex {rec.vertex_id:2d} | Score: {rec.score:5.1f}")
        print(f"    {rec.justification}")
        print()
    
    # Show game state info
    print("📊 GAME STATE SUMMARY:")
    print("-" * 30)
    phase_info = game_state.get_settlement_phase_info(0)
    print(f"Player 0 settlements: {phase_info['settlement_count']}")
    print(f"Settlement locations: {phase_info['existing_settlements']}")
    print(f"Current phase: {phase_info['phase']}")
    print(f"Next settlement would be #{phase_info['next_settlement_number']}")
    print()
    
    print("🎯 DEMO COMPLETE!")
    print("The system now intelligently considers:")
    print("  • Settlement placement order (1st, 2nd, 3rd, etc.)")
    print("  • Synergy between existing settlements") 
    print("  • Resource diversification vs. concentration")
    print("  • Player-specific settlement tracking")
    print("  • Phase-aware recommendations")


if __name__ == "__main__":
    demo_settlement_progression()
