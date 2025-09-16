#!/usr/bin/env python3
"""
Test Interactive Setup Artifacts
================================

Test the interactive setup artifacts generation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interactive_setup import InteractiveCatanSetup

def test_interactive_artifacts():
    """Test the interactive setup artifacts generation."""
    print("🧪 Testing interactive setup artifacts generation...")
    
    # Create setup instance
    setup = InteractiveCatanSetup()
    
    # Load preset board
    setup.use_preset_board()
    print("✅ Preset board loaded")
    
    # Test artifacts generation
    output_dir = "test_output"
    try:
        setup.generate_artifacts(output_dir)
        print("✅ Artifacts generated successfully!")
    except Exception as e:
        print(f"❌ Error generating artifacts: {e}")
        raise
    
    print("🎉 Interactive setup test passed!")

if __name__ == "__main__":
    test_interactive_artifacts()
