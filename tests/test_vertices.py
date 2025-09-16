"""
Test Vertex Discovery and Settlement Rules
==========================================

Tests for vertex enumeration, distance rule validation, and settlement placement.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from catan.board import CatanBoard
from catan.vertices import VertexManager
from catan.state import GameState


def test_vertex_discovery():
    """Test that vertex discovery finds the expected number of vertices."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    vertex_manager = VertexManager(board)
    vertex_count = vertex_manager.get_vertex_count()
    
    # For a radius-2 hex board, expect around 54 vertices
    # This is calculated from the geometric properties
    assert 50 <= vertex_count <= 60, f"Expected ~54 vertices, got {vertex_count}"
    print(f"✅ Vertex discovery: Found {vertex_count} vertices (expected ~54)")


def test_vertex_adjacency():
    """Test that vertex adjacency is built correctly."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    vertex_manager = VertexManager(board)
    
    # Check that all vertices have adjacency information
    for vertex_id in vertex_manager.vertices:
        adjacent = vertex_manager.adjacency[vertex_id]
        
        # Each vertex should have 1-3 adjacent vertices
        assert 1 <= len(adjacent) <= 3, f"Vertex {vertex_id} has {len(adjacent)} adjacent vertices"
        
        # Check bidirectional adjacency
        for adj_id in adjacent:
            assert vertex_id in vertex_manager.adjacency[adj_id], f"Adjacency not bidirectional: {vertex_id} -> {adj_id}"
    
    print("✅ Vertex adjacency: All vertices have valid adjacency")


def test_distance_rule_validation():
    """Test that distance rule is enforced correctly."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    vertex_manager = VertexManager(board)
    game_state = GameState()
    
    # Place a settlement
    vertex_id = 10
    game_state.add_settlement(vertex_id, 0)
    
    # Check that adjacent vertices are not legal
    adjacent_vertices = vertex_manager.adjacency[vertex_id]
    legal_vertices = vertex_manager.get_legal_vertices(game_state.occupied_vertices)
    
    for adj_id in adjacent_vertices:
        assert adj_id not in legal_vertices, f"Adjacent vertex {adj_id} should not be legal"
    
    print("✅ Distance rule: Adjacent vertices correctly blocked")


def test_settlement_placement():
    """Test settlement placement validation."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    vertex_manager = VertexManager(board)
    game_state = GameState()
    
    # Test valid placement
    vertex_id = 5
    assert vertex_manager.is_valid_placement(vertex_id, game_state.occupied_vertices), "Initial placement should be valid"
    
    # Place settlement
    game_state.add_settlement(vertex_id, 0)
    
    # Test that same vertex is now invalid
    assert not vertex_manager.is_valid_placement(vertex_id, game_state.occupied_vertices), "Occupied vertex should be invalid"
    
    # Test that adjacent vertices are invalid
    for adj_id in vertex_manager.adjacency[vertex_id]:
        assert not vertex_manager.is_valid_placement(adj_id, game_state.occupied_vertices), f"Adjacent vertex {adj_id} should be invalid"
    
    print("✅ Settlement placement: Validation works correctly")


def test_vertex_resource_calculation():
    """Test that vertex resource information is calculated correctly."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    vertex_manager = VertexManager(board)
    
    # Check a few vertices
    for vertex_id in list(vertex_manager.vertices.keys())[:5]:
        vertex_info = vertex_manager.get_vertex_info(vertex_id)
        
        assert vertex_info is not None, f"Vertex info should not be None for vertex {vertex_id}"
        assert 'resources' in vertex_info, "Vertex info should contain resources"
        assert 'total_probability' in vertex_info, "Vertex info should contain total probability"
        assert 'incident_hexes' in vertex_info, "Vertex info should contain incident hexes"
        
        # Probability should be non-negative
        assert vertex_info['total_probability'] >= 0, "Total probability should be non-negative"
    
    print("✅ Vertex resources: Information calculated correctly")


def test_vertex_hex_relationship():
    """Test that vertices are correctly associated with hexes."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    vertex_manager = VertexManager(board)
    
    # Each vertex should be associated with 1-3 hexes
    for vertex_id, vertex in vertex_manager.vertices.items():
        hex_count = len(vertex.incident_hexes)
        assert 1 <= hex_count <= 3, f"Vertex {vertex_id} should be incident to 1-3 hexes, got {hex_count}"
        
        # All incident hexes should exist on the board
        for hex_coord in vertex.incident_hexes:
            assert hex_coord in board.tiles, f"Incident hex {hex_coord} should exist on board"
    
    print("✅ Vertex-hex relationship: All associations valid")


def test_boundary_vs_interior_vertices():
    """Test identification of boundary vs interior vertices."""
    board = CatanBoard(seed=42)
    board.create_standard_board()
    
    vertex_manager = VertexManager(board)
    vertex_data = vertex_manager.get_vertices_csv_data()
    
    boundary_count = sum(1 for v in vertex_data if v['is_boundary'])
    interior_count = sum(1 for v in vertex_data if not v['is_boundary'])
    
    # Should have both boundary and interior vertices
    assert boundary_count > 0, "Should have some boundary vertices"
    assert interior_count > 0, "Should have some interior vertices"
    
    print(f"✅ Boundary classification: {boundary_count} boundary, {interior_count} interior vertices")


def run_all_tests():
    """Run all vertex tests."""
    print("🧪 Running Vertex Tests")
    print("=" * 30)
    
    test_vertex_discovery()
    test_vertex_adjacency()
    test_distance_rule_validation()
    test_settlement_placement()
    test_vertex_resource_calculation()
    test_vertex_hex_relationship()
    test_boundary_vs_interior_vertices()
    
    print("\n🎉 All vertex tests passed!")


if __name__ == "__main__":
    run_all_tests()
