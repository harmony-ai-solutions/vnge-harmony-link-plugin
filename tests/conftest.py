"""
Pytest configuration and shared fixtures for VNGE Harmony Link Plugin testing.

This module provides common fixtures and configuration for all tests,
including mock setup, test environment initialization, and cleanup.
"""

import pytest
import sys
import os
import time
import threading
from collections import defaultdict

# Add the src directory to Python path so we can import plugin modules
plugin_src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if plugin_src_dir not in sys.path:
    sys.path.insert(0, plugin_src_dir)

# Add the tests directory to Python path so we can import test framework
tests_dir = os.path.dirname(__file__)
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)

# Import test framework components
from framework.mocks.unity_mocks import setup_unity_mocks
from framework.mocks.system_mocks import setup_system_mocks
from framework.mocks.vnge_mocks import setup_vnge_mocks
from framework.mocks.game_mocks import setup_game_mocks


@pytest.fixture(scope="session", autouse=True)
def setup_mock_environment():
    """
    Session-wide fixture that sets up the complete mock environment.
    This runs once at the beginning of the test session and ensures
    all Unity/VNGE dependencies are mocked before any tests run.
    """
    print("Setting up mock environment for test session...")
    
    # Setup all mock systems
    setup_unity_mocks()
    setup_system_mocks()
    setup_vnge_mocks()
    setup_game_mocks()
    
    print("Mock environment setup complete")
    yield
    
    print("Cleaning up mock environment...")


@pytest.fixture
def mock_config():
    """
    Provides a mock configuration dictionary for testing.
    Based on the harmony.ini structure but with test-appropriate values.
    """
    return {
        'Harmony': {
            'autostart': '0',
            'autostart_delay': '1',  # Reduced for testing
            'start_warmup_time': '0.5'  # Reduced for testing
        },
        'Logging': {
            'log_level': 'DEBUG',
            'show_timestamps': 'true',
            'show_module_names': 'true',
            'truncation_length': '200',
            'truncate_errors': 'false'
        },
        'Scene': {
            'scene': 'test_scene.png',
            'character_entity_id': 'test_character',
            'user_entity_id': 'test_user'
        },
        'Connector': {
            'ws_endpoint': 'ws://127.0.0.1:28080',
            'ws_buffer_size': '8192000',
            'http_endpoint': 'http://127.0.0.1:28080',
            'http_listen_port': '28081'
        },
        'Backend': {},
        'Countenance': {},
        'Perception': {},
        'Movement': {
            'debug_mode': '1'
        },
        'STT': {
            'auto_vad': '1',
            'microphone': 'default',
            'channels': '1',
            'bit_depth': '16',
            'sample_rate': '44100',
            'buffer_clip_duration': '10',
            'record_stepping': '100',
            'debug_save_python_wavs': 'false'
        },
        'TTS': {},
        'Controls.Keymap': {
            'toggle_microphone': 'V',
            'toggle_nonverbal_actions': 'N',
            'toggle_chat_input': 'C'
        }
    }


@pytest.fixture
def test_entity_id():
    """Provides a consistent test entity ID"""
    return "test_entity"


@pytest.fixture
def test_user_entity_id():
    """Provides a consistent test user entity ID"""
    return "test_user"


@pytest.fixture
def sample_action_graph():
    """
    Provides a sample ActionGraph for testing movement functionality.
    """
    return {
        'graph_id': 'test_action_graph',
        'graph_actor': 'test_entity',
        'graph_vector': [
            {
                'action': 'walk',
                'targets': [
                    {
                        'name': 'target_location',
                        'position': [1.0, 0.0, 1.0],
                        'look_at_target': False
                    }
                ],
                'transition_mode': 'linear'
            },
            {
                'action': 'wave',
                'targets': [],
                'transition_mode': 'linear'
            }
        ]
    }


@pytest.fixture
def sample_harmony_event():
    """
    Provides a sample HarmonyLinkEvent for testing.
    """
    # Import here to avoid circular imports
    from harmony_modules.common import HarmonyLinkEvent, EVENT_TYPE_AI_ACTION, EVENT_STATE_NEW
    
    return HarmonyLinkEvent(
        event_id='test_event_001',
        event_type=EVENT_TYPE_AI_ACTION,
        status=EVENT_STATE_NEW,
        payload={'action': 'test_action', 'entity_id': 'test_entity'}
    )


@pytest.fixture
def cleanup_globals():
    """
    Fixture that ensures harmony_globals is cleaned up after each test.
    This prevents test interference.
    """
    yield
    
    # Clean up harmony_globals after test
    try:
        import harmony_globals
        harmony_globals.flush()
    except ImportError:
        pass  # Module not imported in this test


@pytest.fixture
def mock_websocket_server():
    """
    Provides a mock WebSocket server for testing connector functionality.
    """
    from framework.simulation.harmony_link_mock_server import HarmonyLinkMockServer
    
    server = HarmonyLinkMockServer(port=28080)
    server.start()
    
    # Give server time to start
    time.sleep(0.1)
    
    yield server
    
    server.stop()


@pytest.fixture
def performance_monitor():
    """
    Provides a performance monitoring context for timing tests.
    """
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.measurements = defaultdict(list)
        
        def start(self, label="default"):
            self.start_time = time.time()
            return self
        
        def stop(self, label="default"):
            if self.start_time:
                duration = time.time() - self.start_time
                self.measurements[label].append(duration)
                return duration
            return 0
        
        def get_average(self, label="default"):
            measurements = self.measurements[label]
            return sum(measurements) / len(measurements) if measurements else 0
        
        def get_total(self, label="default"):
            return sum(self.measurements[label])
    
    return PerformanceMonitor()


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers based on test names and paths.
    """
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "simulation" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add markers based on test names
        if "websocket" in item.name.lower():
            item.add_marker(pytest.mark.websocket)
        if "animation" in item.name.lower():
            item.add_marker(pytest.mark.animation)
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)


def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Register custom markers
    config.addinivalue_line("markers", "unit: Unit tests for individual modules")
    config.addinivalue_line("markers", "integration: Integration tests for complete workflows")
    config.addinivalue_line("markers", "performance: Performance and timing tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "websocket: WebSocket communication tests")
    config.addinivalue_line("markers", "animation: Character animation tests")
    config.addinivalue_line("markers", "mock: Tests relying on mock objects")


def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    print("\n=== VNGE Harmony Link Plugin Test Session Starting ===")
    print("Python version: {}".format(sys.version))
    print("Test directory: {}".format(os.path.dirname(__file__)))
    print("Plugin source: {}".format(plugin_src_dir))


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    print("\n=== Test Session Finished (exit status: {}) ===".format(exitstatus))
