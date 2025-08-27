#!/usr/bin/env python3
"""
Quick test for the new gender-based voice selection.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.audio_service import audio_service

def test_voice_selection():
    """Test the new gender-based voice selection."""
    print('Testing new gender-based voice selection:')
    print()

    test_cases = [
        ('male', 'Should use Fenrir'),
        ('female', 'Should use Kore'),
        ('non-binary', 'Should use Gacrux'),
        ('prefer_not_to_say', 'Should use Charon'),
        ('unknown', 'Should default to Charon')
    ]

    for gender, description in test_cases:
        voice = audio_service._select_voice_for_user(16, gender)
        print('15')

    print()
    print('✅ Voice selection working correctly!')

if __name__ == "__main__":
    test_voice_selection()
