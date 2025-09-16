# -*- coding: utf-8 -*-
"""
VNGE Harmony Link Plugin Testing Fixtures

This package provides fixture implementations for creating realistic test data
using actual VNGE classes and mock objects.
"""

# Import main fixture functions for easy access
from .game_fixtures import (
    create_game_fixture,
    create_gdata_fixture,
    create_scene_data_fixture,
    create_vncontroller_fixture,
    create_game_fixture_with_scene_data,
    create_game_fixture_with_timers,
    create_performance_test_game_fixture,
    create_game_fixture_with_registered_actors
)

from .actor_fixtures import (
    create_actor_fixture,
    create_oci_char_fixture,
    create_realistic_oci_char_fixture,
    create_multiple_actor_fixtures,
    create_actor_with_animation_history,
    create_actor_with_custom_state
)

__version__ = "1.0.0"
__author__ = "Harmony AI Solutions"
__description__ = "Testing fixtures for VNGE Harmony Link Plugin"

# Package metadata
__all__ = [
    # Game fixtures
    'create_game_fixture',
    'create_gdata_fixture',
    'create_scene_data_fixture',
    'create_vncontroller_fixture',
    'create_game_fixture_with_scene_data',
    'create_game_fixture_with_timers',
    'create_performance_test_game_fixture',
    'create_game_fixture_with_registered_actors',
    
    # Actor fixtures
    'create_actor_fixture',
    'create_oci_char_fixture',
    'create_realistic_oci_char_fixture',
    'create_multiple_actor_fixtures',
    'create_actor_with_animation_history',
    'create_actor_with_custom_state'
]
