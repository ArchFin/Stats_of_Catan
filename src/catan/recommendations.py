"""
Settlement Recommendation System for Catan
==========================================

Provides intelligent settlement recommendations based on board state,
game state, turn order, and strategy preferences.
"""

from typing import List, Dict, Tuple, Optional
import json

from .board import CatanBoard
from .vertices import VertexManager
from .scoring import SettlementScorer, ScoreBreakdown
from .state import GameState
from .board_analyzer import BoardStrategyAnalyzer


class SettlementRecommender:
    """Intelligent settlement recommendation system."""
    
    def __init__(self, board: CatanBoard, vertex_manager: VertexManager):
        """
        Initialize the recommendation system.
        
        Args:
            board: The Catan board
            vertex_manager: Vertex manager for the board
        """
        self.board = board
        self.vertex_manager = vertex_manager
        self.scorer = SettlementScorer(board, vertex_manager)
        self.strategy_analyzer = BoardStrategyAnalyzer(board, vertex_manager)
    
    def recommend_best_settlements(self, game_state: GameState, player_id: str, 
                                 strategy: Optional[str] = None, 
                                 weights: Optional[Dict[str, float]] = None,
                                 top_k: int = 10) -> List[ScoreBreakdown]:
        """
        Recommend the best settlement locations for a player.
        
        Args:
            game_state: Current game state including existing settlements
            player_id: ID of the player to make recommendations for
            strategy: Strategy preference, or None for automatic selection
            weights: Custom scoring weights, or None for defaults
            top_k: Number of top recommendations to return
            
        Returns:
            List of ScoreBreakdown objects, sorted by total score (highest first)
        """
        # Auto-select strategy if not provided
        if strategy is None:
            strategy = self.strategy_analyzer.recommend_strategy()
        
        # Update scorer weights if provided
        if weights:
            self.scorer.set_weights(weights)
        
        # Get all legal settlement locations
        legal_vertices = []
        # Filter out vertices that are not legally placeable
        for vertex_id in self.vertex_manager.vertices:
            if game_state.is_legal_settlement_placement(vertex_id, self.vertex_manager):
                legal_vertices.add(vertex_id)
        
        # Score all legal vertices
        scored_vertices = []
        for vertex_id in legal_vertices:
            score_breakdown = self.scorer.score_vertex(vertex_id, game_state, player_id, strategy)
            if score_breakdown.total_score > 0:  # Only include positive scores
                scored_vertices.append(score_breakdown)
        
        # Sort by total score (highest first) and return top K
        scored_vertices.sort(key=lambda x: x.total_score, reverse=True)
        return scored_vertices[:top_k]
    
    def analyze_player_position(self, game_state: GameState, player_id: str) -> Dict:
        """
        Analyze a player's current position and provide strategic insights.
        
        Args:
            game_state: Current game state
            player_id: ID of the player to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if player_id not in game_state.players:
            return {"error": f"Player {player_id} not found in game state"}
        
        player = game_state.players[player_id]
        
        # Calculate current resource production
        total_production = 0.0
        resource_production = {}
        
        for settlement_id in player.settlements:
            vertex_info = self.vertex_manager.get_vertex_info(settlement_id)
            if vertex_info:
                for hex_id in vertex_info.adjacent_hexes:
                    hex_tile = self.board.get_hex(hex_id)
                    if hex_tile and hex_tile.resource:
                        prob = self.board.get_dice_probability(hex_tile.number)
                        multiplier = 2 if settlement_id in player.cities else 1
                        
                        if hex_tile.resource not in resource_production:
                            resource_production[hex_tile.resource] = 0.0
                        resource_production[hex_tile.resource] += prob * multiplier
                        total_production += prob * multiplier
        
        # Analyze turn order position
        turn_position = None
        turn_advantage = "unknown"
        if game_state.turn_order and player_id in game_state.turn_order:
            turn_position = game_state.turn_order.index(player_id) + 1
            total_players = len(game_state.turn_order)
            if turn_position <= total_players // 3:
                turn_advantage = "early"
            elif turn_position > 2 * total_players // 3:
                turn_advantage = "late"
            else:
                turn_advantage = "middle"
        
        # Count harbor access
        harbor_count = 0
        harbor_types = []
        for settlement_id in player.settlements:
            harbor = self.board.get_harbor_at_vertex(settlement_id)
            if harbor:
                harbor_count += 1
                harbor_types.append(harbor.type.value)
        
        return {
            "player_id": player_id,
            "settlements": len(player.settlements),
            "cities": len(player.cities),
            "roads": len(player.roads),
            "total_production": round(total_production, 2),
            "resource_production": {str(k): round(v, 2) for k, v in resource_production.items()},
            "harbor_count": harbor_count,
            "harbor_types": harbor_types,
            "turn_position": turn_position,
            "turn_advantage": turn_advantage,
            "recommended_strategy": self.strategy_analyzer.recommend_strategy()
        }
    
    def compare_players(self, game_state: GameState) -> Dict:
        """
        Compare all players' positions and provide relative analysis.
        
        Args:
            game_state: Current game state
            
        Returns:
            Dictionary with comparative analysis
        """
        player_analyses = {}
        for player_id in game_state.players:
            player_analyses[player_id] = self.analyze_player_position(game_state, player_id)
        
        # Find leaders in various categories
        leaders = {
            "most_settlements": max(player_analyses.keys(), 
                                  key=lambda p: player_analyses[p]["settlements"]),
            "most_cities": max(player_analyses.keys(), 
                             key=lambda p: player_analyses[p]["cities"]),
            "most_production": max(player_analyses.keys(), 
                                 key=lambda p: player_analyses[p]["total_production"]),
            "most_harbors": max(player_analyses.keys(), 
                              key=lambda p: player_analyses[p]["harbor_count"])
        }
        
        return {
            "players": player_analyses,
            "leaders": leaders,
            "total_players": len(game_state.players),
            "turn_order": game_state.turn_order
        }
    
    def generate_recommendation_report(self, game_state: GameState, player_id: str, 
                                     top_k: int = 5) -> str:
        """
        Generate a human-readable recommendation report.
        
        Args:
            game_state: Current game state
            player_id: ID of the player to generate report for
            top_k: Number of recommendations to include
            
        Returns:
            Formatted text report
        """
        recommendations = self.recommend_best_settlements(game_state, player_id, top_k=top_k)
        analysis = self.analyze_player_position(game_state, player_id)
        
        report = []
        report.append(f"Settlement Recommendations for Player {player_id}")
        report.append("=" * 50)
        report.append("")
        
        # Player analysis
        report.append("Current Position:")
        report.append(f"  Settlements: {analysis['settlements']}")
        report.append(f"  Cities: {analysis['cities']}")
        report.append(f"  Total Production: {analysis['total_production']}")
        report.append(f"  Harbor Access: {analysis['harbor_count']} harbors")
        if analysis['turn_position']:
            report.append(f"  Turn Position: {analysis['turn_position']} ({analysis['turn_advantage']} player)")
        report.append(f"  Recommended Strategy: {analysis['recommended_strategy']}")
        report.append("")
        
        # Top recommendations
        report.append(f"Top {len(recommendations)} Settlement Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. Vertex {rec.vertex_id} (Score: {rec.total_score:.1f})")
            report.append(f"   Production: {rec.production_score:.1f}, "
                        f"Balance: {rec.balance_score:.1f}, "
                        f"Harbor: {rec.harbor_score:.1f}")
            if rec.blocking_score > 0:
                report.append(f"   Blocking potential: {rec.blocking_score:.1f}")
            report.append("")
        
        return "\n".join(report)
