#!/usr/bin/env python3
"""
Enhanced Catan Settlement Helper - AI-Powered Interface
======================================================

An intelligent, easy-to-use tool for finding the best settlement placements in Catan.
Features AI strategy recommendations and visual intersection references.
"""

import os
from catan_analyzer import CatanAnalyzer
from enhanced_board_setup import EnhancedCatanBoard
from strategy_recommender import StrategyRecommender
from intersection_reference import create_intersection_map


def print_banner():
    """Print an enhanced welcome banner."""
    print("🎲" + "="*60 + "🎲")
    print("       ENHANCED CATAN SETTLEMENT HELPER")
    print("    AI-Powered Strategy & Settlement Optimization")
    print("🎲" + "="*60 + "🎲")
    print()


def setup_intersection_reference():
    """Generate intersection reference if needed."""
    ref_path = "catan_reference/intersection_reference.png"
    
    if not os.path.exists(ref_path):
        print("📋 Setting up intersection reference...")
        create_intersection_map()
        print("✅ Intersection reference created!")
    
    print(f"💡 TIP: Check {ref_path} to see intersection numbers")
    
    # Ask if they want to view it now
    view_ref = input("Do you want to open the intersection reference now? (y/n): ").lower()
    if view_ref.startswith('y'):
        # Try to open the image
        try:
            import subprocess
            subprocess.run(['open', ref_path], check=True)  # macOS
        except:
            try:
                subprocess.run(['xdg-open', ref_path], check=True)  # Linux
            except:
                print(f"Please manually open: {ref_path}")
    
    print()


def get_enhanced_player_info():
    """Get enhanced game information from user."""
    print("📋 GAME SETUP")
    print("-" * 15)
    
    # Number of players
    while True:
        try:
            num_players = int(input("How many players? (3 or 4): "))
            if num_players in [3, 4]:
                break
            print("Please enter 3 or 4.")
        except ValueError:
            print("Please enter a number.")
    
    # Player number
    while True:
        try:
            player_id = int(input(f"Which player are you? (1-{num_players}): ")) - 1
            if 0 <= player_id < num_players:
                break
            print(f"Please enter a number between 1 and {num_players}.")
        except ValueError:
            print("Please enter a number.")
    
    # Board setup type
    print("\n🎲 Board Setup:")
    print("1. Standard Catan board (recommended)")
    print("2. Custom board setup")
    
    while True:
        try:
            board_choice = int(input("Choose board type (1-2): "))
            if board_choice in [1, 2]:
                break
            print("Please enter 1 or 2.")
        except ValueError:
            print("Please enter a number.")
    
    return num_players, player_id, board_choice


def setup_enhanced_board(num_players: int, board_choice: int):
    """Set up the enhanced board with harbors."""
    if board_choice == 1:
        # Standard board
        print("✅ Using standard Catan board layout")
        board = EnhancedCatanBoard(num_players)
        board.create_enhanced_standard_board()
        
        # Create analyzer with enhanced board
        analyzer = CatanAnalyzer(num_players)
        analyzer.board = board  # Replace with enhanced board
        analyzer.optimizer.board = board
        analyzer.visualizer.board = board
        
        return analyzer
    else:
        # Custom board (simplified for now)
        print("🔧 Custom board setup not fully implemented yet.")
        print("   Using standard board with guidance...")
        
        from enhanced_board_setup import create_board_with_setup_guidance
        board = create_board_with_setup_guidance()
        
        analyzer = CatanAnalyzer(num_players)
        analyzer.board = board
        analyzer.optimizer.board = board
        analyzer.visualizer.board = board
        
        return analyzer


