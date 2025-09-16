"""
Test Catan Board Generation and Validation
==========================================

Tests for board creation, tile distribution, and number token placement.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from catan.board import CatanBoard, ResourceType
from catan.hex_coords import generate_radius_2_board


def test_radius_2_board_generation():
    """Test that radius-2 board has exactly 19 hexes."""
    hexes = generate_radius_2_board()
    assert len(hexes) == 19, f"Expected 19 hexes, got {len(hexes)}"
    print("✅ Radius-2 board generation: 19 hexes")


def test_tile_distribution():
    """Test that board has correct tile type distribution."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    # Count resources
    resource_counts = {}
    for tile in board.tiles.values():
        resource_counts[tile.resource] = resource_counts.get(tile.resource, 0) + 1
    
    expected = {
        ResourceType.WOOD: 4,
        ResourceType.BRICK: 3,
        ResourceType.SHEEP: 4,
        ResourceType.WHEAT: 4,
        ResourceType.ORE: 3,
        ResourceType.DESERT: 1
    }
    
    assert resource_counts == expected, f"Resource distribution mismatch: {resource_counts} != {expected}"
    print("✅ Tile distribution: Correct resource counts")


def test_number_token_distribution():
    """Test that number tokens follow official distribution."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    # Count numbers (excluding desert)
    number_counts = {}
    desert_count = 0
    
    for tile in board.tiles.values():
        if tile.number == 0:
            desert_count += 1
        else:
            number_counts[tile.number] = number_counts.get(tile.number, 0) + 1
    
    expected_numbers = {
        2: 1, 3: 2, 4: 2, 5: 2, 6: 2,
        8: 2, 9: 2, 10: 2, 11: 2, 12: 1
    }
    
    assert number_counts == expected_numbers, f"Number distribution mismatch: {number_counts} != {expected_numbers}"
    assert desert_count == 1, f"Expected 1 desert, got {desert_count}"
    print("✅ Number tokens: Correct distribution")


def test_desert_has_no_number():
    """Test that desert tile has no number token."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    for tile in board.tiles.values():
        if tile.resource == ResourceType.DESERT:
            assert tile.number == 0, f"Desert should have number 0, got {tile.number}"
    
    print("✅ Desert validation: No number token")


def test_board_validation():
    """Test that board validation works correctly."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    assert board.validate_board(), "Board should be valid"
    print("✅ Board validation: Passes all checks")


def test_deterministic_generation():
    """Test that same seed produces same board."""
    board1 = CatanBoard(seed=123)
    board1.create_standard_board()
    
    board2 = CatanBoard(seed=123)
    board2.create_standard_board()
    
    # Compare tile configurations
    for coord in board1.hexes:
        tile1 = board1.tiles[coord]
        tile2 = board2.tiles[coord]
        
        assert tile1.resource == tile2.resource, f"Resource mismatch at {coord}"
        assert tile1.number == tile2.number, f"Number mismatch at {coord}"
    
    print("✅ Deterministic generation: Same seed produces identical boards")


def test_randomized_generation():
    """Test that different seeds produce different boards."""
    board1 = CatanBoard(seed=111)
    board1.create_standard_board(randomize=True)
    
    board2 = CatanBoard(seed=222)
    board2.create_standard_board(randomize=True)
    
    # Boards should be different (very high probability)
    tiles1 = [(tile.resource, tile.number) for tile in board1.tiles.values()]
    tiles2 = [(tile.resource, tile.number) for tile in board2.tiles.values()]
    
    assert tiles1 != tiles2, "Different seeds should produce different boards"
    print("✅ Randomized generation: Different seeds produce different boards")


def run_all_tests():
    """Run all board tests."""
    print("🧪 Running Board Tests")
    print("=" * 30)
    
    test_radius_2_board_generation()
    test_tile_distribution()
    test_number_token_distribution()
    test_desert_has_no_number()
    test_board_validation()
    test_deterministic_generation()
    test_randomized_generation()
    
    print("\n🎉 All board tests passed!")


if __name__ == "__main__":
    run_all_tests()
