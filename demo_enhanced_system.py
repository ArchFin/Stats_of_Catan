#!/usr/bin/env python3
"""
Enhanced Catan System Demo
=========================

Demonstrates the new interactive features including:
-    for vertex_id in test_vertices:
        is_legal = game_state.is_legal_settlement_placement(vertex_id, vertex_manager)
        occupied = game_state.is_vertex_occupied(vertex_id)
        
        status = "✅ LEGAL" if is_legal else "❌ ILLEGAL"
        reasons = []
        if occupied:
            reasons.append("occupied")
        elif not is_legal:
            reasons.append("too close to existing settlement") management with settlement legality
- Turn-order aware recommendations
- Player position analysis
- Strategic insights
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from catan.board import CatanBoard
from catan.vertices import VertexManager
from catan.state import GameState
from catan.recommendations import SettlementRecommender
from catan.visualize import CatanVisualizer


def main():
    print("🎯 Enhanced Catan Analysis System Demo")
    print("=" * 50)
    
    # Create a standard board
    print("📋 Creating standard Catan board...")
    board = CatanBoard()
    board.create_standard_board()
    vertex_manager = VertexManager(board)
    print(f"✅ Board created with {len(board.tiles)} tiles and {vertex_manager.get_vertex_count()} vertices")
    
    # Create a sample game state
    print("\n🎮 Setting up sample game state...")
    game_state = GameState()
    
    # Add players with string IDs
    game_state.add_player("alice")
    game_state.add_player("bob")
    game_state.add_player("charlie")
    
    print(f"✅ Game state created with {len(game_state.players)} players")
    print(f"   Turn order: {game_state.turn_order}")
    
    # For this demo, we'll manually add some settlements to test the system
    # (Note: in real use, you'd call place_settlement with validation)
    
    # Alice's settlements (early game, balanced strategy)
    game_state.players["alice"].settlements = [16, 25]
    
    # Bob's settlements (development focused)
    game_state.players["bob"].settlements = [42, 51]
    game_state.players["bob"].cities = [42]  # Upgraded settlement
    
    # Charlie's settlements (road building focus)
    game_state.players["charlie"].settlements = [7, 18]
    
    for player_id, player in game_state.players.items():
        print(f"   {player_id}: {len(player.settlements)} settlements, {len(player.cities)} cities")
    
    # Create recommendation system
    print("\n🔧 Setting up recommendation system...")
    recommender = SettlementRecommender(board, vertex_manager)
    print("✅ Recommendation system ready")
    
    # Analyze each player's position
    print("\n👥 Player Position Analysis")
    print("-" * 40)
    
    comparison = recommender.compare_players(game_state)
    for player_id, analysis in comparison["players"].items():
        print(f"\n{player_id.upper()}:")
        print(f"  Turn Position: #{analysis['turn_position']} ({analysis['turn_advantage']} player)")
        print(f"  Settlements: {analysis['settlements']}, Cities: {analysis['cities']}")
        print(f"  Total Production: {analysis['total_production']:.1f}")
        print(f"  Harbors: {analysis['harbor_count']}")
        print(f"  Recommended Strategy: {analysis['recommended_strategy']}")
    
    print(f"\nLeaders:")
    for category, leader in comparison["leaders"].items():
        print(f"  {category.replace('_', ' ').title()}: {leader}")
    
    # Generate recommendations for each player
    print("\n🎯 Settlement Recommendations")
    print("-" * 40)
    
    for player_id in game_state.players.keys():
        print(f"\n{player_id.upper()} - Next Settlement Recommendations:")
        recommendations = recommender.recommend_best_settlements(
            game_state, player_id, top_k=3
        )
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                # Get some context about this vertex
                vertex_info = vertex_manager.get_vertex_info(rec.vertex_id)
                harbor = board.get_harbor_at_vertex(rec.vertex_id)
                harbor_text = f" (Harbor: {harbor.type.value})" if harbor else ""
                
                print(f"  #{i} Vertex {rec.vertex_id}: Score {rec.total_score:.1f}{harbor_text}")
                print(f"      Production: {rec.production_score:.1f}, "
                      f"Balance: {rec.balance_score:.1f}, "
                      f"Harbor: {rec.harbor_score:.1f}")
        else:
            print("  No legal settlement locations available!")
    
    # Demonstrate strategy comparison
    print("\n📊 Strategy Comparison Example")
    print("-" * 40)
    
    # Pick a good vertex to analyze
    test_vertex = 30  # This should be a decent spot
    if game_state.is_legal_settlement_placement(test_vertex, vertex_manager):
        print(f"Analyzing vertex {test_vertex} for Alice across different strategies:")
        
        for strategy in ['balanced', 'road_focused', 'dev_focused', 'city_focused']:
            score_breakdown = recommender.scorer.score_vertex(
                test_vertex, game_state, "alice", strategy
            )
            print(f"  {strategy:15}: {score_breakdown.total_score:5.1f} "
                  f"(Prod: {score_breakdown.production_score:.1f}, "
                  f"Harbor: {score_breakdown.harbor_score:.1f})")
    
    # Demonstrate settlement legality checking
    print("\n⚖️  Settlement Legality Demonstration")
    print("-" * 40)
    
    # Check vertices near existing settlements
    test_vertices = [15, 17, 24, 26]  # Should be near Alice's settlement at 16
    print("Testing vertices near Alice's settlement at vertex 16:")
    
    for vertex_id in test_vertices:
        is_legal = game_state.is_settlement_legal(vertex_id)
        distance_ok = game_state._check_distance_rule(vertex_id)
        occupied = vertex_id in game_state.get_all_occupied_vertices()
        
        status = "✅ LEGAL" if is_legal else "❌ ILLEGAL"
        reasons = []
        if occupied:
            reasons.append("occupied")
        if not distance_ok:
            reasons.append("too close")
        
        reason_text = f" ({', '.join(reasons)})" if reasons else ""
        print(f"  Vertex {vertex_id}: {status}{reason_text}")
    
    # Generate a full report for one player
    print("\n📋 Detailed Player Report")
    print("-" * 40)
    
    report = recommender.generate_recommendation_report(game_state, "alice", top_k=3)
    print(report)
    
    print("\n✅ Demo completed! The system now supports:")
    print("   • Interactive game state input via JSON")
    print("   • Settlement legality validation (distance rules)")
    print("   • Turn-order aware scoring adjustments")
    print("   • Multi-player position analysis")
    print("   • Strategy-specific recommendations")
    print("   • Comprehensive player reports")


if __name__ == "__main__":
    main()
