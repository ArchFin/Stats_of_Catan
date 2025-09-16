#!/usr/bin/env python3
"""
Build Board CLI - Create Catan Board and Generate Reference Artifacts
====================================================================

Command-line interface for creating a Catan board with tiles and number tokens,
then saving all artifacts and generating the reference image.
"""

import argparse
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from catan.board import CatanBoard
from catan.vertices import VertexManager
from catan.visualize import CatanVisualizer
from catan.io_utils import (
    save_board_json, save_vertices_csv, get_artifact_path, 
    ensure_artifacts_directory, create_example_state_file
)


def main():
    parser = argparse.ArgumentParser(
        description="Create Catan board and generate reference artifacts"
    )
    
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed for deterministic board generation"
    )
    
    parser.add_argument(
        "--layout", choices=["standard", "randomized"], default="standard",
        help="Board layout type (standard uses fixed layout, randomized shuffles tiles)"
    )
    
    parser.add_argument(
        "--output-dir", default="artifacts",
        help="Output directory for generated artifacts"
    )
    
    parser.add_argument(
        "--show-vertices", action="store_true", default=True,
        help="Show vertex labels on the reference image"
    )
    
    parser.add_argument(
        "--show-numbers", action="store_true", default=True,
        help="Show number tokens on the reference image"
    )
    
    args = parser.parse_args()
    
    print("🎲 Catan Board Builder")
    print("=" * 50)
    
    # Ensure artifacts directory exists
    artifacts_dir = ensure_artifacts_directory(args.output_dir)
    print(f"📁 Output directory: {artifacts_dir}")
    
    # Create board
    print(f"🏗️  Creating board (layout: {args.layout}, seed: {args.seed})...")
    board = CatanBoard(seed=args.seed)
    
    if args.layout == "randomized":
        board.create_standard_board(randomize=True)
    else:
        board.create_standard_board(randomize=False)
    
    # Validate board
    if board.validate_board():
        print("✅ Board validation passed")
    else:
        print("❌ Board validation failed!")
        return 1
    
    # Print board summary
    summary = board.get_board_summary()
    print(f"📊 Board summary:")
    print(f"   Total tiles: {summary['total_tiles']}")
    print(f"   Resource distribution: {summary['resource_distribution']}")
    print(f"   Number distribution: {summary['number_distribution']}")
    print(f"   Adjacent high numbers: {summary['adjacent_high_numbers']}")
    
    # Create vertex manager
    print("🔗 Discovering vertices...")
    vertex_manager = VertexManager(board)
    vertex_count = vertex_manager.get_vertex_count()
    print(f"   Found {vertex_count} vertices")
    
    # Save board data
    board_path = get_artifact_path("board.json", args.output_dir)
    save_board_json(board, board_path)
    print(f"💾 Board data saved: {board_path}")
    
    # Save vertex data
    vertices_path = get_artifact_path("vertices.csv", args.output_dir)
    save_vertices_csv(vertex_manager, vertices_path)
    print(f"💾 Vertex data saved: {vertices_path}")
    
    # Create example game state
    example_state_path = get_artifact_path("example_state.json", args.output_dir)
    create_example_state_file(example_state_path)
    print(f"💾 Example game state saved: {example_state_path}")
    
    # Generate reference visualization
    print("🎨 Generating board reference image...")
    visualizer = CatanVisualizer(board, vertex_manager)
    
    reference_path = get_artifact_path("board_reference.png", args.output_dir)
    visualizer.render_board(
        save_path=reference_path,
        show_vertices=args.show_vertices,
        show_numbers=args.show_numbers
    )
    print(f"🖼️  Board reference saved: {reference_path}")
    
    # Generate vertex reference table
    vertex_table_path = get_artifact_path("vertex_reference_table.png", args.output_dir)
    visualizer.create_vertex_reference_table(vertex_table_path)
    print(f"📋 Vertex reference table saved: {vertex_table_path}")
    
    print("\n🎉 Board generation complete!")
    print(f"📁 All artifacts saved to: {artifacts_dir}")
    print("\nGenerated files:")
    print(f"  • board.json - Board configuration")
    print(f"  • vertices.csv - Vertex positions and properties")
    print(f"  • board_reference.png - Visual board reference")
    print(f"  • vertex_reference_table.png - Vertex data table")
    print(f"  • example_state.json - Example game state")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
