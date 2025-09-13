"""
Unit Tests for harmony_modules/common.py

Tests the HarmonyLinkEvent system, base classes, event types, and constants
using direct VNGE imports from Lib directory.
"""

import sys
import os
import time

# Add the src directory to the path so we can import the plugin modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add the Lib directory to the path so we can import VNGE modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Lib'))

# Add the tests directory to the path so we can import the test framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework.plugin_test_environment import PluginTestEnvironment


class TestHarmonyLinkEvent:
    """Test HarmonyLinkEvent class functionality"""
    
    def test_event_creation_basic(self):
        """Test basic HarmonyLinkEvent creation"""
        with PluginTestEnvironment() as env:
            # Import after mocks are set up
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            
            event = HarmonyLinkEvent("event_123", "test_event", EVENT_STATE_NEW, {"key": "value"})
            
            assert event.event_id == "event_123"
            assert event.event_type == "test_event"
            assert event.status == EVENT_STATE_NEW
            assert event.payload == {"key": "value"}
    
    def test_event_creation_with_different_states(self):
        """Test HarmonyLinkEvent creation with different states"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import (
                HarmonyLinkEvent, 
                EVENT_STATE_NEW, 
                EVENT_STATE_PENDING, 
                EVENT_STATE_DONE, 
                EVENT_STATE_ERROR
            )
            
            # Test different states
            new_event = HarmonyLinkEvent("1", "test", EVENT_STATE_NEW, {})
            pending_event = HarmonyLinkEvent("2", "test", EVENT_STATE_PENDING, {})
            done_event = HarmonyLinkEvent("3", "test", EVENT_STATE_DONE, {})
            error_event = HarmonyLinkEvent("4", "test", EVENT_STATE_ERROR, {})
            
            assert new_event.status == EVENT_STATE_NEW
            assert pending_event.status == EVENT_STATE_PENDING
            assert done_event.status == EVENT_STATE_DONE
            assert error_event.status == EVENT_STATE_ERROR
    
    def test_event_with_complex_payload(self):
        """Test HarmonyLinkEvent with complex payload"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            
            complex_payload = {
                "action": "walk",
                "parameters": {
                    "speed": 1.5,
                    "direction": [0, 0, 1],
                    "duration": 3.0
                },
                "metadata": {
                    "timestamp": time.time(),
                    "source": "test"
                }
            }
            
            event = HarmonyLinkEvent("complex_1", "action", EVENT_STATE_NEW, complex_payload)
            
            assert event.payload["action"] == "walk"
            assert event.payload["parameters"]["speed"] == 1.5
            assert event.payload["metadata"]["source"] == "test"


