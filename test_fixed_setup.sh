#!/bin/bash
# Test the interactive setup with automated input

echo "Testing interactive setup with preset board and artifacts generation..."

# Simulate selecting option 4 (preset board), then option 5 (analyze board), then option 7 (generate artifacts), then option 8 (exit)
echo -e "4\n5\n7\ntest_output\n8" | python3.11 interactive_setup.py

echo "Test completed!"
