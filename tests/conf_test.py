# tests/conftest.py
import sys
import os

# Add parent directory to path
# So tests can import scorer, db etc
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))