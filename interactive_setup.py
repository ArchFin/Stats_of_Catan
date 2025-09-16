#!/usr/bin/env python3
"""
Interactive Catan Board Setup
============================

User-friendly interface for creating custom Catan boards with tile placement,
settlement analysis, and recommendation generation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from catan import (
    CatanBoard, VertexManager, CatanVisualizer, 
    SettlementRecommender, SettlementScorer, GameState, ResourceType
)

# Tile layout mapping for intuitive input
# Maps user-friendly position numbers to hex coordinates
TILE_LAYOUT_MAP = {
    # Row 1 (top): 3 tiles
    0: (0, -2),   # Top-left
    1: (1, -2),   # Top-center  
    2: (2, -2),   # Top-right
    
    # Row 2: 4 tiles
    3: (-1, -1),  # Left
    4: (0, -1),   # Center-left
    5: (1, -1),   # Center-right
    6: (2, -1),   # Right
    
    # Row 3 (middle): 5 tiles  
    7: (-2, 0),   # Far left
    8: (-1, 0),   # Left
    9: (0, 0),    # Center (often desert)
    10: (1, 0),   # Right
    11: (2, 0),   # Far right
    
    # Row 4: 4 tiles
    12: (-2, 1),  # Left
    13: (-1, 1),  # Center-left
    14: (0, 1),   # Center-right
    15: (1, 1),   # Right
    
    # Row 5 (bottom): 3 tiles
    16: (-2, 2),  # Bottom-left
    17: (-1, 2),  # Bottom-center
    18: (0, 2),   # Bottom-right
}

# Reverse mapping for display
COORD_TO_POSITION = {v: k for k, v in TILE_LAYOUT_MAP.items()}

# Standard resource distributions
STANDARD_RESOURCES = {
    ResourceType.WOOD: 4,
    ResourceType.BRICK: 3, 
    ResourceType.SHEEP: 4,
    ResourceType.WHEAT: 4,
    ResourceType.ORE: 3,
    ResourceType.DESERT: 1
}

STANDARD_NUMBERS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

@dataclass
class TileSetup:
    """Configuration for a single tile."""
    position: int  # 0-18 user position
    resource: ResourceType
    number: int
    coord: Tuple[int, int]  # (q, r) hex coordinate


class InteractiveCatanSetup:
    """Interactive setup system for Catan boards."""
    
    def __init__(self):
        """Initialize the setup system."""
        self.tiles: Dict[int, TileSetup] = {}
        self.board: Optional[CatanBoard] = None
        self.vertex_manager: Optional[VertexManager] = None
        
    def print_banner(self):
        """Print welcome banner."""
        print("🏰" + "="*70 + "🏰")
        print("🎯           INTERACTIVE CATAN BOARD SETUP SYSTEM           🎯")
        print("🏰" + "="*70 + "🏰")
        print()
        print("Create custom Catan boards with intuitive tile placement!")
        print("• Set up tiles in logical order (0-18)")
        print("• Get optimal settlement recommendations") 
        print("• Generate beautiful board visualizations")
        print("• Export data for analysis")
        print()
    
    def show_board_layout(self):
        """Show the tile layout positions for user reference."""
        print("📍 TILE LAYOUT POSITIONS:")
        print("=" * 30)
        print()
        print("     [0] [1] [2]")
        print("   [3] [4] [5] [6]") 
        print(" [7] [8] [9] [10] [11]")
        print("   [12] [13] [14] [15]")
        print("     [16] [17] [18]")
        print()
        print("💡 Enter tiles in this order for intuitive setup!")
        print()
    
    def show_harbor_layout(self):
        """Show harbor positions for reference."""
        print("⚓ HARBOR LAYOUT:")
        print("=" * 25)
        print()
        print("Harbors are automatically placed at these positions:")
        print("• Brick 2:1    - Top-right edge")
        print("• Wood 2:1     - Right edge") 
        print("• Generic 3:1  - Bottom-right edge")
        print("• Wheat 2:1    - Bottom edge")
        print("• Ore 2:1      - Bottom-left edge")
        print("• Generic 3:1  - Left edge")
        print("• Sheep 2:1    - Top-left edge")
        print("• Generic 3:1  - Top edge")
        print("• Generic 3:1  - Top-right secondary")
        print()
    
    def get_resource_input(self, position: int) -> ResourceType:
        """Get resource type from user input."""
        resources = {
            'w': ResourceType.WOOD,
            'wood': ResourceType.WOOD,
            'b': ResourceType.BRICK, 
            'brick': ResourceType.BRICK,
            's': ResourceType.SHEEP,
            'sheep': ResourceType.SHEEP,
            'wh': ResourceType.WHEAT,
            'wheat': ResourceType.WHEAT,
            'o': ResourceType.ORE,
            'ore': ResourceType.ORE,
            'd': ResourceType.DESERT,
            'desert': ResourceType.DESERT
        }
        
        while True:
            print(f"🏔️  Tile [{position}] - Enter resource type:")
            print("   W/Wood, B/Brick, S/Sheep, WH/Wheat, O/Ore, D/Desert")
            
            resource_input = input("   Resource: ").lower().strip()
            
            if resource_input in resources:
                return resources[resource_input]
            else:
                print("   ❌ Invalid resource. Try: w, b, s, wh, o, d")
                print()
    
    def get_number_input(self, position: int, resource: ResourceType) -> int:
        """Get number token from user input."""
        if resource == ResourceType.DESERT:
            return 0
            
        while True:
            print(f"🎲 Tile [{position}] - Enter number token (2-12, no 7):")
            
            try:
                number = int(input("   Number: ").strip())
                if 2 <= number <= 12 and number != 7:
                    return number
                else:
                    print("   ❌ Invalid number. Use 2-6 or 8-12 (no 7)")
                    print()
            except ValueError:
                print("   ❌ Please enter a valid number")
                print()
    
    def validate_setup(self) -> Tuple[bool, List[str]]:
        """Validate the tile setup meets Catan rules."""
        errors = []
        
        # Count resources
        resource_counts = {}
        number_counts = {}
        
        for tile in self.tiles.values():
            resource_counts[tile.resource] = resource_counts.get(tile.resource, 0) + 1
            if tile.number > 0:
                number_counts[tile.number] = number_counts.get(tile.number, 0) + 1
        
        # Check resource distribution
        for resource, expected in STANDARD_RESOURCES.items():
            actual = resource_counts.get(resource, 0)
            if actual != expected:
                errors.append(f"❌ {resource.value}: expected {expected}, got {actual}")
        
        # Check number distribution
        for number in STANDARD_NUMBERS:
            expected = STANDARD_NUMBERS.count(number)
            actual = number_counts.get(number, 0)
            if actual != expected:
                errors.append(f"❌ Number {number}: expected {expected}, got {actual}")
        
        return len(errors) == 0, errors
    
    def interactive_setup(self):
        """Run interactive tile setup."""
        print("🎯 INTERACTIVE TILE SETUP")
        print("=" * 30)
        print()
        
        # Show expected distributions
        print("📊 Standard Catan Distribution:")
        for resource, count in STANDARD_RESOURCES.items():
            print(f"   {resource.value.capitalize()}: {count}")
        print(f"   Numbers: {len(STANDARD_NUMBERS)} tokens (2-12, no 7)")
        print()
        
        # Set up each tile
        for position in range(19):
            print(f"🔷 Setting up tile {position + 1}/19")
            print("-" * 25)
            
            resource = self.get_resource_input(position)
            number = self.get_number_input(position, resource)
            coord = TILE_LAYOUT_MAP[position]
            
            self.tiles[position] = TileSetup(
                position=position,
                resource=resource, 
                number=number,
                coord=coord
            )
            
            print(f"   ✅ Tile [{position}]: {resource.value} {number if number > 0 else ''}")
            print()
        
        # Validate setup
        is_valid, errors = self.validate_setup()
        
        if is_valid:
            print("✅ SETUP VALID! All tiles configured correctly.")
        else:
            print("⚠️  SETUP WARNINGS:")
            for error in errors:
                print(f"   {error}")
            print()
            proceed = input("Continue anyway? (y/n): ").lower().strip()
            if proceed != 'y':
                print("❌ Setup cancelled.")
                return False
        
        return True
    
    def use_preset_board(self, preset_name: str = "standard"):
        """Use a preset board configuration."""
        print(f"🎲 Using preset board: {preset_name}")
        
        if preset_name == "standard":
            # Create standard randomized board
            self.board = CatanBoard(seed=42)
            self.board.create_standard_board(randomize=True)
            
            # Map board tiles to our layout
            for position, coord_tuple in TILE_LAYOUT_MAP.items():
                from catan.hex_coords import HexCoord
                coord = HexCoord(coord_tuple[0], coord_tuple[1])
                
                if coord in self.board.tiles:
                    tile = self.board.tiles[coord]
                    self.tiles[position] = TileSetup(
                        position=position,
                        resource=tile.resource,
                        number=tile.number,
                        coord=coord_tuple
                    )
            
            print("✅ Standard board loaded successfully!")
            return True
        
        return False
    
    def create_board_from_setup(self):
        """Create CatanBoard from user setup."""
        from catan.hex_coords import HexCoord
        
        self.board = CatanBoard()
        
        # Clear existing tiles
        self.board.tiles.clear()
        
        # Add user-configured tiles
        for tile_setup in self.tiles.values():
            coord = HexCoord(tile_setup.coord[0], tile_setup.coord[1])
            
            from catan.board import Tile
            tile = Tile(
                coord=coord,
                resource=tile_setup.resource,
                number=tile_setup.number,
                has_robber=(tile_setup.resource == ResourceType.DESERT)
            )
            
            self.board.tiles[coord] = tile
            
            # Set robber position on desert
            if tile_setup.resource == ResourceType.DESERT:
                self.board.robber_position = coord
        
        print("✅ Board created from your setup!")
        
    def analyze_board(self):
        """Perform settlement analysis with intelligent strategy recommendation."""
        if not self.board:
            print("❌ No board available for analysis")
            return
            
        print("🔍 ANALYZING BOARD...")
        print("=" * 25)
        
        # Create vertex manager
        self.vertex_manager = VertexManager(self.board)
        print(f"✅ Discovered {len(self.vertex_manager.vertices)} vertices")
        
        # Validate board
        is_valid = self.board.validate_board()
        print(f"✅ Board validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Show harbor information
        harbors = self.board.get_all_harbors()
        print(f"⚓ Harbor count: {len(harbors)}")
        
        harbor_vertices = []
        for vertex_id in range(54):
            if self.board.is_harbor_vertex(vertex_id):
                harbor = self.board.get_harbor_at_vertex(vertex_id)
                harbor_vertices.append((vertex_id, harbor.type.value))
        
        print(f"🏴 Harbor-accessible vertices: {len(harbor_vertices)}")
        
        # Show board summary
        summary = self.board.get_board_summary()
        print(f"📊 Resource distribution: {summary['resource_distribution']}")
        print(f"🎲 Number distribution: {summary['number_distribution']}")
        
        # 🧠 INTELLIGENT STRATEGY RECOMMENDATION
        print("\n🧠 INTELLIGENT STRATEGY ANALYSIS")
        print("=" * 35)
        
        try:
            from src.catan.board_analyzer import BoardStrategyAnalyzer
            analyzer = BoardStrategyAnalyzer(self.board, self.vertex_manager)
            strategy, explanation, details = analyzer.recommend_strategy()
            
            print(f"🎯 RECOMMENDED STRATEGY: {strategy.upper().replace('_', ' ')}")
            print(f"📝 {explanation}")
            print()
            print("📊 Strategy Scores:")
            for strat, score in details['scores'].items():
                indicator = "👑" if strat == strategy else "  "
                print(f"   {indicator} {strat.replace('_', ' ').title()}: {score}")
            
            # Store recommended strategy
            self.recommended_strategy = strategy
            
        except ImportError:
            print("⚠️  Strategy analyzer not available, using balanced as default")
            self.recommended_strategy = "balanced"
        
        print()
    
    def get_recommendations(self, strategy: str = "balanced", top_k: int = 5, settlement_number: int = 1):
        """Get settlement recommendations."""
        if not self.board or not self.vertex_manager:
            print("❌ Board analysis required first")
            return
            
        print(f"🎯 GETTING TOP {top_k} RECOMMENDATIONS ({strategy} strategy)")
        print(f"   Settlement #{settlement_number} placement")
        print("=" * 50)
        
        # Create scorer and recommender
        scorer = SettlementScorer(self.board, self.vertex_manager)
        recommender = SettlementRecommender(self.board, self.vertex_manager, scorer)
        game_state = GameState()
        
        # Get recommendations
        recommendations = recommender.recommend_settlements(
            game_state, strategy=strategy, top_k=top_k, settlement_number=settlement_number
        )
        
        print(f"🏆 TOP {len(recommendations)} SETTLEMENTS:")
        print("-" * 40)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"#{i} | Vertex {rec.vertex_id:2d} | Score: {rec.score:5.1f}")
            print(f"    Harbor: {rec.score_breakdown.harbor_score:4.1f} | Production: {rec.score_breakdown.production_score:5.1f}")
            print(f"    {rec.justification}")
            
            # Show harbor info if applicable
            if self.board.harbors.is_harbor_vertex(rec.vertex_id):
                harbor = self.board.harbors.get_harbor_at_vertex(rec.vertex_id)
                print(f"    ⚓ Harbor: {harbor.type.value}")
            print()
        
        return recommendations
    
    def demonstrate_settlement_progression(self, strategy: str = "balanced", player_id: int = 0):
        """Demonstrate how recommendations change as settlements are placed."""
        if not self.board or not self.vertex_manager:
            print("❌ Board analysis required first")
            return
            
        print("🏆 SETTLEMENT PROGRESSION DEMONSTRATION")
        print("=" * 60)
        print("See how recommendations change with each settlement placement!")
        print()
        
        # Create scorer and recommender
        scorer = SettlementScorer(self.board, self.vertex_manager)
        recommender = SettlementRecommender(self.board, self.vertex_manager, scorer)
        game_state = GameState()
        
        # Get initial recommendations for 1st settlement
        print("🥇 FIRST SETTLEMENT RECOMMENDATIONS:")
        print("-" * 40)
        first_recs = recommender.recommend_settlements(
            game_state, strategy=strategy, player_id=player_id, top_k=3, settlement_number=1
        )
        
        for i, rec in enumerate(first_recs, 1):
            print(f"#{i} | Vertex {rec.vertex_id:2d} | Score: {rec.score:5.1f}")
            print(f"    {rec.justification}")
        
        # Simulate placing the top recommendation
        if first_recs:
            chosen_first = first_recs[0].vertex_id
            game_state.place_settlement_enhanced(player_id, chosen_first)
            print(f"\n✅ Placed first settlement at vertex {chosen_first}")
        
        print(f"\n🥈 SECOND SETTLEMENT RECOMMENDATIONS:")
        print("   (Note how synergy with first settlement affects scores)")
        print("-" * 40)
        
        second_recs = recommender.recommend_settlements(
            game_state, strategy=strategy, player_id=player_id, top_k=3, settlement_number=2
        )
        
        for i, rec in enumerate(second_recs, 1):
            print(f"#{i} | Vertex {rec.vertex_id:2d} | Score: {rec.score:5.1f}")
            print(f"    {rec.justification}")
        
        # Show phase info
        phase_info = game_state.get_settlement_phase_info(player_id)
        print(f"\n📊 GAME STATE:")
        print(f"   Player {player_id} settlements: {len(phase_info['existing_settlements'])}")
        print(f"   Current phase: {phase_info['phase']}")
        print(f"   Next settlement would be #{phase_info['next_settlement_number']}")
        
        return first_recs, second_recs
    
    def generate_artifacts(self, output_dir: str = "interactive_output"):
        """Generate visualization and data files."""
        if not self.board or not self.vertex_manager:
            print("❌ Board analysis required first")
            return
            
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎨 GENERATING ARTIFACTS in {output_dir}/")
        print("=" * 40)
        
        # Create visualizer
        visualizer = CatanVisualizer(self.board, self.vertex_manager)
        
        # Generate board reference
        board_path = os.path.join(output_dir, "custom_board.png")
        visualizer.render_board(board_path, show_vertices=True, show_harbors=True)
        print(f"✅ Board visualization: {board_path}")
        
        # Save board data
        from catan.io_utils import save_board_json
        board_data_path = os.path.join(output_dir, "board_data.json")
        save_board_json(self.board, board_data_path)
        print(f"✅ Board data: {board_data_path}")
        
        # Generate recommendations
        recommendations = self.get_recommendations("balanced", 10)
        if recommendations:
            # Save recommendations
            from catan.io_utils import save_recommendations_csv
            rec_path = os.path.join(output_dir, "recommendations.csv")
            save_recommendations_csv(recommendations, rec_path)
            print(f"✅ Recommendations: {rec_path}")
            
            # Create recommendation visualization
            rec_vis_path = os.path.join(output_dir, "recommended_settlements.png")
            game_state = GameState()
            visualizer.render_recommendations(
                recommendations[:5], game_state, rec_vis_path, show_top_k=5
            )
            print(f"✅ Recommendation visualization: {rec_vis_path}")
        
        print()
        print(f"🎊 All artifacts saved to: {output_dir}/")
    
    def run_interactive_mode(self):
        """Run the full interactive setup experience."""
        self.print_banner()
        
        while True:
            print("🎮 MAIN MENU")
            print("=" * 15)
            print("1. Show board layout")
            print("2. Show harbor layout") 
            print("3. Interactive tile setup")
            print("4. Use preset board")
            print("5. Analyze current board")
            print("6. Get recommendations")
            print("7. Settlement progression demo")
            print("8. Generate artifacts")
            print("9. Exit")
            print()
            
            choice = input("Select option (1-9): ").strip()
            print()
            
            if choice == "1":
                self.show_board_layout()
            elif choice == "2":
                self.show_harbor_layout()
            elif choice == "3":
                if self.interactive_setup():
                    self.create_board_from_setup()
            elif choice == "4":
                self.use_preset_board()
            elif choice == "5":
                self.analyze_board()
            elif choice == "6":
                # Use intelligent strategy if available, otherwise show instruction
                if hasattr(self, 'recommended_strategy'):
                    strategy = self.recommended_strategy
                    print(f"🧠 Using intelligent strategy: {strategy.upper().replace('_', ' ')}")
                else:
                    print("ℹ️  No strategy recommendation available.")
                    print("💡 Tip: Run 'Analyze current board' (option 5) first to get intelligent strategy recommendation!")
                    strategy = input("Manual strategy (balanced/road_focused/dev_focused/city_focused): ").strip()
                    if not strategy:
                        strategy = "balanced"
                        print(f"🎯 Using default strategy: {strategy}")
                
                try:
                    top_k = int(input("Number of recommendations (5): ").strip() or "5")
                except ValueError:
                    top_k = 5
                
                try:
                    settlement_num = int(input("Settlement number (1 for first, 2 for second, etc.) [1]: ").strip() or "1")
                except ValueError:
                    settlement_num = 1
                
                self.get_recommendations(strategy, top_k, settlement_num)
            elif choice == "7":
                print("🚀 SETTLEMENT PROGRESSION DEMONSTRATION")
                print("This shows how recommendations change from 1st to 2nd settlement!")
                print()
                
                strategy = input("Strategy (balanced/road_focused/dev_focused/city_focused) [balanced]: ").strip()
                if not strategy:
                    strategy = "balanced"
                
                try:
                    player_id = int(input("Player ID (0-3) [0]: ").strip() or "0")
                except ValueError:
                    player_id = 0
                
                self.demonstrate_settlement_progression(strategy, player_id)
            elif choice == "8":
                output_dir = input("Output directory (interactive_output): ").strip()
                if not output_dir:
                    output_dir = "interactive_output"
                self.generate_artifacts(output_dir)
            elif choice == "9":
                print("👋 Thanks for using Catan Board Setup!")
                break
            else:
                print("❌ Invalid choice. Please select 1-9.")
            
            print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Interactive Catan Board Setup")
    parser.add_argument("--preset", choices=["standard"], 
                       help="Start with a preset board")
    parser.add_argument("--quick", action="store_true",
                       help="Quick mode: preset board + analysis + artifacts")
    
    args = parser.parse_args()
    
    setup = InteractiveCatanSetup()
    
    if args.quick:
        # Quick mode: automated flow
        setup.print_banner()
        print("🚀 QUICK MODE: Automated setup\n")
        
        setup.use_preset_board("standard")
        setup.analyze_board()
        setup.get_recommendations("balanced", 5)
        setup.generate_artifacts("quick_output")
        
        print("✅ Quick setup complete! Check 'quick_output/' directory.")
        
    elif args.preset:
        # Start with preset
        setup.print_banner()
        setup.use_preset_board(args.preset)
        setup.run_interactive_mode()
        
    else:
        # Full interactive mode
        setup.run_interactive_mode()


if __name__ == "__main__":
    main()