class TestHarmonyClientModuleBase:
    """Test HarmonyClientModuleBase class functionality"""
    
    def test_module_base_initialization(self):
        """Test base module initialization"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import HarmonyClientModuleBase
            
            # Create a mock entity controller
            mock_connector = type('MockConnector', (), {})()
            mock_entity_controller = type('MockEntityController', (), {
                'connector': mock_connector
            })()
            
            module = HarmonyClientModuleBase(mock_entity_controller)
            
            assert module.entity_controller is mock_entity_controller
            assert module.backend_connector is mock_connector
            assert module.active == False
            assert module.ai_state is None
            assert module.countenance_state is None
            assert module.chara is None
    
    def test_module_activation_lifecycle(self):
        """Test module activation and deactivation lifecycle"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import HarmonyClientModuleBase
            
            # Create a mock entity controller with connector
            mock_connector = type('MockConnector', (), {
                'register_event_handler': lambda slf, handler: None,
                'unregister_event_handler': lambda slf, handler: None
            })()
            
            mock_entity_controller = type('MockEntityController', (), {
                'connector': mock_connector
            })()
            
            module = HarmonyClientModuleBase(mock_entity_controller)
            
            # Test activation
            module.activate()
            assert module.active == True
            assert module.is_active() == True
            
            # Test deactivation
            module.deactivate()
            assert module.active == False
            assert module.is_active() == False
    
    def test_ai_state_update(self):
        """Test AI state update functionality"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import HarmonyClientModuleBase
            
            mock_connector = type('MockConnector', (), {})()
            mock_entity_controller = type('MockEntityController', (), {
                'connector': mock_connector
            })()
            
            module = HarmonyClientModuleBase(mock_entity_controller)
            
            # Test AI state update
            ai_state_data = {
                "gender": "female",
                "name": "Kaji",
                "mood": "happy",
                "behaviour": "friendly",
                "persona": "cheerful",
                "status_message": "Ready to chat!"
            }
            
            module.update_ai_state(ai_state_data)
            
            assert module.ai_state is not None
            assert module.ai_state.gender == "female"
            assert module.ai_state.name == "Kaji"
            assert module.ai_state.mood == "happy"
            assert module.ai_state.behaviour == "friendly"
            assert module.ai_state.persona == "cheerful"
            assert module.ai_state.status_message == "Ready to chat!"
    
    def test_chara_update(self):
        """Test character update functionality"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import HarmonyClientModuleBase
            
            mock_connector = type('MockConnector', (), {})()
            mock_entity_controller = type('MockEntityController', (), {
                'connector': mock_connector
            })()
            
            module = HarmonyClientModuleBase(mock_entity_controller)
            
            # Test character update
            mock_chara = type('MockChara', (), {'name': 'test_character'})()
            module.update_chara(mock_chara)
            
            assert module.chara == mock_chara
    
    def test_handle_event(self):
        """Test event handling (base implementation)"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import HarmonyClientModuleBase, HarmonyLinkEvent, EVENT_STATE_NEW
            
            mock_connector = type('MockConnector', (), {})()
            mock_entity_controller = type('MockEntityController', (), {
                'connector': mock_connector
            })()
            
            module = HarmonyClientModuleBase(mock_entity_controller)
            
            # Test event handling (base implementation should return None)
            test_event = HarmonyLinkEvent("test_1", "test_event", EVENT_STATE_NEW, {"test": "data"})
            result = module.handle_event(test_event)
            
            # Base implementation returns None
            assert result is None


class TestAIState:
    """Test AIState class functionality"""
    
    def test_ai_state_creation_empty(self):
        """Test AIState creation with default values"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import AIState
            
            ai_state = AIState()
            
            assert ai_state.gender == ""
            assert ai_state.name == ""
            assert ai_state.mood == ""
            assert ai_state.behaviour == ""
            assert ai_state.persona == ""
            assert ai_state.status_message == ""
    
    def test_ai_state_creation_with_values(self):
        """Test AIState creation with specific values"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import AIState
            
            ai_state = AIState(
                gender="female",
                name="Kaji",
                mood="happy",
                behaviour="friendly",
                persona="cheerful",
                status_message="Ready!"
            )
            
            assert ai_state.gender == "female"
            assert ai_state.name == "Kaji"
            assert ai_state.mood == "happy"
            assert ai_state.behaviour == "friendly"
            assert ai_state.persona == "cheerful"
            assert ai_state.status_message == "Ready!"


class TestEventConstants:
    """Test event type constants and states"""
    
    def test_event_state_constants(self):
        """Test that event state constants are defined"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import (
                EVENT_STATE_DONE,
                EVENT_STATE_ERROR,
                EVENT_STATE_NEW,
                EVENT_STATE_PENDING
            )
            
            # Test constants exist and are strings
            assert EVENT_STATE_DONE == 'SUCCESS'
            assert EVENT_STATE_ERROR == 'ERROR'
            assert EVENT_STATE_NEW == 'NEW'
            assert EVENT_STATE_PENDING == 'PENDING'
    
    def test_event_type_constants(self):
        """Test that event type constants are defined"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import (
                EVENT_TYPE_INIT_ENTITY,
                EVENT_TYPE_ENVIRONMENT_LOADED,
                EVENT_TYPE_AI_ACTION,
                EVENT_TYPE_AI_SPEECH,
                EVENT_TYPE_USER_UTTERANCE,
                EVENT_TYPE_MOVEMENT_V1_PERFORM_ACTIONS
            )
            
            # Test some key event types exist and are strings
            assert isinstance(EVENT_TYPE_INIT_ENTITY, str)
            assert isinstance(EVENT_TYPE_ENVIRONMENT_LOADED, str)
            assert isinstance(EVENT_TYPE_AI_ACTION, str)
            assert isinstance(EVENT_TYPE_AI_SPEECH, str)
            assert isinstance(EVENT_TYPE_USER_UTTERANCE, str)
            assert isinstance(EVENT_TYPE_MOVEMENT_V1_PERFORM_ACTIONS, str)
    
    def test_utterance_type_constants(self):
        """Test that utterance type constants are defined"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import (
                UTTERANCE_COMBINED,
                UTTERANCE_VERBAL,
                UTTERANCE_NONVERBAL,
                UTTERANCE_NONVERBAL_DELAYED
            )
            
            # Test utterance types exist and are strings
            assert isinstance(UTTERANCE_COMBINED, str)
            assert isinstance(UTTERANCE_VERBAL, str)
            assert isinstance(UTTERANCE_NONVERBAL, str)
            assert isinstance(UTTERANCE_NONVERBAL_DELAYED, str)


class TestUtilityFunctions:
    """Test utility functions in common.py"""
    
    def test_get_actors_distance_function_exists(self):
        """Test that get_actors_distance function exists"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import get_actors_distance
            
            # Function should exist (even if incomplete in the source)
            assert callable(get_actors_distance)


class TestPerformance:
    """Test performance characteristics of common.py"""
    
    def test_event_creation_performance(self):
        """Test event creation performance"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            
            start_time = time.time()
            
            # Create many events
            events = []
            for i in range(1000):
                event = HarmonyLinkEvent("event_{}".format(i), "test", EVENT_STATE_NEW, {"index": i})
                events.append(event)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should create 1000 events in reasonable time
            assert execution_time < 1.0  # Less than 1 second
            assert len(events) == 1000
    
    def test_ai_state_creation_performance(self):
        """Test AI state creation performance"""
        with PluginTestEnvironment() as env:
            from harmony_modules.common import AIState
            
            start_time = time.time()
            
            # Create many AI states
            states = []
            for i in range(1000):
                state = AIState(
                    gender="test",
                    name="test_{}".format(i),
                    mood="happy",
                    behaviour="friendly",
                    persona="test",
                    status_message="Ready"
                )
                states.append(state)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should create 1000 AI states in reasonable time
            assert execution_time < 1.0  # Less than 1 second
            assert len(states) == 1000


if __name__ == "__main__":
    # Import the new test logging system
    from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
    
    # Create test instances
    test_classes = [
        TestHarmonyLinkEvent(),
        TestHarmonyClientModuleBase(),
        TestAIState(),
        TestEventConstants(),
        TestUtilityFunctions(),
        TestPerformance()
    ]
    
    # Run tests with clean output
    runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)
    runner.run_test_suite(test_classes, "unit tests for harmony_modules/common.py")
