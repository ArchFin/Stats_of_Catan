# Catan Settlement Optimizer 🎯

A comprehensive, test-backed optimal settlement placement calculator for Settlers of Catan (3-4 players).

## Features

🗺️ **Accurate Board Representation**: Radius-2 hexagonal board with official tile and number token distributions  
🎯 **Optimal Settlement Recommendations**: AI-powered scoring across multiple strategic dimensions  
📊 **Multiple Strategies**: Balanced, longest road, development cards, and city-focused approaches  
🔍 **Detailed Analysis**: Score breakdowns with clear justifications for every recommendation  
🎨 **Rich Visualizations**: High-quality board images with settlement recommendations and references  
📈 **Export Capabilities**: JSON, CSV, and PNG outputs for integration and analysis  

## Quick Start

### 1. Installation

```bash
# Clone the repository
cd Stats_of_Catan

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate a Board

```bash
# Create a standard deterministic board
python scripts/build_board.py

# Or create a randomized board with seed
python scripts/build_board.py --seed 42 --layout randomized
```

This creates:
- `artifacts/board.json` - Board configuration
- `artifacts/vertices.csv` - All settlement vertices  
- `artifacts/board_reference.png` - Visual board reference
- `artifacts/example_state.json` - Example game state

### 3. Get Settlement Recommendations

```bash
# Basic recommendations (balanced strategy)
python scripts/recommend_cli.py

# Specify strategy and number of recommendations
python scripts/recommend_cli.py --strategy road_focused --top-k 5

# Use custom scoring weights
python scripts/recommend_cli.py --weights '{"production":1.5,"balance":0.3,"road":0.8}'

# Analyze a specific vertex across all strategies
python scripts/recommend_cli.py --analyze-vertex 23
```

This creates:
- `artifacts/recommendations.json` - Detailed recommendations
- `artifacts/recommendations.csv` - Tabular format
- `artifacts/optimal_placements.png` - Visual recommendations
- `artifacts/recommendations_report.txt` - Human-readable summary

## Map Model

### Board Geometry
- **Large hexagon** of radius 2 in axial coordinates (q, r)
- **19 tiles** total in classic Catan arrangement
- **~54 vertices** where settlements can be placed

### Tile Distribution (Base Game)
- Forest (wood) ×4
- Pasture (sheep) ×4  
- Fields (wheat) ×4
- Hills (brick) ×3
- Mountains (ore) ×3
- Desert ×1

### Number Tokens
- Distribution: 2×1, 3×2, 4×2, 5×2, 6×2, 8×2, 9×2, 10×2, 11×2, 12×1
- **No token on desert**
- **6 and 8 marked as high-probability** (5 pips each)

### Settlement Rules
- **Distance rule**: No settlements within 1 edge of each other
- **Legal vertices**: All intersection points where 2-3 hexes meet

## Strategy Types

### 🎪 Balanced Strategy
Equal weighting across all factors. Prioritizes versatile settlements with good resource diversity and production.

### 🛣️ Road-Focused Strategy  
Emphasizes wood and brick production for longest road achievement. Values expansion potential and connectivity.

### 🃏 Development-Focused Strategy
Targets ore, wheat, and sheep for development cards. Optimizes for largest army and victory point cards.

### 🏰 City-Focused Strategy
Heavily weights ore and wheat for settlement upgrades. Maximizes late-game point generation.

## Scoring Model

The scoring system evaluates settlements across multiple factors:

### Production Score (Weight: 1.0)
- Dice probability × resource strategy preference × 100
- Based on adjacent hex numbers and resource types

### Balance Score (Weight: 0.4)  
- 20 points for 3+ different resources
- 10 points for 2 different resources
- Encourages resource diversity

### Road Score (Weight: 0.5)
- Adjacent vertex count × 2
- Wood/brick production bonus
- Connectivity to existing road network

### Development Score (Weight: 0.6)
- Ore, wheat, sheep production × 30
- Optimizes for development card purchases

### Robber Penalty (Weight: -0.2)
- 5 points penalty per adjacent 6 or 8
- Accounts for robber targeting risk

### Blocking Score (Weight: 0.3)
- Bonus for positions that limit opponents
- Strategic defensive placement value

## CLI Examples

```bash
# Create board with specific seed
python scripts/build_board.py --seed 42 --layout randomized

# Get top 10 balanced recommendations  
python scripts/recommend_cli.py --top-k 10 --strategy balanced

# Road-focused strategy with custom weights
python scripts/recommend_cli.py \
  --strategy road_focused \
  --weights '{"production":1.0,"road":1.2,"balance":0.2}' \
  --top-k 5

# Analyze specific game state
python scripts/recommend_cli.py \
  --state artifacts/my_game.json \
  --player-id 1

# Compare strategies for a specific vertex
python scripts/recommend_cli.py --analyze-vertex 23
```

## Development

### Running Tests

```bash
# Run all tests
python tests/test_board.py
python tests/test_vertices.py  
python tests/test_scoring.py

# Tests verify:
# - Exactly 19 tiles with correct distribution
# - Proper number token multiplicities  
# - Desert has no number token
# - ~54 vertices discovered
# - Distance rule enforcement
# - Deterministic scoring with fixed seeds
```

### Code Structure

```
src/catan/
├── __init__.py          # Package initialization
├── hex_coords.py        # Axial coordinate math and transformations
├── board.py             # Board assembly and tile management  
├── vertices.py          # Vertex discovery and settlement rules
├── state.py             # Game state management
├── scoring.py           # Settlement scoring model
├── recommend.py         # Recommendation engine
├── visualize.py         # Matplotlib visualization system
└── io_utils.py          # JSON/CSV import/export utilities

scripts/
├── build_board.py       # CLI: Create board and reference artifacts
└── recommend_cli.py     # CLI: Generate settlement recommendations

tests/
├── test_board.py        # Board generation and validation tests
├── test_vertices.py     # Vertex discovery and rule tests
└── test_scoring.py      # Scoring model and strategy tests
```

## Generated Artifacts

### Board Reference (`artifacts/board_reference.png`)
Visual representation showing:
- Hexagonal tiles with resource types
- Number tokens (6s and 8s highlighted)  
- All legal settlement vertices labeled
- Resource type legend

### Settlement Recommendations (`artifacts/optimal_placements.png`)
Board overlay with:
- Top-K recommendations highlighted by rank
- Score values displayed
- Existing settlements shown
- Recommendation legend

### Data Exports
- `board.json` - Complete board configuration
- `vertices.csv` - All vertex positions and properties
- `recommendations.csv` - Ranked settlements with score breakdowns
- `analysis_summary.json` - Comprehensive analysis metadata

## Acceptance Criteria ✅

- ✅ **19-tile radius-2 hex board** with exact base game distribution
- ✅ **Official number token multiplicities** (no 7, correct counts)
- ✅ **Desert has no number token**
- ✅ **~54 vertices discovered** at hex intersection points  
- ✅ **Distance rule enforcement** (no adjacent settlements)
- ✅ **Deterministic generation** with fixed seeds
- ✅ **Multi-factor scoring** with configurable strategy weights
- ✅ **Score breakdowns** and human-readable justifications
- ✅ **High-quality visualizations** with clear vertex labeling
- ✅ **Comprehensive test coverage** validating all core functionality
- ✅ **Clean codebase** with proper structure and documentation

## License

MIT License - feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Please ensure tests pass and follow the existing code style.
