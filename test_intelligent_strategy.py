#!/usr/bin/env python3
"""
Test Intelligent Strategy System
=================================

Test the intelligent strategy recommendation system with harbor fixes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.catan.board import CatanBoard
from src.catan.vertices import VertexManager
from src.catan.board_analyzer import BoardStrategyAnalyzer

def test_intelligent_strategy():
    """Test the intelligent strategy recommendation system."""
    print("🧪 TESTING INTELLIGENT STRATEGY SYSTEM")
    print("=" * 42)
    
    # Create a standard board
    print("📋 Creating standard board...")
    board = CatanBoard()
    board.create_standard_board()
    
    # Create vertex manager
    print("🔍 Setting up vertex manager...")
    vertex_manager = VertexManager(board)
    
    # Test harbor information
    print(f"⚓ Harbor count: {len(board.get_all_harbors())}")
    
    harbor_vertices = []
    for vertex_id in range(54):
        if board.is_harbor_vertex(vertex_id):
            harbor = board.get_harbor_at_vertex(vertex_id)
            harbor_vertices.append((vertex_id, harbor.type.value))
    
    print(f"🏴 Harbor vertices: {harbor_vertices}")
    
    # Test intelligent strategy
    print("\n🧠 Testing intelligent strategy analysis...")
    analyzer = BoardStrategyAnalyzer(board, vertex_manager)
    
    strategy, explanation, details = analyzer.recommend_strategy()
    
    print(f"🎯 RECOMMENDED STRATEGY: {strategy.upper().replace('_', ' ')}")
    print(f"📝 {explanation}")
    print()
    print("📊 Strategy Scores:")
    for strat, score in details['scores'].items():
        indicator = "👑" if strat == strategy else "  "
        print(f"   {indicator} {strat.replace('_', ' ').title()}: {score:.2f}")
    
    print("\n📋 Board Analysis Details:")
    if 'best_resource' in details:
        print(f"   🌾 Best resource quality: {details['best_resource']}")
    if 'number_diversity' in details:
        print(f"   🎲 Number diversity: {details['number_diversity']:.2f}")
    if 'harbor_access' in details:
        print(f"   ⚓ Harbor access: {details['harbor_access']:.2f}")
    
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_intelligent_strategy()
