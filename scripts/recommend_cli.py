#!/usr/bin/env python3
"""
Settlement Recommendation CLI
============================

Command-line interface for computing and plotting optimal settlement placements.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from catan.board import CatanBoard
from catan.vertices import VertexManager
from catan.state import GameState
from catan.scoring import SettlementScorer
from catan.recommendations import SettlementRecommender
from catan.visualize import CatanVisualizer
from catan.io_utils import (
    load_board_json, load_game_state_json, save_recommendations_json,
    save_recommendations_csv, get_artifact_path, save_analysis_summary
)


def parse_weights(weights_str: str) -> dict:
    """Parse weights string into dictionary."""
    try:
        return json.loads(weights_str)
    except json.JSONDecodeError:
        print(f"❌ Invalid weights format: {weights_str}")
        print("   Example: '{\"production\":1.0,\"balance\":0.4,\"road\":0.5}'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate optimal settlement recommendations for Catan"
    )
    
    parser.add_argument(
        "--board", default="artifacts/board.json",
        help="Path to board configuration JSON file"
    )
    
    parser.add_argument(
        "--state", default="artifacts/example_state.json",
        help="Path to game state JSON file"
    )
    
    parser.add_argument(
        "--strategy", choices=["balanced", "road_focused", "dev_focused", "city_focused"],
        default="balanced",
        help="Settlement strategy to use"
    )
    
    parser.add_argument(
        "--weights", type=str, default=None,
        help='Custom weights as JSON string, e.g., \'{"production":1.0,"balance":0.4}\''
    )
    
    parser.add_argument(
        "--top-k", type=int, default=10,
        help="Number of top recommendations to generate"
    )
    
    parser.add_argument(
        "--player-id", type=str, default="player1",
        help="Player ID for recommendations"
    )
    
    parser.add_argument(
        "--analyze-player", type=str, default=None,
        help="Analyze a specific player's position and generate report"
    )
    
    parser.add_argument(
        "--compare-players", action="store_true",
        help="Compare all players' positions"
    )
    
    parser.add_argument(
        "--output-dir", default="artifacts",
        help="Output directory for recommendations"
    )
    
    parser.add_argument(
        "--analyze-vertex", type=int, default=None,
        help="Analyze a specific vertex ID across all strategies"
    )
    
    parser.add_argument(
        "--no-visualization", action="store_true",
        help="Skip generating visualization images"
    )
    
    args = parser.parse_args()
    
    print("🎯 Catan Settlement Recommender")
    print("=" * 50)
    
    # Load board
    print(f"📋 Loading board from: {args.board}")
    try:
        board = load_board_json(args.board)
        print(f"✅ Board loaded successfully ({len(board.tiles)} tiles)")
    except FileNotFoundError:
        print(f"❌ Board file not found: {args.board}")
        print("   Run 'python scripts/build_board.py' first to create a board")
        return 1
    except Exception as e:
        print(f"❌ Error loading board: {e}")
        return 1
    
    # Load game state
    print(f"🎮 Loading game state from: {args.state}")
    try:
        game_state = load_game_state_json(args.state)
        print(f"✅ Game state loaded ({len(game_state.occupied_vertices)} occupied vertices)")
    except FileNotFoundError:
        print(f"❌ Game state file not found: {args.state}")
        print("   Using empty game state")
        game_state = GameState()
    except Exception as e:
        print(f"❌ Error loading game state: {e}")
        return 1
    
    # Create analysis components
    print("🔧 Setting up analysis components...")
    vertex_manager = VertexManager(board)
    recommender = SettlementRecommender(board, vertex_manager)
    
    # Apply custom weights if provided
    if args.weights:
        custom_weights = parse_weights(args.weights)
        recommender.scorer.set_weights(custom_weights)
        print(f"⚖️  Applied custom weights: {custom_weights}")
    
    print(f"📊 Analysis ready ({vertex_manager.get_vertex_count()} total vertices)")
    
    # Handle player comparison
    if args.compare_players:
        print(f"\n👥 Comparing all players...")
        comparison = recommender.compare_players(game_state)
        
        print("\nPlayer Comparison:")
        print("-" * 60)
        for player_id, analysis in comparison["players"].items():
            print(f"Player {player_id}:")
            print(f"  Settlements: {analysis['settlements']}, Cities: {analysis['cities']}")
            print(f"  Production: {analysis['total_production']}")
            print(f"  Turn Position: {analysis['turn_position']} ({analysis['turn_advantage']})")
            print()
        
        print("Leaders:")
        for category, leader in comparison["leaders"].items():
            print(f"  {category}: {leader}")
        
        return 0
    
    # Handle player-specific analysis
    if args.analyze_player:
        print(f"\n👤 Analyzing player {args.analyze_player}...")
        report = recommender.generate_recommendation_report(game_state, args.analyze_player)
        print(report)
        
        # Save report
        report_path = get_artifact_path(f"player_{args.analyze_player}_report.txt", args.output_dir)
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved: {report_path}")
        
        return 0
    
    # Handle vertex-specific analysis
    if args.analyze_vertex is not None:
        print(f"\n🔍 Analyzing vertex {args.analyze_vertex} across all strategies...")
        
        if args.analyze_vertex not in vertex_manager.vertices:
            print(f"❌ Vertex {args.analyze_vertex} does not exist")
            return 1
        
        # Check if vertex is legal for settlement
        if not game_state.is_legal_settlement_placement(args.analyze_vertex, vertex_manager):
            print(f"❌ Vertex {args.analyze_vertex} is not legal for settlement placement")
            if game_state.is_vertex_occupied(args.analyze_vertex):
                print(f"   Vertex is already occupied")
            else:
                adjacent_settlements = []
                for settlement_vertex in game_state.occupied_vertices:
                    if settlement_vertex in vertex_manager.adjacency.get(args.analyze_vertex, set()):
                        adjacent_settlements.append(settlement_vertex)
                if adjacent_settlements:
                    print(f"   Adjacent to settlements at: {adjacent_settlements}")
            return 1
        
        # Compare strategies for this vertex
        strategy_results = {}
        for strategy in ['balanced', 'road_focused', 'dev_focused', 'city_focused']:
            score_breakdown = recommender.scorer.score_vertex(
                args.analyze_vertex, game_state, args.player_id, strategy
            )
            strategy_results[strategy] = score_breakdown
        
        # Print comparison results
        print(f"\nStrategy Comparison for Vertex {args.analyze_vertex}:")
        print("-" * 60)
        for strategy, breakdown in strategy_results.items():
            print(f"{strategy:15} | Score: {breakdown.total_score:6.1f} | "
                  f"Prod: {breakdown.production_score:.1f} | "
                  f"Harbor: {breakdown.harbor_score:.1f}")
        
        return 0
    
    # Generate recommendations
    print(f"\n🎯 Generating top-{args.top_k} recommendations for {args.player_id} ({args.strategy} strategy)...")
    recommendations = recommender.recommend_best_settlements(
        game_state=game_state,
        player_id=args.player_id,
        strategy=args.strategy,
        top_k=args.top_k
    )
    
    if not recommendations:
        print("❌ No valid recommendations found")
        return 1
    
    print(f"✅ Generated {len(recommendations)} recommendations")
    
    # Print top recommendations
    print(f"\n🏆 Top {min(5, len(recommendations))} Recommendations ({args.strategy}):")
    print("-" * 80)
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"#{i:2} | Vertex {rec.vertex_id:2} | Score: {rec.total_score:5.1f} | "
              f"Prod: {rec.production_score:.1f} | Bal: {rec.balance_score:.1f} | "
              f"Harbor: {rec.harbor_score:.1f}")
    
    # Save recommendations
    print(f"\n💾 Saving recommendations...")
    
    # JSON export
    json_path = get_artifact_path("recommendations.json", args.output_dir)
    save_recommendations_json(recommendations, json_path, {
        'strategy': args.strategy,
        'player_id': args.player_id,
        'top_k': args.top_k,
        'board_file': args.board,
        'state_file': args.state
    })
    print(f"   📄 JSON: {json_path}")
    
    # CSV export
    csv_path = get_artifact_path("recommendations.csv", args.output_dir)
    save_recommendations_csv(recommendations, csv_path)
    print(f"   📊 CSV: {csv_path}")
    
    # Analysis summary
    summary_path = get_artifact_path("analysis_summary.json", args.output_dir)
    save_analysis_summary(board, vertex_manager, recommendations, args.strategy, summary_path)
    print(f"   📋 Summary: {summary_path}")
    
    # Generate visualizations
    if not args.no_visualization:
        print(f"\n🎨 Generating visualizations...")
        visualizer = CatanVisualizer(board, vertex_manager)
        
        # Recommendations visualization
        viz_path = get_artifact_path("optimal_placements.png", args.output_dir)
        visualizer.render_recommendations(recommendations, game_state, viz_path, show_top_k=min(5, len(recommendations)))
        print(f"   🖼️  Optimal placements: {viz_path}")
    
    # Generate text report
    report = recommender.get_summary_report(recommendations, args.strategy)
    report_path = get_artifact_path("recommendations_report.txt", args.output_dir)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"   📝 Text report: {report_path}")
    
    print(f"\n🎉 Analysis complete!")
    print(f"📁 All outputs saved to: {args.output_dir}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
