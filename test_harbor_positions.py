#!/usr/bin/env python3
"""
Test Harbor Positions
=====================

Test the corrected harbor positioning system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.catan.board import CatanBoard

def test_harbor_positions():
    """Test the corrected harbor positions."""
    print("🏴 TESTING HARBOR POSITIONS")
    print("=" * 30)
    
    # Create a standard board
    print("📋 Creating standard board...")
    board = CatanBoard()
    board.create_standard_board()
    
    # Get all harbors and their vertices
    harbors = board.get_all_harbors()
    print(f"⚓ Total harbors: {len(harbors)}")
    print()
    
    # Show harbor configuration
    print("🗺️  HARBOR CONFIGURATION:")
    print("-" * 25)
    
    # Show each harbor and its vertices
    harbor_manager = board.harbors
    for harbor_id, harbor in harbor_manager.harbors.items():
        vertices_str = ", ".join(map(str, harbor.vertices))
        print(f"Harbor {harbor_id}: {harbor.type.value} at vertices [{vertices_str}]")
        
    print()
    print("🔍 USER SPECIFIED POSITIONS:")
    print("(HarborType.BRICK, [39, 52])")
    print("(HarborType.WOOD, [41, 36])")
    print("(HarborType.SHEEP, [50, 29])")
    print("(HarborType.WHEAT, [48, 27])")
    print("(HarborType.ORE, [46, 25])")
    print("(HarborType.GENERIC, [44, 13])")
    print("(HarborType.GENERIC, [42, 11])")
    print("(HarborType.GENERIC, [30, 17])")
    print("(HarborType.GENERIC, [32, 19])")
    
    print()
    print("✅ Harbor test completed!")

if __name__ == "__main__":
    test_harbor_positions()