def get_existing_settlements_enhanced(analyzer, num_players, current_player):
    """Enhanced settlement input with better guidance."""
    print("\n🏘️  EXISTING SETTLEMENTS")
    print("-" * 25)
    print("Enter settlements that are already on the board")
    print(f"💡 Use the intersection reference image to find numbers (0-{len(analyzer.board.intersections)-1})")
    print("   Just press Enter if no settlements for a player")
    print()
    
    for player in range(num_players):
        if player == current_player:
            player_name = "Your"
            print(f"🫵 {player_name} existing settlements:")
        else:
            player_name = f"Player {player + 1}'s"
            print(f"🏠 {player_name} settlements:")
        
        settlement_count = 0
        while settlement_count < 5:  # Max 5 settlements per player
            if settlement_count == 0:
                prompt = f"  First settlement (intersection #, or Enter if none): "
            else:
                prompt = f"  Settlement #{settlement_count + 1} (intersection #, or Enter to finish): "
            
            settlement_input = input(prompt).strip()
            
            if not settlement_input:
                break
            
            try:
                intersection_id = int(settlement_input)
                
                # Validate intersection exists
                if intersection_id not in analyzer.board.intersections:
                    print(f"  ❌ Intersection {intersection_id} doesn't exist. Try 0-{len(analyzer.board.intersections)-1}")
                    continue
                
                # Check if it's already occupied
                if analyzer.board.intersections[intersection_id].structure is not None:
                    print(f"  ❌ Intersection {intersection_id} is already occupied!")
                    continue
                
                # Add the settlement
                is_city = False
                if settlement_count >= 2:  # After 2 settlements, ask if it's a city
                    city_input = input(f"    Is this a city? (y/n): ").lower()
                    is_city = city_input.startswith('y')
                
                analyzer.add_existing_settlement(intersection_id, player_id=player, is_city=is_city)
                settlement_count += 1
                
                structure_type = "city" if is_city else "settlement"
                print(f"  ✅ Added {structure_type} at intersection {intersection_id}")
                
                # Show harbor information if applicable
                if hasattr(analyzer.board, 'get_harbor_at_intersection'):
                    harbor_info = analyzer.board.get_harbor_at_intersection(intersection_id)
                    if harbor_info[0]:
                        print(f"     🚢 This intersection has a {harbor_info[0]} harbor ({harbor_info[1]}:1 trade)")
                
            except ValueError:
                print("  ❌ Please enter a valid intersection number")
        
        print()


def get_ai_strategy_recommendation(analyzer, player_id):
    """Get AI-powered strategy recommendation."""
    print("🤖 AI STRATEGY ANALYSIS")
    print("-" * 25)
    print("Analyzing current game state to recommend optimal strategy...")
    
    # Create strategy recommender
    recommender = StrategyRecommender(analyzer)
    
    try:
        strategy, reasoning, analysis = recommender.analyze_and_recommend_strategy(player_id)
        
        print(f"\n🎯 RECOMMENDED STRATEGY: {strategy.replace('_', ' ').title()}")
        print("=" * 50)
        print(reasoning)
        
        # Show some key insights
        print(f"\n📊 Key Game State Insights:")
        comp_level = analysis['competition_level']
        print(f"   • Game Phase: {comp_level['phase'].title()}")
        print(f"   • Board Competition: {comp_level['occupied_spots']}/{comp_level['total_spots']} spots taken")
        
        if analysis['harbor_access']['available_harbors'] > 0:
            print(f"   • Available Harbors: {analysis['harbor_access']['available_harbors']}")
        
        # Show resource scarcity
        resource_avail = analysis['resource_availability']
        scarce_resources = [name for name, data in resource_avail.items() 
                          if data['scarcity_level'] > 0.6]
        if scarce_resources:
            print(f"   ⚠️  Limited Resources: {', '.join(scarce_resources)}")
        
        print(f"\n🤔 Do you want to:")
        print("1. Use the AI recommended strategy")
        print("2. Choose your own strategy")
        
        while True:
            try:
                choice = int(input("Your choice (1-2): "))
                if choice in [1, 2]:
                    break
                print("Please enter 1 or 2.")
            except ValueError:
                print("Please enter a number.")
        
        if choice == 1:
            return strategy
        else:
            return choose_manual_strategy()
    
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        print("Falling back to manual strategy selection...")
        return choose_manual_strategy()


