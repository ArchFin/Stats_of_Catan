"""
Settlement Recommendation Engine
===============================

Main ranking pipeline for optimal settlement placement.
"""

import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass

from .board import CatanBoard
from .vertices import VertexManager 
from .state import GameState
from .scoring import SettlementScorer, ScoreBreakdown


@dataclass
class RecommendationResult:
    """Result of settlement recommendation analysis."""
    vertex_id: int
    rank: int
    score: float
    score_breakdown: ScoreBreakdown
    justification: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'vertex_id': self.vertex_id,
            'rank': self.rank,
            'score': self.score,
            'score_breakdown': self.score_breakdown.to_dict(),
            'justification': self.justification
        }


class SettlementRecommender:
    """Main recommendation engine for optimal settlement placement."""
    
    def __init__(self, board: CatanBoard, vertex_manager: VertexManager, scorer: SettlementScorer):
        """
        Initialize the recommendation engine.
        
        Args:
            board: The Catan board
            vertex_manager: Vertex manager for the board
            scorer: Settlement scoring system
        """
        self.board = board
        self.vertex_manager = vertex_manager
        self.scorer = scorer
    
    def recommend_settlements(self, game_state: GameState, strategy: str = 'balanced',
                            player_id: int = 0, top_k: int = 10, settlement_number: int = None) -> List[RecommendationResult]:
        """
        Generate top-K settlement recommendations.
        
        Args:
            game_state: Current game state
            strategy: Strategy preference
            player_id: ID of the player making the placement
            top_k: Number of recommendations to return
            settlement_number: Which settlement number this is for the player (1st, 2nd, etc.)
        
        Returns:
            List of RecommendationResult objects, ranked by score
        """
        # Auto-detect settlement number if not provided
        if settlement_number is None:
            settlement_number = game_state.get_settlement_count(player_id) + 1
        
        # Get scored vertices
        scored_vertices = self.scorer.rank_vertices(game_state, strategy, player_id, top_k, settlement_number)
        
        # Convert to recommendation results with justifications
        results = []
        for rank, score_breakdown in enumerate(scored_vertices, 1):
            justification = self._generate_justification(score_breakdown, strategy, settlement_number)
            
            result = RecommendationResult(
                vertex_id=score_breakdown.vertex_id,
                rank=rank,
                score=score_breakdown.total_score,
                score_breakdown=score_breakdown,
                justification=justification
            )
            results.append(result)
        
        return results
    
    def analyze_placement(self, vertex_id: int, game_state: GameState, 
                         strategy: str = 'balanced', player_id: int = 0, settlement_number: int = None) -> RecommendationResult:
        """
        Analyze a specific vertex placement.
        
        Args:
            vertex_id: ID of the vertex to analyze
            game_state: Current game state
            strategy: Strategy preference
            player_id: ID of the player making the placement
            settlement_number: Which settlement number this is for the player
        
        Returns:
            RecommendationResult for the specific vertex
        """
        # Auto-detect settlement number if not provided
        if settlement_number is None:
            settlement_number = game_state.get_settlement_count(player_id) + 1
        
        score_breakdown = self.scorer.score_vertex(vertex_id, game_state, strategy, settlement_number)
        justification = self._generate_justification(score_breakdown, strategy, settlement_number)
        
        return RecommendationResult(
            vertex_id=vertex_id,
            rank=0,  # Not ranked in this context
            score=score_breakdown.total_score,
            score_breakdown=score_breakdown,
            justification=justification
        )
    
    def compare_strategies_for_vertex(self, vertex_id: int, game_state: GameState, 
                                   player_id: int = 0, settlement_number: int = None) -> Dict[str, RecommendationResult]:
        """Compare how different strategies evaluate the same vertex."""
        strategies = ['balanced', 'road_focused', 'dev_focused', 'city_focused']
        results = {}
        
        for strategy in strategies:
            results[strategy] = self.analyze_placement(vertex_id, game_state, strategy, player_id, settlement_number)
        
        return results
    
    def _generate_justification(self, score_breakdown: ScoreBreakdown, strategy: str, settlement_number: int = 1) -> str:
        """Generate human-readable justification for a recommendation."""
        vertex_info = self.vertex_manager.get_vertex_info(score_breakdown.vertex_id)
        if not vertex_info:
            return "Invalid vertex"
        
        justifications = []
        
        # Settlement-specific considerations
        if settlement_number == 1:
            justifications.append("1st settlement: Focus on production and diversity")
        elif settlement_number == 2:
            justifications.append("2nd settlement: Complement existing resources")
        elif settlement_number > 2:
            justifications.append(f"{settlement_number}th settlement: Advanced strategy")
        
        # Production analysis
        if score_breakdown.production_score > 15:
            resources = []
            for resource_name, resource_data in vertex_info['resources'].items():
                if resource_name != 'desert' and resource_data['probability'] > 0.08:
                    prob_pct = resource_data['probability'] * 100
                    resources.append(f"{resource_name} ({prob_pct:.1f}%)")
            
            if resources:
                justifications.append(f"Strong production: {', '.join(resources)}")
        
        # Resource diversity
        resource_count = len([r for r in vertex_info['resources'].keys() if r != 'desert'])
        if resource_count >= 3:
            justifications.append("Excellent resource diversity")
        elif resource_count == 2:
            justifications.append("Good resource diversity")
        
        # Strategy-specific analysis
        if strategy == 'road_focused' and score_breakdown.road_score > 10:
            justifications.append("Good for road building (wood/brick access)")
        elif strategy == 'dev_focused' and score_breakdown.dev_score > 15:
            justifications.append("Excellent for development cards (ore/wheat/sheep)")
        elif strategy == 'city_focused':
            ore_wheat = 0
            for resource in ['ore', 'wheat']:
                if resource in vertex_info['resources']:
                    ore_wheat += vertex_info['resources'][resource]['probability'] * 100
            if ore_wheat > 15:
                justifications.append("Strong for city upgrades (ore/wheat)")
        
        # High probability numbers
        high_prob_numbers = []
        for resource_data in vertex_info['resources'].values():
            for number in resource_data.get('numbers', []):
                if number in (6, 8):
                    high_prob_numbers.append(str(number))
        
        if high_prob_numbers:
            justifications.append(f"High-probability numbers: {', '.join(high_prob_numbers)}")
        
        # Robber risk
        if score_breakdown.robber_penalty > 10:
            justifications.append("High robber risk (multiple 6s/8s)")
        
        # Blocking potential
        if score_breakdown.blocking_score > 5:
            justifications.append("Good blocking position")
        
        if not justifications:
            if score_breakdown.total_score > 10:
                justifications.append("Solid overall placement")
            else:
                justifications.append("Limited strategic value")
        
        return "; ".join(justifications)
    
    def export_recommendations_json(self, recommendations: List[RecommendationResult], 
                                  filepath: str) -> None:
        """Export recommendations to JSON file."""
        data = {
            'recommendations': [rec.to_dict() for rec in recommendations],
            'metadata': {
                'total_recommendations': len(recommendations),
                'board_valid': self.board.validate_board(),
                'total_vertices': self.vertex_manager.get_vertex_count()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_recommendations_csv(self, recommendations: List[RecommendationResult], 
                                 filepath: str) -> None:
        """Export recommendations to CSV file."""
        import csv
        
        with open(filepath, 'w', newline='') as f:
            fieldnames = [
                'rank', 'vertex_id', 'total_score', 
                'production_score', 'balance_score', 'road_score', 
                'dev_score', 'robber_penalty', 'blocking_score',
                'justification'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for rec in recommendations:
                sb = rec.score_breakdown
                writer.writerow({
                    'rank': rec.rank,
                    'vertex_id': rec.vertex_id,
                    'total_score': f"{rec.score:.2f}",
                    'production_score': f"{sb.production_score:.2f}",
                    'balance_score': f"{sb.balance_score:.2f}",
                    'road_score': f"{sb.road_score:.2f}",
                    'dev_score': f"{sb.dev_score:.2f}",
                    'robber_penalty': f"{sb.robber_penalty:.2f}",
                    'blocking_score': f"{sb.blocking_score:.2f}",
                    'justification': rec.justification
                })
    
    def get_summary_report(self, recommendations: List[RecommendationResult], 
                          strategy: str) -> str:
        """Generate a text summary report of recommendations."""
        if not recommendations:
            return "No recommendations available."
        
        lines = [
            f"Catan Settlement Recommendations ({strategy} strategy)",
            "=" * 60,
            ""
        ]
        
        strategy_explanation = self.scorer.get_strategy_explanation(strategy)
        lines.extend([
            f"Strategy: {strategy_explanation}",
            f"Board validated: {self.board.validate_board()}",
            f"Total vertices analyzed: {self.vertex_manager.get_vertex_count()}",
            f"Legal placements found: {len(self.vertex_manager.get_legal_vertices())}",
            "",
            "Top Recommendations:",
            "-" * 30
        ])
        
        for rec in recommendations[:5]:  # Show top 5
            lines.extend([
                f"#{rec.rank} - Vertex {rec.vertex_id}",
                f"    Score: {rec.score:.1f}",
                f"    Why: {rec.justification}",
                ""
            ])
        
        return "\n".join(lines)
