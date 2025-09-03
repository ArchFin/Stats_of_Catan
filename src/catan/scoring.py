"""
Settlement Scoring System for Catan
====================================

Implements multi-factor scoring for settlement placement optimization,
including production probability, resource balance, road potential, 
development focus, robber penalty, blocking strategy, and harbor access.
"""

import math
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter

from .board import CatanBoard, ResourceType
from .vertices import VertexManager

import math
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

from .board import CatanBoard, ResourceType
from .vertices import VertexManager
from .state import GameState


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of settlement scoring factors."""
    vertex_id: int
    total_score: float
    production_score: float
    balance_score: float
    road_score: float
    dev_score: float
    robber_penalty: float
    blocking_score: float
    harbor_score: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'vertex_id': self.vertex_id,
            'total_score': self.total_score,
            'production_score': self.production_score,
            'balance_score': self.balance_score,
            'road_score': self.road_score,
            'dev_score': self.dev_score,
            'robber_penalty': self.robber_penalty,
            'blocking_score': self.blocking_score,
            'harbor_score': self.harbor_score
        }


class SettlementScorer:
    """Advanced scoring system for settlement placement evaluation."""
    
    def __init__(self, board: CatanBoard, vertex_manager: VertexManager):
        """
        Initialize the scoring system.
        
        Args:
            board: The Catan board
            vertex_manager: Vertex manager for the board
        """
        self.board = board
        self.vertex_manager = vertex_manager
        
        # Default scoring weights
        self.weights = {
            'production': 1.0,     # Resource production probability
            'balance': 0.4,        # Resource diversity
            'road': 0.5,           # Longest road potential
            'dev': 0.6,            # Development card potential
            'robber': -0.2,        # Robber risk penalty
            'blocking': 0.3,       # Blocking opponents
            'harbor': 0.4          # Harbor access bonus
        }
        
        # Resource strategy preferences
        self.resource_preferences = {
            'balanced': {
                ResourceType.WOOD: 1.0,
                ResourceType.BRICK: 1.0,
                ResourceType.SHEEP: 1.0,
                ResourceType.WHEAT: 1.0,
                ResourceType.ORE: 1.0
            },
            'road_focused': {
                ResourceType.WOOD: 1.5,
                ResourceType.BRICK: 1.5,
                ResourceType.SHEEP: 0.8,
                ResourceType.WHEAT: 0.8,
                ResourceType.ORE: 0.7
            },
            'dev_focused': {
                ResourceType.WOOD: 0.7,
                ResourceType.BRICK: 0.7,
                ResourceType.SHEEP: 1.2,
                ResourceType.WHEAT: 1.4,
                ResourceType.ORE: 1.4
            },
            'city_focused': {
                ResourceType.WOOD: 0.8,
                ResourceType.BRICK: 0.8,
                ResourceType.SHEEP: 0.9,
                ResourceType.WHEAT: 1.3,
                ResourceType.ORE: 1.5
            }
        }
    
    def set_weights(self, weights: Dict[str, float]) -> None:
        """Update scoring weights."""
        self.weights.update(weights)
    
    def score_vertex(self, vertex_id: int, game_state: GameState, 
                    strategy: str = 'balanced') -> ScoreBreakdown:
        """
        Score a vertex for settlement placement.
        
        Args:
            vertex_id: ID of the vertex to score
            game_state: Current game state
            strategy: Strategy preference ('balanced', 'road_focused', 'dev_focused', 'city_focused')
        
        Returns:
            ScoreBreakdown with detailed scoring information
        """
        if vertex_id not in self.vertex_manager.vertices:
            return ScoreBreakdown(vertex_id, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        vertex_info = self.vertex_manager.get_vertex_info(vertex_id)
        if not vertex_info:
            return ScoreBreakdown(vertex_id, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Calculate individual score components
        production_score = self._calculate_production_score(vertex_info, strategy)
        balance_score = self._calculate_balance_score(vertex_info)
        road_score = self._calculate_road_score(vertex_id, game_state, vertex_info)
        dev_score = self._calculate_dev_score(vertex_info)
        robber_penalty = self._calculate_robber_penalty(vertex_info)
        blocking_score = self._calculate_blocking_score(vertex_id, game_state)
        harbor_score = self._calculate_harbor_score(vertex_id, strategy)
        
        # Combine scores with weights
        total_score = (
            self.weights['production'] * production_score +
            self.weights['balance'] * balance_score +
            self.weights['road'] * road_score +
            self.weights['dev'] * dev_score +
            self.weights['robber'] * robber_penalty +
            self.weights['blocking'] * blocking_score +
            self.weights['harbor'] * harbor_score
        )
        
        return ScoreBreakdown(
            vertex_id=vertex_id,
            total_score=total_score,
            production_score=production_score,
            balance_score=balance_score,
            road_score=road_score,
            dev_score=dev_score,
            robber_penalty=robber_penalty,
            blocking_score=blocking_score,
            harbor_score=harbor_score
        )
    
    def _calculate_production_score(self, vertex_info: Dict, strategy: str) -> float:
        """Calculate score based on resource production probability."""
        preferences = self.resource_preferences.get(strategy, self.resource_preferences['balanced'])
        
        total_score = 0.0
        
        for resource_name, resource_data in vertex_info['resources'].items():
            if resource_name == 'desert':
                continue
            
            try:
                resource_type = ResourceType(resource_name)
                preference = preferences.get(resource_type, 1.0)
                probability = resource_data['probability']
                
                # Score = probability * preference, scaled to reasonable range
                total_score += probability * preference * 100
                
            except ValueError:
                continue  # Skip invalid resource types
        
        return total_score
    
    def _calculate_balance_score(self, vertex_info: Dict) -> float:
        """Calculate score based on resource diversity."""
        resources = vertex_info['resources']
        
        # Count different resource types (excluding desert)
        resource_types = [r for r in resources.keys() if r != 'desert']
        num_different_resources = len(resource_types)
        
        # Bonus for having multiple different resources
        if num_different_resources >= 3:
            return 20.0
        elif num_different_resources == 2:
            return 10.0
        elif num_different_resources == 1:
            return 2.0
        else:
            return 0.0
    
    def _calculate_road_score(self, vertex_id: int, game_state: GameState, vertex_info: Dict) -> float:
        """Calculate score based on longest road potential."""
        # Simple heuristic: more adjacent vertices = better road potential
        adjacent_count = len(vertex_info['adjacent_vertices'])
        
        # Bonus for wood and brick production (needed for roads)
        wood_brick_bonus = 0.0
        for resource_name in ['wood', 'brick']:
            if resource_name in vertex_info['resources']:
                wood_brick_bonus += vertex_info['resources'][resource_name]['probability'] * 50
        
        # Penalty if vertex is isolated from player's road network
        connectivity_bonus = 0.0
        # TODO: Implement road network connectivity analysis
        
        return adjacent_count * 2.0 + wood_brick_bonus + connectivity_bonus
    
    def _calculate_dev_score(self, vertex_info: Dict) -> float:
        """Calculate score based on development card potential."""
        # Development cards require ore, wheat, and sheep
        dev_resources = ['ore', 'wheat', 'sheep']
        
        dev_score = 0.0
        for resource_name in dev_resources:
            if resource_name in vertex_info['resources']:
                probability = vertex_info['resources'][resource_name]['probability']
                dev_score += probability * 30  # Weight development resources
        
        return dev_score
    
    def _calculate_robber_penalty(self, vertex_info: Dict) -> float:
        """Calculate penalty for being vulnerable to robber (6s and 8s)."""
        penalty = 0.0
        
        for resource_data in vertex_info['resources'].values():
            for number in resource_data.get('numbers', []):
                if number in (6, 8):
                    penalty += 5.0  # Penalty for each 6 or 8
        
        return penalty
    
    def _calculate_blocking_score(self, vertex_id: int, game_state: GameState) -> float:
        """Calculate score for blocking opponents."""
        # Simple heuristic: higher score if this vertex is near opponent settlements
        blocking_score = 0.0
        
        adjacent_vertices = self.vertex_manager.adjacency.get(vertex_id, set())
        
        # Check for nearby opponent structures
        for adj_vertex in adjacent_vertices:
            structure = game_state.get_structure_at_vertex(adj_vertex)
            if structure:
                blocking_score += 5.0  # Bonus for being near opponent structures
        
        return blocking_score
    
    def rank_vertices(self, game_state: GameState, strategy: str = 'balanced',
                     player_id: int = 0, top_k: int = 10) -> List[ScoreBreakdown]:
        """
        Rank all legal vertices for settlement placement.
        
        Args:
            game_state: Current game state
            strategy: Strategy preference
            player_id: ID of the player making the placement
            top_k: Number of top candidates to return
        
        Returns:
            List of ScoreBreakdown objects, sorted by score (highest first)
        """
        legal_vertices = self.vertex_manager.get_legal_vertices(game_state.occupied_vertices)
        
        scores = []
        for vertex_id in legal_vertices:
            score = self.score_vertex(vertex_id, game_state, strategy)
            scores.append(score)
        
        # Sort by total score (descending)
        scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return scores[:top_k]
    
    def _calculate_harbor_score(self, vertex_id: int, strategy: str) -> float:
        """
        Calculate harbor access bonus score.
        
        Args:
            vertex_id: ID of the vertex to score
            strategy: Strategy preference for harbor types
        
        Returns:
            Harbor score (0-30 points)
        """
        harbor = self.board.get_harbor_at_vertex(vertex_id)
        if not harbor:
            return 0.0
        
        # Base score depends on harbor type
        if harbor.type.value == "3:1":
            base_score = 15.0  # Generic harbors are generally useful
        else:
            base_score = 25.0  # Specific resource harbors are more valuable
            
            # Strategy-specific bonuses for 2:1 harbors
            if strategy == 'road_focused' and harbor.resource in (ResourceType.WOOD, ResourceType.BRICK):
                base_score += 5.0
            elif strategy == 'dev_focused' and harbor.resource in (ResourceType.ORE, ResourceType.WHEAT, ResourceType.SHEEP):
                base_score += 5.0
            elif strategy == 'city_focused' and harbor.resource in (ResourceType.ORE, ResourceType.WHEAT):
                base_score += 5.0
        
        return base_score
    
    def get_strategy_explanation(self, strategy: str) -> str:
        """Get explanation of what a strategy prioritizes."""
        explanations = {
            'balanced': "Prioritizes overall resource production and diversity. Good all-around strategy.",
            'road_focused': "Emphasizes wood and brick production for building the longest road. Prioritizes connectivity and expansion potential.",
            'dev_focused': "Focuses on ore, wheat, and sheep for purchasing development cards. Aims for Largest Army and victory point cards.",
            'city_focused': "Heavily weights ore and wheat production for upgrading settlements to cities. Maximizes late-game point generation."
        }
        return explanations.get(strategy, "Unknown strategy")
    
    def compare_strategies(self, vertex_id: int, game_state: GameState) -> Dict[str, ScoreBreakdown]:
        """Compare how different strategies score the same vertex."""
        strategies = ['balanced', 'road_focused', 'dev_focused', 'city_focused']
        
        results = {}
        for strategy in strategies:
            results[strategy] = self.score_vertex(vertex_id, game_state, strategy)
        
        return results
