# -*- coding: utf-8 -*-
"""
VNGE Harmony Link Plugin Testing Framework

This package provides comprehensive mock implementations and testing utilities
for the VNGE Harmony Link Plugin, enabling testing without Unity/VNGE dependencies.
"""

# Import main components for easy access
from .plugin_test_environment import (
    PluginTestEnvironment,
    create_test_environment,
    setup_basic_test_environment,
    setup_integration_test_environment,
    set_plugin_harmony_log_level
)

__version__ = "1.0.0"
__author__ = "Harmony AI Solutions"
__description__ = "Testing framework for VNGE Harmony Link Plugin"

# Package metadata
__all__ = [
    'PluginTestEnvironment',
    'create_test_environment',
    'setup_basic_test_environment',
    'setup_integration_test_environment',
    'set_plugin_harmony_log_level'
]
