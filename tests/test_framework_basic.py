# -*- coding: utf-8 -*-
"""
Basic test to verify the testing framework works with IronPython
"""
import sys
import os

# Add the tests directory to Python path for imports
tests_dir = os.path.dirname(os.path.abspath(__file__))
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)

from framework.plugin_test_environment import PluginTestEnvironment


def test_plugin_environment_setup():
    """Test that the plugin environment can be set up and torn down"""
    print("Testing PluginTestEnvironment setup...")
    
    # Create test environment
    env = PluginTestEnvironment()
    
    # Test setup
    env.setup()
    assert env.is_initialized, "Environment should be initialized"
    
    # Test that mocks are created
    assert 'unity_input' in env.mocks, "Unity Input mock should be created"
    assert 'unity_gui' in env.mocks, "Unity GUI mock should be created"
    assert 'websocket_client' in env.mocks, "WebSocket client mock should be created"
    assert 'studio_info' in env.mocks, "Studio Info mock should be created"
    assert 'character_actors' in env.mocks, "Character actors should be created"
    assert 'game' in env.mocks, "Game mock should be created"
    
    # Test character actors
    kaji_actor = env.get_character_actor('kaji')
    assert kaji_actor is not None, "Kaji actor should be created"
    assert kaji_actor.entity_id == 'kaji', "Actor should have correct entity ID"
    
    user_actor = env.get_character_actor('user')
    assert user_actor is not None, "User actor should be created"
    assert user_actor.entity_id == 'user', "Actor should have correct entity ID"
    
    # Test teardown
    env.teardown()
    assert not env.is_initialized, "Environment should not be initialized after teardown"
    
    print("+ PluginTestEnvironment setup test passed")


def test_mock_character_animation():
    """Test that mock character animation works"""
    print("Testing mock character animation...")
    
    env = PluginTestEnvironment()
    env.setup()
    
    try:
        # Get character actor
        kaji_actor = env.get_character_actor('kaji')
        assert kaji_actor is not None, "Kaji actor should exist"
        
        # Test animation
        kaji_actor.animate2(0, 1, 0, 1.0)  # Walk animation
        
        # Check animation was recorded
        assert len(kaji_actor.animation_history) == 1, "Animation should be recorded"
        
        last_animation = kaji_actor.get_last_animation()
        assert last_animation is not None, "Last animation should exist"
        assert last_animation['group'] == 0, "Animation group should be correct"
        assert last_animation['category'] == 1, "Animation category should be correct"
        assert last_animation['no'] == 0, "Animation number should be correct"
        
        print("+ Mock character animation test passed")
        
    finally:
        env.teardown()


def test_mock_websocket_communication():
    """Test that mock WebSocket communication works"""
    print("Testing mock WebSocket communication...")
    
    env = PluginTestEnvironment()
    env.setup()
    
    try:
        # Get WebSocket client
        websocket_client = env.get_mock('websocket_client')
        assert websocket_client is not None, "WebSocket client should exist"
        
        # Test sending a mock message
        test_message = '{"type": "test", "data": "hello"}'
        websocket_client.simulate_received_message(test_message)
        
        # Test that message was queued
        assert len(websocket_client.message_queue) == 1, "Message should be queued"
        
        print("+ Mock WebSocket communication test passed")
        
    finally:
        env.teardown()


def test_context_manager():
    """Test that the context manager works correctly"""
    print("Testing context manager...")
    
    with PluginTestEnvironment().plugin_context() as env:
        assert env.is_initialized, "Environment should be initialized in context"
        
        # Test basic functionality
        kaji_actor = env.get_character_actor('kaji')
        assert kaji_actor is not None, "Actor should be available in context"
    
    # Environment should be cleaned up automatically
    assert not env.is_initialized, "Environment should be cleaned up after context"
    
    print("+ Context manager test passed")


def test_action_graph_creation():
    """Test ActionGraph creation"""
    print("Testing ActionGraph creation...")
    
    env = PluginTestEnvironment()
    env.setup()
    
    try:
        # Create test ActionGraph
        action_graph = env.create_test_action_graph(
            actions=['walk', 'wave'],
            targets=['kaji'],
            graph_id='test_graph_123'
        )
        
        assert action_graph['id'] == 'test_graph_123', "Graph ID should be correct"
        assert action_graph['version'] == 'v1', "Graph version should be correct"
        assert len(action_graph['actions']) == 2, "Should have 2 actions"
        
        # Check actions
        walk_action = action_graph['actions'][0]
        assert walk_action['type'] == 'walk', "First action should be walk"
        assert walk_action['target'] == 'kaji', "Action target should be kaji"
        
        wave_action = action_graph['actions'][1]
        assert wave_action['type'] == 'wave', "Second action should be wave"
        assert wave_action['target'] == 'kaji', "Action target should be kaji"
        
        print("+ ActionGraph creation test passed")
        
    finally:
        env.teardown()


def test_execution_metrics():
    """Test execution metrics collection"""
    print("Testing execution metrics...")
    
    env = PluginTestEnvironment()
    env.setup()
    
    try:
        # Perform some actions
        kaji_actor = env.get_character_actor('kaji')
        kaji_actor.animate2(0, 1, 0, 1.0)  # Walk
        kaji_actor.animate2(1, 0, 0, 1.0)  # Wave
        
        # Mark entities as initialized
        kaji_actor.is_initialized = True
        user_actor = env.get_character_actor('user')
        user_actor.is_initialized = True
        
        # Get metrics
        metrics = env.get_execution_metrics()
        
        assert metrics['animations_executed'] == 2, "Should have 2 animations executed"
        assert metrics['entities_initialized'] == 2, "Should have 2 entities initialized"
        
        print("+ Execution metrics test passed")
        
    finally:
        env.teardown()


def run_all_tests():
    """Run all basic framework tests"""
    print("Running basic framework tests...")
    print("=" * 50)
    
    try:
        test_plugin_environment_setup()
        test_mock_character_animation()
        test_mock_websocket_communication()
        test_context_manager()
        test_action_graph_creation()
        test_execution_metrics()
        
        print("=" * 50)
        print("+ All basic framework tests passed!")
        return True
        
    except Exception as e:
        print("=" * 50)
        print("- Test failed with error: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
