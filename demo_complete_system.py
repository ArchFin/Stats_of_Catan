#!/usr/bin/env python3
"""
Demo: Complete Harbor + Strategy System
=======================================

Demonstration of the complete system with:
1. ✅ Corrected harbor positions (exactly matching user specs)
2. 🧠 Intelligent strategy recommendation (no manual selection)
3. 🎨 Enhanced harbor visualization
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.catan.board import CatanBoard
from src.catan.vertices import VertexManager
from src.catan.board_analyzer import BoardStrategyAnalyzer

def demo_complete_system():
    """Demo the complete harbor and strategy system."""
    print("🎮 COMPLETE HARBOR + STRATEGY SYSTEM DEMO")
    print("=" * 45)
    
    # Create standard board
    print("📋 Creating standard board...")
    board = CatanBoard()
    board.create_standard_board()
    
    # Show corrected harbor positions
    print("\n⚓ CORRECTED HARBOR POSITIONS")
    print("-" * 30)
    
    harbor_manager = board.harbors
    for harbor_id, harbor in harbor_manager.harbors.items():
        vertices_str = ", ".join(map(str, harbor.vertices))
        print(f"   {harbor.type.value} → vertices [{vertices_str}]")
    
    # Create vertex manager
    print(f"\n🔍 Setting up vertex analysis...")
    vertex_manager = VertexManager(board)
    print(f"   ✅ Discovered {len(vertex_manager.vertices)} vertices")
    
    # 🧠 INTELLIGENT STRATEGY RECOMMENDATION
    print("\n🧠 INTELLIGENT STRATEGY ANALYSIS")
    print("=" * 35)
    
    analyzer = BoardStrategyAnalyzer(board, vertex_manager)
    strategy, explanation, details = analyzer.recommend_strategy()
    
    print(f"🎯 RECOMMENDED STRATEGY: {strategy.upper().replace('_', ' ')}")
    print(f"📝 {explanation}")
    print()
    print("📊 Strategy Scores:")
    for strat, score in details['scores'].items():
        indicator = "👑" if strat == strategy else "  "
        print(f"   {indicator} {strat.replace('_', ' ').title()}: {score:.1f}")
    
    # Harbor analysis
    print(f"\n🏴 Harbor Analysis:")
    print(f"   ⚓ Total harbors: {len(board.get_all_harbors())}")
    
    harbor_vertices = []
    for vertex_id in range(54):
        if board.is_harbor_vertex(vertex_id):
            harbor = board.get_harbor_at_vertex(vertex_id)
            harbor_vertices.append((vertex_id, harbor.type.value))
    
    print(f"   🗺️  Harbor-accessible vertices: {len(harbor_vertices)}")
    
    # Resource analysis
    summary = board.get_board_summary()
    print(f"\n📊 Board Quality:")
    print(f"   🌾 Resources: {summary['resource_distribution']}")
    print(f"   🎲 Numbers: {summary['number_distribution']}")
    
    print("\n✅ SYSTEM FEATURES COMPLETED:")
    print("   🔧 Harbor positions corrected to user specifications")
    print("   🧠 Intelligent strategy recommendation (no manual selection)")
    print("   🎨 Enhanced harbor visualization (larger symbols, connections)")
    print("   📊 Comprehensive board analysis")
    
    print(f"\n🎊 Demo completed! Recommended strategy: {strategy.upper().replace('_', ' ')}")

if __name__ == "__main__":
    demo_complete_system()
