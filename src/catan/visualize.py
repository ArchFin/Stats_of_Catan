"""
Catan Board Visualization System
===============================

Matplotlib-based plotting for boards, vertices, and settlement recommendations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Dict, List, Set, Optional, Tuple
import math

from .hex_coords import HexCoord, axial_to_pixel, hex_corners
from .board import CatanBoard, ResourceType
from .vertices import VertexManager
from .state import GameState
from .recommend import RecommendationResult


class CatanVisualizer:
    """Visualization system for Catan boards and recommendations."""
    
    def __init__(self, board: CatanBoard, vertex_manager: VertexManager):
        """
        Initialize the visualizer.
        
        Args:
            board: The Catan board
            vertex_manager: Vertex manager for the board
        """
        self.board = board
        self.vertex_manager = vertex_manager
        
        # Color scheme for resources
        self.resource_colors = {
            ResourceType.WOOD: '#228B22',      # Forest Green
            ResourceType.BRICK: '#8B4513',     # Saddle Brown
            ResourceType.SHEEP: '#90EE90',     # Light Green
            ResourceType.WHEAT: '#FFD700',     # Gold
            ResourceType.ORE: '#708090',       # Slate Gray
            ResourceType.DESERT: '#F5DEB3'     # Wheat (tan)
        }
        
        # Color scheme for players
        self.player_colors = ['red', 'blue', 'orange', 'white']
        
        # Hex size for visualization
        self.hex_size = 1.0
    
    def render_board(self, save_path: str, show_vertices: bool = True, 
                    show_numbers: bool = True, show_harbors: bool = True) -> None:
        """
        Render the complete board with tiles, numbers, and vertices.
        
        Args:
            save_path: Path to save the image
            show_vertices: Whether to show vertex labels
            show_numbers: Whether to show number tokens
            show_harbors: Whether to show harbor locations (if implemented)
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Draw hexagonal tiles
        self._draw_hexes(ax, show_numbers)
        
        # Draw vertices if requested
        if show_vertices:
            self._draw_vertices(ax)
        
        # Draw harbors if requested and implemented
        if show_harbors:
            self._draw_harbors(ax)
        
        # Set up the plot
        self._setup_plot(ax, "Catan Board Reference")
        
        # Add legend
        self._add_resource_legend(ax)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def render_recommendations(self, recommendations: List[RecommendationResult], 
                             game_state: GameState, save_path: str, 
                             show_top_k: int = 5) -> None:
        """
        Render board with settlement recommendations highlighted.
        
        Args:
            recommendations: List of settlement recommendations
            game_state: Current game state
            save_path: Path to save the image
            show_top_k: Number of top recommendations to highlight
        """
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))
        
        # Draw base board
        self._draw_hexes(ax, show_numbers=True)
        
        # Draw existing structures
        self._draw_existing_structures(ax, game_state)
        
        # Draw all vertices (lightly)
        self._draw_vertices(ax, alpha=0.3)
        
        # Highlight top recommendations
        self._draw_recommendations(ax, recommendations[:show_top_k])
        
        # Set up the plot
        self._setup_plot(ax, f"Settlement Recommendations (Top {show_top_k})")
        
        # Add legends
        self._add_resource_legend(ax)
        self._add_recommendation_legend(ax, recommendations[:show_top_k])
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def render_strategy_comparison(self, vertex_id: int, strategy_results: Dict[str, RecommendationResult], 
                                 save_path: str) -> None:
        """
        Render comparison of how different strategies score a vertex.
        
        Args:
            vertex_id: ID of the vertex being compared
            strategy_results: Dictionary mapping strategy names to results
            save_path: Path to save the image
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        axes = [ax1, ax2, ax3, ax4]
        strategies = list(strategy_results.keys())
        
        for i, (strategy, result) in enumerate(strategy_results.items()):
            if i >= 4:
                break
            
            ax = axes[i]
            
            # Draw board
            self._draw_hexes(ax, show_numbers=True)
            
            # Highlight the vertex being analyzed
            vertex = self.vertex_manager.vertices[vertex_id]
            x, y = vertex.position
            
            circle = patches.Circle((x, y), 0.15, color='red', alpha=0.8, zorder=10)
            ax.add_patch(circle)
            
            # Add score information
            score_text = f"{strategy.replace('_', ' ').title()}\nScore: {result.score:.1f}"
            ax.text(x, y - 0.4, score_text, ha='center', va='top', 
                   fontsize=10, weight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            
            self._setup_plot(ax, f"{strategy.replace('_', ' ').title()} Strategy")
        
        plt.suptitle(f"Strategy Comparison for Vertex {vertex_id}", fontsize=16, weight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _draw_hexes(self, ax, show_numbers: bool = True) -> None:
        """Draw all hexagonal tiles."""
        for hex_coord, tile in self.board.tiles.items():
            center_x, center_y = axial_to_pixel(hex_coord, self.hex_size)
            
            # Create hexagon
            corners = hex_corners(hex_coord, self.hex_size)
            hex_patch = patches.Polygon(corners, closed=True, 
                                      facecolor=self.resource_colors[tile.resource],
                                      edgecolor='black', linewidth=2)
            ax.add_patch(hex_patch)
            
            # Add resource label
            resource_name = tile.resource.value.title()
            ax.text(center_x, center_y + 0.2, resource_name, 
                   ha='center', va='center', fontsize=9, weight='bold')
            
            # Add number token
            if show_numbers and tile.number > 0:
                # Circle for number token
                circle = patches.Circle((center_x, center_y - 0.2), 0.2, 
                                      facecolor='white', edgecolor='black', linewidth=2)
                ax.add_patch(circle)
                
                # Number text
                font_weight = 'bold' if tile.is_high_probability else 'normal'
                color = 'red' if tile.is_high_probability else 'black'
                
                ax.text(center_x, center_y - 0.2, str(tile.number),
                       ha='center', va='center', fontsize=12, 
                       weight=font_weight, color=color)
                
                # Add pip dots for high-probability numbers
                if tile.is_high_probability:
                    pips = "•" * tile.pips
                    ax.text(center_x, center_y - 0.4, pips,
                           ha='center', va='center', fontsize=8, color='red')
    
    def _draw_vertices(self, ax, alpha: float = 1.0) -> None:
        """Draw all vertices with labels."""
        for vertex_id, vertex in self.vertex_manager.vertices.items():
            x, y = vertex.position
            
            # Draw vertex marker
            circle = patches.Circle((x, y), 0.08, 
                                  facecolor='blue', edgecolor='white',
                                  alpha=alpha, linewidth=1)
            ax.add_patch(circle)
            
            # Add vertex ID label
            ax.text(x + 0.12, y + 0.12, str(vertex_id),
                   ha='left', va='bottom', fontsize=8, 
                   color='blue', weight='bold', alpha=alpha)
    
    def _draw_existing_structures(self, ax, game_state: GameState) -> None:
        """Draw existing settlements, cities, and roads."""
        # Draw settlements
        for vertex_id, player_id in game_state.settlements.items():
            if vertex_id in self.vertex_manager.vertices:
                vertex = self.vertex_manager.vertices[vertex_id]
                x, y = vertex.position
                
                # Settlement as square
                square = patches.Rectangle((x - 0.1, y - 0.1), 0.2, 0.2,
                                         facecolor=self.player_colors[player_id % len(self.player_colors)],
                                         edgecolor='black', linewidth=2)
                ax.add_patch(square)
        
        # Draw cities
        for vertex_id, player_id in game_state.cities.items():
            if vertex_id in self.vertex_manager.vertices:
                vertex = self.vertex_manager.vertices[vertex_id]
                x, y = vertex.position
                
                # City as larger square with cross
                square = patches.Rectangle((x - 0.15, y - 0.15), 0.3, 0.3,
                                         facecolor=self.player_colors[player_id % len(self.player_colors)],
                                         edgecolor='black', linewidth=2)
                ax.add_patch(square)
                
                # Add cross to indicate city
                ax.plot([x - 0.1, x + 0.1], [y, y], 'k-', linewidth=2)
                ax.plot([x, x], [y - 0.1, y + 0.1], 'k-', linewidth=2)
        
        # Draw roads
        for edge in game_state.roads:
            vertex1_id, vertex2_id = edge
            if (vertex1_id in self.vertex_manager.vertices and 
                vertex2_id in self.vertex_manager.vertices):
                
                v1 = self.vertex_manager.vertices[vertex1_id]
                v2 = self.vertex_manager.vertices[vertex2_id]
                
                ax.plot([v1.position[0], v2.position[0]], 
                       [v1.position[1], v2.position[1]], 
                       'brown', linewidth=4, alpha=0.7)
    
    def _draw_recommendations(self, ax, recommendations: List[RecommendationResult]) -> None:
        """Draw highlighted settlement recommendations."""
        colors = ['gold', 'orange', 'red', 'purple', 'pink']
        
        for i, rec in enumerate(recommendations):
            if rec.vertex_id in self.vertex_manager.vertices:
                vertex = self.vertex_manager.vertices[rec.vertex_id]
                x, y = vertex.position
                
                # Draw recommendation marker
                color = colors[i % len(colors)]
                circle = patches.Circle((x, y), 0.12, 
                                      facecolor=color, edgecolor='black',
                                      linewidth=2, alpha=0.9, zorder=10)
                ax.add_patch(circle)
                
                # Add rank number
                ax.text(x, y, str(rec.rank),
                       ha='center', va='center', fontsize=10, 
                       weight='bold', color='black')
                
                # Add score below
                ax.text(x, y - 0.25, f"{rec.score:.1f}",
                       ha='center', va='top', fontsize=8, 
                       weight='bold', color=color,
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    def _draw_harbors(self, ax) -> None:
        """Draw harbor locations with proper symbols and labels."""
        harbors = self.board.get_all_harbors()
        
        # Harbor color scheme
        harbor_colors = {
            '3:1': '#4169E1',        # Royal Blue for generic
            '2:1_wood': '#228B22',   # Forest Green
            '2:1_brick': '#8B4513',  # Saddle Brown
            '2:1_sheep': '#90EE90',  # Light Green
            '2:1_wheat': '#FFD700',  # Gold
            '2:1_ore': '#708090'     # Slate Gray
        }
        
        for harbor_id, harbor in harbors.items():
            # Calculate harbor position dynamically based on vertex locations
            harbor_x, harbor_y = self._calculate_dynamic_harbor_position(harbor)
            
            # Draw harbor symbol (larger and more visible)
            color = harbor_colors.get(harbor.type.value, '#4169E1')
            
            # Draw harbor background circle (larger)
            circle = plt.Circle((harbor_x, harbor_y), 0.4, 
                              facecolor=color, edgecolor='white', 
                              linewidth=3, alpha=0.9, zorder=15)
            ax.add_patch(circle)
            
            # Draw harbor text
            if harbor.type.value == '3:1':
                text = '3:1'
                text_color = 'white'
            else:
                resource_short = {
                    'wood': 'W', 'brick': 'B', 'sheep': 'S', 
                    'wheat': 'Wh', 'ore': 'O'
                }
                resource_name = harbor.resource.value if harbor.resource else ''
                text = f"2:1\n{resource_short.get(resource_name, '?')}"
                text_color = 'white'
            
            ax.text(harbor_x, harbor_y, text, 
                   ha='center', va='center', fontsize=9, 
                   weight='bold', color=text_color, zorder=16)
            
            # Mark harbor vertices with visible indicators
            for vertex_id in harbor.vertices:
                if vertex_id in self.vertex_manager.vertices:
                    vertex = self.vertex_manager.vertices[vertex_id]
                    v_x, v_y = vertex.position
                    
                    # Draw harbor indicator at vertex (more visible)
                    marker = plt.Circle((v_x, v_y), 0.12, 
                                      facecolor=color, edgecolor='white', 
                                      linewidth=2, alpha=1.0, zorder=14)
                    ax.add_patch(marker)
                    
                    # Draw connection line to harbor
                    ax.plot([harbor_x, v_x], [harbor_y, v_y], 
                           color=color, linewidth=2, alpha=0.7, 
                           linestyle='--', zorder=13)
    
    def _calculate_dynamic_harbor_position(self, harbor) -> Tuple[float, float]:
        """Calculate harbor position based on vertex locations."""
        if len(harbor.vertices) != 2:
            return (0.0, 0.0)  # Fallback
        
        v1_id, v2_id = harbor.vertices
        if v1_id not in self.vertex_manager.vertices or v2_id not in self.vertex_manager.vertices:
            return (0.0, 0.0)  # Fallback
        
        v1 = self.vertex_manager.vertices[v1_id]
        v2 = self.vertex_manager.vertices[v2_id]
        
        # Calculate midpoint between vertices
        mid_x = (v1.position[0] + v2.position[0]) / 2
        mid_y = (v1.position[1] + v2.position[1]) / 2
        
        # Calculate direction vector from board center to midpoint
        import math
        center_to_mid_x = mid_x - 0  # board center at (0, 0)
        center_to_mid_y = mid_y - 0
        
        # Normalize and extend outward to place harbor on edge
        distance = math.sqrt(center_to_mid_x**2 + center_to_mid_y**2)
        if distance > 0:
            unit_x = center_to_mid_x / distance
            unit_y = center_to_mid_y / distance
            
            # Place harbor further out from the edge
            harbor_x = mid_x + unit_x * 0.8
            harbor_y = mid_y + unit_y * 0.8
            
            return (harbor_x, harbor_y)
        
        return (mid_x, mid_y)  # Fallback to midpoint
    
    def _setup_plot(self, ax, title: str) -> None:
        """Set up plot axes and styling."""
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        
        # Calculate plot bounds
        all_positions = [v.position for v in self.vertex_manager.vertices.values()]
        if all_positions:
            xs, ys = zip(*all_positions)
            margin = 1.0
            ax.set_xlim(min(xs) - margin, max(xs) + margin)
            ax.set_ylim(min(ys) - margin, max(ys) + margin)
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add grid for reference
        ax.grid(True, alpha=0.2)
    
    def _add_resource_legend(self, ax) -> None:
        """Add legend showing resource colors."""
        legend_elements = []
        for resource, color in self.resource_colors.items():
            if resource != ResourceType.DESERT:  # Skip desert in main legend
                legend_elements.append(
                    patches.Patch(color=color, label=resource.value.title())
                )
        
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    def _add_recommendation_legend(self, ax, recommendations: List[RecommendationResult]) -> None:
        """Add legend for recommendation rankings."""
        colors = ['gold', 'orange', 'red', 'purple', 'pink']
        
        legend_elements = []
        for i, rec in enumerate(recommendations):
            color = colors[i % len(colors)]
            legend_elements.append(
                patches.Patch(color=color, 
                            label=f"#{rec.rank} (Score: {rec.score:.1f})")
            )
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.02, 0.7),
                 title="Top Recommendations")
    
    def create_vertex_reference_table(self, save_path: str) -> None:
        """Create a reference table showing all vertices and their properties."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get vertex data
        vertex_data = self.vertex_manager.get_vertices_csv_data()
        
        # Create table data
        table_data = []
        headers = ['Vertex ID', 'Position (X, Y)', 'Incident Hexes', 'Hex Count', 'Boundary']
        
        for vertex in vertex_data[:20]:  # Show first 20 vertices
            table_data.append([
                vertex['vertex_id'],
                f"({vertex['x']:.2f}, {vertex['y']:.2f})",
                vertex['incident_hexes'][:30] + "..." if len(vertex['incident_hexes']) > 30 else vertex['incident_hexes'],
                vertex['hex_count'],
                "Yes" if vertex['is_boundary'] else "No"
            ])
        
        # Create table
        table = ax.table(cellText=table_data, colLabels=headers, 
                        cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        
        # Style the table
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title(f'Vertex Reference Table (First 20 of {len(vertex_data)} vertices)', 
                    fontsize=14, weight='bold', pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