def choose_manual_strategy():
    """Manual strategy selection."""
    print("\n🎯 MANUAL STRATEGY SELECTION")
    print("-" * 30)
    print("Choose your strategy:")
    print()
    print("1. 🎪 Balanced - Well-rounded approach for general gameplay")
    print("2. 🛣️  Longest Road - Focus on wood & brick for road building")
    print("3. 🃏 Development Cards - Focus on ore & wheat for dev cards") 
    print("4. 🏰 City Building - Focus on ore & wheat for city upgrades")
    print()
    
    while True:
        try:
            choice = int(input("Choose your strategy (1-4): "))
            if choice in [1, 2, 3, 4]:
                strategies = ['balanced', 'road_focused', 'development_focused', 'city_focused']
                return strategies[choice - 1]
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a number.")


def show_enhanced_recommendations(recommendations, strategy, analyzer, player_id):
    """Display enhanced settlement recommendations."""
    strategy_names = {
        'balanced': '🎪 Balanced',
        'road_focused': '🛣️  Longest Road', 
        'development_focused': '🃏 Development Cards',
        'city_focused': '🏰 City Building'
    }
    
    print(f"\n🎯 TOP SETTLEMENT RECOMMENDATIONS ({strategy_names[strategy]})")
    print("="*65)
    
    if not recommendations:
        print("❌ No valid settlement spots found!")
        print("   This might happen if the board is very crowded.")
        print("   Try a different strategy or check if intersections were entered correctly.")
        return
    
    for i, rec in enumerate(recommendations[:3]):  # Show top 3
        print(f"\n#{i+1} - Intersection {rec.intersection_id}")
        print(f"    Overall Score: {rec.total_score:.1f}/50 ⭐")
        print(f"    Why it's excellent: {rec.reasoning}")
        
        # Enhanced resource breakdown
        resources = []
        total_per_turn = 0
        for resource, amount in rec.resource_production.items():
            if amount > 0:
                cards_per_10_turns = amount * 10
                resources.append(f"{resource.value}: {cards_per_10_turns:.1f}/10 turns")
                total_per_turn += amount
        
        if resources:
            print(f"    📊 Expected Resources: {', '.join(resources)}")
            print(f"    💰 Total Production: {total_per_turn * 10:.1f} cards per 10 turns")
        
        # Harbor bonus info
        if hasattr(analyzer.board, 'get_harbor_at_intersection'):
            harbor_info = analyzer.board.get_harbor_at_intersection(rec.intersection_id)
            if harbor_info[0]:
                print(f"    🚢 Bonus: {harbor_info[0].title()} Harbor ({harbor_info[1]}:1 trade)")
        
        # Detailed score breakdown for #1 recommendation
        if i == 0:
            print(f"    📈 Score Breakdown:")
            print(f"        Resource Value: {rec.resource_score:.1f}")
            print(f"        Diversity Bonus: {rec.diversity_score:.1f}")
            print(f"        Expansion Potential: {rec.expansion_score:.1f}")
            print(f"        Road Building: {rec.road_potential_score:.1f}")
            if rec.port_score > 0:
                print(f"        Harbor Access: {rec.port_score:.1f}")
    
    print(f"\n💡 STRONG RECOMMENDATION:")
    print(f"   Place your settlement at intersection #{recommendations[0].intersection_id}")
    best_rec = recommendations[0]
    if best_rec.total_score > 35:
        quality = "EXCELLENT"
    elif best_rec.total_score > 25:
        quality = "GOOD"
    else:
        quality = "ACCEPTABLE"
    print(f"   This is a {quality} placement with score {best_rec.total_score:.1f}/50")


