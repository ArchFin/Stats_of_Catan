"""Tests for enhanced settlement tracking system."""

import pytest
from src.catan.board import CatanBoard
from src.catan.vertices import VertexManager
from src.catan.state import GameState
from src.catan.scoring import SettlementScorer
from src.catan.recommend import SettlementRecommender


class TestSettlementTracking:
    """Test enhanced settlement tracking functionality."""
    
    @pytest.fixture
    def game_components(self):
        """Create game components for testing."""
        board = CatanBoard(seed=42)
        board.create_standard_board(randomize=False)
        vertex_manager = VertexManager(board)
        scorer = SettlementScorer(board, vertex_manager)
        recommender = SettlementRecommender(board, vertex_manager, scorer)
        
        return {
            'board': board,
            'vertex_manager': vertex_manager,
            'scorer': scorer,
            'recommender': recommender
        }
    
    def test_game_state_initialization(self, game_components):
        """Test that GameState initializes with proper settlement tracking."""
        game_state = GameState()
        
        assert hasattr(game_state, 'player_settlements')
        assert hasattr(game_state, 'settlement_order')
        assert hasattr(game_state, 'current_phase')
        # GameState pre-initializes player_settlements for 4 players
        assert len(game_state.player_settlements) == 4
        assert all(settlements == [] for settlements in game_state.player_settlements.values())
        assert game_state.settlement_order == []
        assert game_state.current_phase == 'initial_placement'
    
    def test_settlement_placement_tracking(self, game_components):
        """Test placing settlements and tracking them per player."""
        game_state = GameState()
        vertex_manager = game_components['vertex_manager']
        
        # Get some legal vertices
        legal_vertices = vertex_manager.get_legal_vertices(set())
        vertex1, vertex2, vertex3 = list(legal_vertices)[:3]
        
        # Place first settlement for player 0
        game_state.place_settlement_enhanced(0, vertex1)
        
        assert game_state.get_settlement_count(0) == 1
        assert game_state.get_settlement_count(1) == 0
        assert vertex1 in game_state.get_player_settlements(0)
        assert len(game_state.settlement_order) == 1
        assert game_state.settlement_order[0] == (vertex1, 0)
        
        # Place settlement for different player
        game_state.place_settlement_enhanced(1, vertex2)
        
        assert game_state.get_settlement_count(0) == 1
        assert game_state.get_settlement_count(1) == 1
        assert vertex2 in game_state.get_player_settlements(1)
        assert len(game_state.settlement_order) == 2
        
        # Place second settlement for player 0
        game_state.place_settlement_enhanced(0, vertex3)
        
        assert game_state.get_settlement_count(0) == 2
        assert vertex3 in game_state.get_player_settlements(0)
        assert len(game_state.settlement_order) == 3
    
    def test_settlement_phase_detection(self, game_components):
        """Test automatic detection of settlement phases."""
        game_state = GameState()
        
        # Initially should be phase 'initial_placement'
        phase_info = game_state.get_settlement_phase_info(0)
        assert phase_info['phase'] == 'initial_placement'
        assert phase_info['next_settlement_number'] == 1
        
        # Place first settlement
        game_state.place_settlement_enhanced(0, 1)
        phase_info = game_state.get_settlement_phase_info(0)
        assert phase_info['next_settlement_number'] == 2
        
        # Place second settlement
        game_state.place_settlement_enhanced(0, 5)
        phase_info = game_state.get_settlement_phase_info(0)
        assert phase_info['next_settlement_number'] == 3
    
    def test_settlement_aware_scoring(self, game_components):
        """Test that scoring considers settlement number."""
        game_state = GameState()
        scorer = game_components['scorer']
        vertex_manager = game_components['vertex_manager']
        
        # Get a legal vertex
        legal_vertices = vertex_manager.get_legal_vertices(set())
        test_vertex = list(legal_vertices)[0]
        
        # Score as first settlement
        score1 = scorer.score_vertex(test_vertex, game_state, 'balanced', settlement_number=1)
        
        # Score as second settlement (after placing first elsewhere)
        game_state.place_settlement_enhanced(0, list(legal_vertices)[1])
        score2 = scorer.score_vertex(test_vertex, game_state, 'balanced', settlement_number=2)
        
        # Scores should be different due to synergy considerations
        assert score1.total_score != score2.total_score
    
    def test_recommendation_engine_integration(self, game_components):
        """Test that recommendation engine works with settlement tracking."""
        game_state = GameState()
        recommender = game_components['recommender']
        
        # Get recommendations for first settlement
        recs1 = recommender.recommend_settlements(game_state, player_id=0, top_k=3)
        
        assert len(recs1) == 3
        assert all(rec.rank > 0 for rec in recs1)
        assert all('1st settlement' in rec.justification for rec in recs1)
        
        # Place a settlement and get recommendations for second
        vertex_manager = game_components['vertex_manager']
        legal_vertices = vertex_manager.get_legal_vertices(set())
        first_settlement = list(legal_vertices)[0]
        game_state.place_settlement_enhanced(0, first_settlement)
        
        recs2 = recommender.recommend_settlements(game_state, player_id=0, top_k=3)
        
        assert len(recs2) == 3
        assert all('2nd settlement' in rec.justification for rec in recs2)
        
        # Recommendations should be different (or at least scores should differ)
        rec1_vertices = {rec.vertex_id for rec in recs1}
        rec2_vertices = {rec.vertex_id for rec in recs2}
        rec1_scores = [rec.score for rec in recs1]
        rec2_scores = [rec.score for rec in recs2]
        
        # Either vertex recommendations or their scores should differ
        assert rec1_vertices != rec2_vertices or rec1_scores != rec2_scores
    
    def test_settlement_serialization(self, game_components):
        """Test that settlement tracking survives serialization."""
        game_state = GameState()
        vertex_manager = game_components['vertex_manager']
        
        # Place some settlements
        legal_vertices = list(vertex_manager.get_legal_vertices(set()))
        game_state.place_settlement_enhanced(0, legal_vertices[0])
        game_state.place_settlement_enhanced(1, legal_vertices[1])
        game_state.place_settlement_enhanced(0, legal_vertices[2])
        
        # Serialize and deserialize
        state_dict = game_state.to_dict()
        new_game_state = GameState.from_dict(state_dict)
        
        # Verify tracking is preserved
        assert new_game_state.get_settlement_count(0) == 2
        assert new_game_state.get_settlement_count(1) == 1
        assert new_game_state.get_player_settlements(0) == game_state.get_player_settlements(0)
        assert new_game_state.get_player_settlements(1) == game_state.get_player_settlements(1)
        assert new_game_state.settlement_order == game_state.settlement_order
    
    def test_synergy_calculation(self, game_components):
        """Test settlement synergy calculation logic."""
        game_state = GameState()
        scorer = game_components['scorer']
        
        # Place a settlement with known resources
        game_state.place_settlement_enhanced(0, 1)
        
        # Score a vertex that would create synergy
        existing_settlements = game_state.get_player_settlements(0)
        synergy_score = scorer._calculate_settlement_synergy(5, existing_settlements, 2)
        
        # Should return a numeric score (could be positive, negative, or zero)
        assert isinstance(synergy_score, (int, float))
        
        # Test with multiple existing settlements
        game_state.place_settlement_enhanced(0, 10)
        existing_settlements = game_state.get_player_settlements(0)
        multi_synergy = scorer._calculate_settlement_synergy(15, existing_settlements, 3)
        assert isinstance(multi_synergy, (int, float))
    
    def test_settlement_number_bias(self, game_components):
        """Test settlement number bias calculation."""
        scorer = game_components['scorer']
        
        # First settlement should have no bias
        bias1 = scorer._calculate_settlement_number_bias(1, 'balanced')
        assert bias1 == 0
        
        # Second settlement should have slight bias toward synergy
        bias2 = scorer._calculate_settlement_number_bias(2, 'balanced')
        assert isinstance(bias2, (int, float))
        
        # Later settlements should have increasing bias
        bias3 = scorer._calculate_settlement_number_bias(3, 'balanced')
        assert isinstance(bias3, (int, float))
    
    def test_multiple_players(self, game_components):
        """Test settlement tracking works correctly with multiple players."""
        game_state = GameState()
        vertex_manager = game_components['vertex_manager']
        legal_vertices = list(vertex_manager.get_legal_vertices(set()))
        
        # Simulate initial placement round (2 settlements per player)
        players = [0, 1, 2, 3]  # 4 players
        for player in players:
            # First settlement
            game_state.place_settlement_enhanced(player, legal_vertices.pop(0))
        
        for player in reversed(players):  # Reverse order for second settlement
            # Second settlement
            game_state.place_settlement_enhanced(player, legal_vertices.pop(0))
        
        # Verify each player has exactly 2 settlements
        for player in players:
            assert game_state.get_settlement_count(player) == 2
            assert len(game_state.get_player_settlements(player)) == 2
        
        # Verify total settlement count
        assert len(game_state.settlement_order) == 8
        
        # Test phase detection for each player after initial round
        for player in players:
            phase_info = game_state.get_settlement_phase_info(player)
            # Phase might still be initial_placement or could be expansion 
            assert phase_info['phase'] in ['initial_placement', 'expansion']
            assert phase_info['next_settlement_number'] == 3
