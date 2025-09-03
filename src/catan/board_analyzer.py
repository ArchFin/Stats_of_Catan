"""
Board Strategy Analyzer
=======================

Analyzes board characteristics to recommend optimal strategies.
"""

from typing import Dict, List, Tuple
from collections import Counter

from .board import CatanBoard, ResourceType
from .vertices import VertexManager


class BoardStrategyAnalyzer:
    """Analyzes board layout to recommend optimal strategies."""
    
    def __init__(self, board: CatanBoard, vertex_manager: VertexManager):
        """Initialize the analyzer."""
        self.board = board
        self.vertex_manager = vertex_manager
    
    def analyze_board_characteristics(self) -> Dict:
        """Analyze key board characteristics for strategy recommendation."""
        characteristics = {}
        
        # 1. Resource abundance analysis
        resource_distribution = self._analyze_resource_distribution()
        characteristics['resources'] = resource_distribution
        
        # 2. Number distribution analysis
        number_quality = self._analyze_number_distribution()
        characteristics['numbers'] = number_quality
        
        # 3. Harbor analysis
        harbor_analysis = self._analyze_harbors()
        characteristics['harbors'] = harbor_analysis
        
        # 4. High-value positions analysis
        position_analysis = self._analyze_vertex_positions()
        characteristics['positions'] = position_analysis
        
        return characteristics
    
    def _analyze_resource_distribution(self) -> Dict:
        """Analyze resource tile distribution and quality."""
        resource_scores = {}
        
        for tile in self.board.tiles.values():
            if tile.resource == ResourceType.DESERT:
                continue
                
            resource = tile.resource.value
            quality_score = tile.probability * 100  # Convert to percentage
            
            if resource not in resource_scores:
                resource_scores[resource] = []
            resource_scores[resource].append(quality_score)
        
        # Calculate average quality per resource
        resource_quality = {}
        for resource, scores in resource_scores.items():
            resource_quality[resource] = {
                'count': len(scores),
                'avg_quality': sum(scores) / len(scores),
                'total_production': sum(scores),
                'has_high_numbers': any(score >= 13.9 for score in scores)  # 6 or 8
            }
        
        return resource_quality
    
    def _analyze_number_distribution(self) -> Dict:
        """Analyze number token distribution."""
        number_counts = Counter()
        high_number_tiles = []
        
        for tile in self.board.tiles.values():
            if tile.number > 0:
                number_counts[tile.number] += 1
                if tile.number in (6, 8):
                    high_number_tiles.append(tile)
        
        return {
            'distribution': dict(number_counts),
            'high_number_count': len(high_number_tiles),
            'high_number_resources': [tile.resource.value for tile in high_number_tiles]
        }
    
    def _analyze_harbors(self) -> Dict:
        """Analyze harbor placement and types."""
        harbors = self.board.get_all_harbors()
        harbor_types = Counter()
        resource_harbors = []
        
        for harbor in harbors.values():
            harbor_types[harbor.type.value] += 1
            if harbor.resource:
                resource_harbors.append(harbor.resource.value)
        
        return {
            'total_harbors': len(harbors),
            'types': dict(harbor_types),
            'resource_harbors': resource_harbors,
            'generic_harbors': harbor_types.get('3:1', 0)
        }
    
    def _analyze_vertex_positions(self) -> Dict:
        """Analyze vertex quality and clustering."""
        # This would analyze vertex positions, adjacencies, etc.
        # For now, return basic info
        total_vertices = len(self.vertex_manager.vertices)
        harbor_vertices = sum(1 for vid in range(total_vertices) 
                            if self.board.is_harbor_vertex(vid))
        
        return {
            'total_vertices': total_vertices,
            'harbor_vertices': harbor_vertices,
            'non_harbor_vertices': total_vertices - harbor_vertices
        }
    
    def recommend_strategy(self) -> Tuple[str, str, Dict]:
        """
        Recommend the best strategy based on board analysis.
        
        Returns:
            Tuple of (strategy_name, explanation, analysis_details)
        """
        characteristics = self.analyze_board_characteristics()
        
        # Strategy scoring system
        strategy_scores = {
            'balanced': 0,
            'road_focused': 0,
            'dev_focused': 0,
            'city_focused': 0
        }
        
        resources = characteristics['resources']
        harbors = characteristics['harbors']
        numbers = characteristics['numbers']
        
        # 1. Analyze wood/brick availability (road strategy)
        wood_quality = resources.get('wood', {}).get('total_production', 0)
        brick_quality = resources.get('brick', {}).get('total_production', 0)
        road_resources = wood_quality + brick_quality
        
        if road_resources > 60:  # High wood/brick production
            strategy_scores['road_focused'] += 30
        
        # Check for wood/brick harbors
        if 'wood' in harbors['resource_harbors']:
            strategy_scores['road_focused'] += 15
        if 'brick' in harbors['resource_harbors']:
            strategy_scores['road_focused'] += 15
        
        # 2. Analyze ore/wheat/sheep availability (dev strategy)
        ore_quality = resources.get('ore', {}).get('total_production', 0)
        wheat_quality = resources.get('wheat', {}).get('total_production', 0)
        sheep_quality = resources.get('sheep', {}).get('total_production', 0)
        dev_resources = ore_quality + wheat_quality + sheep_quality
        
        if dev_resources > 80:  # High dev card resources
            strategy_scores['dev_focused'] += 30
        
        # Check for dev-friendly harbors
        dev_harbors = sum(1 for r in ['ore', 'wheat', 'sheep'] if r in harbors['resource_harbors'])
        strategy_scores['dev_focused'] += dev_harbors * 10
        
        # 3. Analyze ore/wheat for cities (city strategy)
        city_resources = ore_quality + wheat_quality
        
        if city_resources > 50:  # Good city resources
            strategy_scores['city_focused'] += 25
            
        # Bonus for ore/wheat harbors
        if 'ore' in harbors['resource_harbors']:
            strategy_scores['city_focused'] += 20
        if 'wheat' in harbors['resource_harbors']:
            strategy_scores['city_focused'] += 15
        
        # 4. Balanced strategy gets points for overall distribution
        resource_balance = len([r for r in resources.values() if r.get('total_production', 0) > 30])
        strategy_scores['balanced'] += resource_balance * 8
        
        # Bonus for generic harbors (good for balanced)
        strategy_scores['balanced'] += harbors['generic_harbors'] * 5
        
        # 5. High numbers bonus
        high_number_resources = numbers['high_number_resources']
        for resource in high_number_resources:
            if resource in ['wood', 'brick']:
                strategy_scores['road_focused'] += 8
            elif resource in ['ore', 'wheat']:
                strategy_scores['city_focused'] += 8
            elif resource in ['ore', 'wheat', 'sheep']:
                strategy_scores['dev_focused'] += 6
        
        # Find best strategy
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])
        strategy_name = best_strategy[0]
        
        # Generate explanation
        explanations = {
            'balanced': self._explain_balanced(characteristics),
            'road_focused': self._explain_road_focused(characteristics),
            'dev_focused': self._explain_dev_focused(characteristics),
            'city_focused': self._explain_city_focused(characteristics)
        }
        
        explanation = explanations[strategy_name]
        
        return strategy_name, explanation, {
            'scores': strategy_scores,
            'characteristics': characteristics
        }
    
    def _explain_balanced(self, characteristics: Dict) -> str:
        """Generate explanation for balanced strategy."""
        resources = characteristics['resources']
        harbors = characteristics['harbors']
        
        reasons = []
        
        # Check resource diversity
        good_resources = [r for r, data in resources.items() 
                         if data.get('total_production', 0) > 25]
        if len(good_resources) >= 4:
            reasons.append(f"Good diversity with {len(good_resources)} productive resources")
        
        # Check harbor variety
        if harbors['generic_harbors'] >= 2:
            reasons.append(f"{harbors['generic_harbors']} generic harbors provide trading flexibility")
            
        # Check for moderate production across all resources
        if all(data.get('total_production', 0) > 15 for data in resources.values()):
            reasons.append("All resources have decent production")
        
        if not reasons:
            reasons.append("Even resource distribution favors flexible approach")
        
        return f"This board rewards a balanced strategy. {'. '.join(reasons)}."
    
    def _explain_road_focused(self, characteristics: Dict) -> str:
        """Generate explanation for road-focused strategy."""
        resources = characteristics['resources']
        harbors = characteristics['harbors']
        
        reasons = []
        
        wood_prod = resources.get('wood', {}).get('total_production', 0)
        brick_prod = resources.get('brick', {}).get('total_production', 0)
        
        if wood_prod > 30:
            reasons.append(f"Excellent wood production ({wood_prod:.1f})")
        if brick_prod > 25:
            reasons.append(f"Strong brick production ({brick_prod:.1f})")
        
        road_harbors = [h for h in harbors['resource_harbors'] if h in ['wood', 'brick']]
        if road_harbors:
            reasons.append(f"{', '.join(road_harbors)} harbor(s) boost road building")
        
        if not reasons:
            reasons.append("Wood and brick availability supports road expansion")
        
        return f"This board favors road building strategy. {'. '.join(reasons)}."
    
    def _explain_dev_focused(self, characteristics: Dict) -> str:
        """Generate explanation for development-focused strategy."""
        resources = characteristics['resources']
        harbors = characteristics['harbors']
        
        reasons = []
        
        ore_prod = resources.get('ore', {}).get('total_production', 0)
        wheat_prod = resources.get('wheat', {}).get('total_production', 0)
        sheep_prod = resources.get('sheep', {}).get('total_production', 0)
        
        if ore_prod > 25:
            reasons.append(f"Strong ore production ({ore_prod:.1f})")
        if wheat_prod > 30:
            reasons.append(f"Excellent wheat production ({wheat_prod:.1f})")
        if sheep_prod > 25:
            reasons.append(f"Good sheep production ({sheep_prod:.1f})")
        
        dev_harbors = [h for h in harbors['resource_harbors'] if h in ['ore', 'wheat', 'sheep']]
        if dev_harbors:
            reasons.append(f"{', '.join(dev_harbors)} harbor(s) support development cards")
        
        if not reasons:
            reasons.append("Development card resources are well-positioned")
        
        return f"This board supports development card strategy. {'. '.join(reasons)}."
    
    def _explain_city_focused(self, characteristics: Dict) -> str:
        """Generate explanation for city-focused strategy."""
        resources = characteristics['resources']
        harbors = characteristics['harbors']
        
        reasons = []
        
        ore_prod = resources.get('ore', {}).get('total_production', 0)
        wheat_prod = resources.get('wheat', {}).get('total_production', 0)
        
        if ore_prod > 30:
            reasons.append(f"Excellent ore production ({ore_prod:.1f})")
        if wheat_prod > 30:
            reasons.append(f"Strong wheat production ({wheat_prod:.1f})")
        
        city_harbors = [h for h in harbors['resource_harbors'] if h in ['ore', 'wheat']]
        if city_harbors:
            reasons.append(f"{', '.join(city_harbors)} harbor(s) facilitate city upgrades")
        
        if not reasons:
            reasons.append("Ore and wheat positioning favors city development")
        
        return f"This board rewards city building strategy. {'. '.join(reasons)}."