def generate_enhanced_visual(analyzer, player_id, strategy):
    """Generate enhanced visual board with better information."""
    print(f"\n📊 GENERATING ENHANCED VISUAL BOARD...")
    print("-" * 40)
    
    # Create output directory
    os.makedirs("catan_output", exist_ok=True)
    
    try:
        # Generate the main plot with more detail
        plot_path = analyzer.generate_recommendation_plot(
            player_id=player_id,
            strategy=strategy,
            top_n=5,
            save_path="catan_output/enhanced_settlement_recommendations.png",
            show_all_intersections=True
        )
        
        print(f"✅ Enhanced visual board saved: {plot_path}")
        print("   📍 Shows your top 5 settlement recommendations with detailed scoring")
        print("   🔢 All intersection numbers are displayed for easy reference")
        
        # Also generate resource analysis
        resource_path = analyzer.generate_resource_analysis_plot(
            save_path="catan_output/resource_probability_analysis.png"
        )
        print(f"✅ Resource analysis saved: {resource_path}")
        
        # Try to open the main image
        try_open = input("\nDo you want to open the visual board now? (y/n): ").lower()
        if try_open.startswith('y'):
            try:
                import subprocess
                subprocess.run(['open', plot_path], check=True)  # macOS
            except:
                try:
                    subprocess.run(['xdg-open', plot_path], check=True)  # Linux
                except:
                    print(f"Please manually open: {plot_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Could not generate visual: {e}")
        print("   The analysis still works, just no visual output.")
        return False


def ask_for_additional_analysis():
    """Ask about additional analysis options."""
    print(f"\n🔄 ADDITIONAL ANALYSIS OPTIONS")
    print("-" * 35)
    print("What would you like to do next?")
    print("1. Try a different strategy")
    print("2. Add more settlements and re-analyze")
    print("3. Analyze for a different player")
    print("4. Exit")
    
    while True:
        try:
            choice = int(input("Your choice (1-4): "))
            if choice in [1, 2, 3, 4]:
                return choice
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a number.")


def main():
    """Enhanced main program loop."""
    print_banner()
    
    # Setup intersection reference
    setup_intersection_reference()
    
    while True:
        try:
            # Get game setup
            num_players, player_id, board_choice = get_enhanced_player_info()
            
            # Create enhanced analyzer
            analyzer = setup_enhanced_board(num_players, board_choice)
            
            # Get existing settlements
            get_existing_settlements_enhanced(analyzer, num_players, player_id)
            
            while True:
                # Get AI strategy recommendation
                strategy = get_ai_strategy_recommendation(analyzer, player_id)
                
                # Get recommendations
                print(f"\n🔍 ANALYZING BOARD WITH {strategy.replace('_', ' ').title()} STRATEGY...")
                print("-" * 50)
                recommendations = analyzer.get_optimal_settlements(player_id, strategy, top_n=5)
                
                # Show results
                show_enhanced_recommendations(recommendations, strategy, analyzer, player_id)
                
                # Generate enhanced visual
                if recommendations:
                    generate_enhanced_visual(analyzer, player_id, strategy)
                
                # Ask for additional analysis
                next_action = ask_for_additional_analysis()
                
                if next_action == 1:
                    # Different strategy
                    continue
                elif next_action == 2:
                    # Add more settlements
                    print("\n🏘️  Add more settlements:")
                    get_existing_settlements_enhanced(analyzer, num_players, player_id)
                    continue
                elif next_action == 3:
                    # Different player
                    while True:
                        try:
                            new_player = int(input(f"Which player to analyze? (1-{num_players}): ")) - 1
                            if 0 <= new_player < num_players:
                                player_id = new_player
                                break
                            print(f"Please enter a number between 1 and {num_players}.")
                        except ValueError:
                            print("Please enter a number.")
                    continue
                else:
                    # Exit inner loop
                    break
            
            # Ask if they want to start a new game
            new_game = input("\n🎲 Start analysis for a new game? (y/n): ").lower()
            if not new_game.startswith('y'):
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or restart the program.")
            continue
    
    print(f"\n🎉 Thanks for using Enhanced Catan Settlement Helper!")
    print("   May your settlements prosper and your cities flourish! 🏰🎲")


if __name__ == "__main__":
    print("🏠 Enhanced Catan Settlement Helper")
    print("=" * 50)
    main()
