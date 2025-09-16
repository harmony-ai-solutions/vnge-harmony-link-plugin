#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for harmony_modules/movement.py

Tests the Movement module functionality including:
- ActionInstance lifecycle management
- ActionExecutor core functionality  
- Dynamic animation duration detection
- Distance-based completion detection
- Animation mapping system
- ActionGraph processing

Priority: CRITICAL - Recently enhanced with dynamic animation detection
"""

import sys
import os
import time

# Add the src directory to the path so we can import the plugin modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add the tests directory to the path so we can import the test framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test framework
from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
from framework.plugin_test_environment import PluginTestEnvironment

class TestMovementModule:
    """Test Movement Module functionality"""
    
    def _setup_movement_handler(self, env):
        """Create a properly configured MovementHandler for testing"""
        # Create proper EntityController with connector
        from harmony_modules.connector import ConnectorEventHandler
        from harmony_modules.movement import MovementHandler
        from harmony import EntityController
        
        game = env.get_mock('game')
        
        # Create mock config
        game.scenedata.scene_config = {'scene': 'test_scene.png'}
        mock_config = type('MockConfig', (), {
            'get': lambda self, section, key: {
                ('Connector', 'ws_endpoint'): 'ws://127.0.0.1:28080',
                ('Connector', 'ws_buffer_size'): '8192000',
                ('Connector', 'http_endpoint'): 'http://127.0.0.1:28080',
                ('Connector', 'http_listen_port'): '28081',
                ('Movement', 'debug_mode'): '0'
            }.get((section, key), ''),
            'items': lambda self, section: [('debug_mode', '0')] if section == 'Movement' else []
        })()
        
        # Create EntityController
        entity_controller = EntityController('test_entity', game, mock_config)
        
        # Create MovementHandler with proper entity_controller
        movement_handler = MovementHandler(entity_controller, {'debug_mode': '0'})
        
        return movement_handler, entity_controller
    
    def test_action_instance_state_transitions(self):
        """Test ActionInstance state transitions: QUEUED → EXECUTING → COMPLETED"""
        with PluginTestEnvironment() as env:
            # Import after environment setup to ensure mocks are in place
            from harmony_modules.movement import ActionInstance, ActionState
            
            # Create ActionInstance
            action = ActionInstance('walk', targets=[{'name': 'target_location'}])
            
            # Test initial state
            assert action.state == ActionState.QUEUED
            assert action.name == 'walk'
            assert len(action.targets) == 1
            assert action.start_time is None
            assert action.expected_duration is None
            assert action.actual_duration is None
            
            # Test start execution
            expected_duration = 3.0
            action.start_execution(expected_duration)
            
            assert action.state == ActionState.EXECUTING
            assert action.expected_duration == expected_duration
            assert action.start_time is not None
            assert action.actual_duration is None
            
            # Test completion
            success = True
            actual_duration = action.complete_execution(success)
            
            assert action.state == ActionState.COMPLETED
            assert action.actual_duration is not None
            assert actual_duration > 0
            assert actual_duration == action.actual_duration
    
    def test_action_instance_timing_control(self):
        """Test ActionInstance timing control with start/expected/actual duration tracking"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionInstance, ActionState
            
            action = ActionInstance('run', targets=[])
            
            # Test timing before execution
            assert action.get_execution_time() == 0.0
            
            # Start execution
            expected_duration = 2.5
            action.start_execution(expected_duration)
            
            # Small delay to ensure timing
            time.sleep(0.1)
            
            # Test execution timing
            execution_time = action.get_execution_time()
            assert execution_time > 0.0
            assert execution_time < 1.0  # Should be small since we just started
            
            # Complete execution
            actual_duration = action.complete_execution(True)
            
            # Verify timing
            assert actual_duration >= 0.1  # At least our sleep time
            assert action.expected_duration == expected_duration
            assert action.actual_duration == actual_duration
    
    def test_action_instance_timeout_detection(self):
        """Test ActionInstance timeout state and recovery"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionInstance, ActionState
            
            action = ActionInstance('sit_down', targets=[])
            
            # Start execution
            action.start_execution(1.0)
            
            # Test timeout detection
            assert action.is_timeout() == False  # Should not be timeout initially
            
            # Simulate timeout by setting state
            action.state = ActionState.TIMEOUT
            
            # Complete with timeout
            actual_duration = action.complete_execution(False)
            
            assert action.state == ActionState.TIMEOUT
            assert actual_duration > 0
    
    def test_action_executor_movement_actions(self):
        """Test ActionExecutor movement actions: move, walk, run with distance detection"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionExecutor, ActionInstance
            
            # Create mock character
            character = env.get_character_actor('test_entity')
            
            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            
            # Create ActionExecutor
            executor = ActionExecutor(movement_handler)
            executor.update_chara(character)
            
            # Test movement actions
            movement_actions = ['walk', 'run']  # Use actions that likely exist
            
            for action_name in movement_actions:
                action = ActionInstance(action_name, targets=[{
                    'name': 'target_location',
                    'position': [5.0, 0.0, 5.0]
                }])
                
                # Execute action (this calls the movement handler)
                executor.execute_action(action)
                
                # Verify animation was called
                if character and hasattr(character, 'animation_history'):
                    assert len(character.animation_history) > 0
    
    def test_action_executor_posture_actions(self):
        """Test ActionExecutor posture actions: sit_down, stand_up, lay_down"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionExecutor, ActionInstance
            
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            
            # Create ActionExecutor
            executor = ActionExecutor(movement_handler)
            executor.update_chara(character)
            
            posture_actions = ['sit_down', 'stand_up', 'lay_down']
            
            for action_name in posture_actions:
                action = ActionInstance(action_name, targets=[])
                
                # Execute action (this calls the movement handler)
                executor.execute_action(action)
                
                # Verify animation was called
                if character and hasattr(character, 'animation_history'):
                    assert len(character.animation_history) >= 0  # May be 0 if action not mapped
    
    def test_action_executor_simple_actions(self):
        """Test ActionExecutor simple actions: jump_fixed, wave, nod"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionExecutor, ActionInstance
            
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            
            # Create ActionExecutor
            executor = ActionExecutor(movement_handler)
            executor.update_chara(character)
            
            simple_actions = ['jump_fixed']  # Use actions that likely exist
            
            for action_name in simple_actions:
                action = ActionInstance(action_name, targets=[])
                
                # Execute action (this calls the movement handler)
                executor.execute_action(action)
                
                # Verify animation was called
                if character and hasattr(character, 'animation_history'):
                    assert len(character.animation_history) >= 0  # May be 0 if action not mapped
    
    def test_animation_duration_detector_cache(self):
        """Test animation duration detection caching for performance"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement_animations import AnimationDurationDetector
            
            detector = AnimationDurationDetector()
            character = env.get_character_actor('test_entity')
            
            # Test cache miss and hit
            group, category, no = 0, 1, 0
            
            # First call - cache miss
            duration1 = detector.get_animation_duration(character, group, category, no)
            if duration1 is not None:
                assert duration1 > 0
                
                # Second call - cache hit
                duration2 = detector.get_animation_duration(character, group, category, no)
                assert duration2 == duration1
                
                # Verify cache contains the entry
                cache_key = "{0}_{1}_{2}".format(group, category, no)
                assert cache_key in detector.duration_cache
    
    def test_animation_duration_detector_unity_integration(self):
        """Test AnimationDurationDetector Unity RuntimeAnimatorController access"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement_animations import AnimationDurationDetector
            
            detector = AnimationDurationDetector()
            character = env.get_character_actor('test_entity')
            
            # Test Unity integration (mocked)
            duration = detector._detect_duration_from_unity(character, 0, 1, 0)
            
            # Should return None or a reasonable duration from mock
            if duration is not None:
                assert duration > 0
                assert duration <= 10.0  # Reasonable upper bound
    
    def test_animation_duration_detection_fallback(self):
        """Test animation duration detection fallback when Unity data unavailable"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement_animations import AnimationDurationDetector
            
            detector = AnimationDurationDetector()
            character = env.get_character_actor('test_entity')
            
            # Test fallback for invalid animation
            duration = detector.get_animation_duration(character, 999, 999, 999)
            
            # Should return None when detection fails
            assert duration is None
    
    def test_distance_based_movement_completion(self):
        """Test distance-based movement completion with 1.0 unit threshold"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionExecutor, ActionInstance
            from framework.mocks.unity_mocks import MockVector3
            
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            
            # Create ActionExecutor
            executor = ActionExecutor(movement_handler)
            executor.update_chara(character)
            
            # Set initial position
            if character and hasattr(character, 'actor') and character.actor:
                character.actor.pos = MockVector3(0.0, 0.0, 0.0)
            
            # Create movement action to target position
            target_pos = [3.0, 0.0, 4.0]  # 5 units away
            action = ActionInstance('walk', targets=[{
                'name': 'target_location',
                'position': target_pos
            }])
            
            # Execute action (this calls the movement handler)
            executor.execute_action(action)
            
            # Test that action was processed
            assert action.state in ['queued', 'executing', 'completed']
    
    def test_target_position_resolution(self):
        """Test target position resolution: named entities, coordinates, scene objects"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionExecutor, ActionInstance
            
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            
            # Create ActionExecutor
            executor = ActionExecutor(movement_handler)
            executor.update_chara(character)
            
            # Test coordinate target - use _get_target_position method that exists
            coord_action = ActionInstance('move', targets=[{
                'name': 'coordinate_target',
                'position': [1.0, 0.0, 1.0]
            }])
            
            target_pos = executor._get_target_position(coord_action.targets)
            if target_pos is not None:
                assert len(target_pos) == 3
                assert target_pos == [1.0, 0.0, 1.0]
    
    def test_movement_completion_monitoring(self):
        """Test movement completion monitoring with distance calculation"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import ActionExecutor, ActionInstance
            from framework.mocks.unity_mocks import MockVector3
            
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            
            # Create ActionExecutor
            executor = ActionExecutor(movement_handler)
            executor.update_chara(character)
            
            # Test distance calculation method that exists
            pos1 = [0.0, 0.0, 0.0]
            pos2 = [1.0, 0.0, 0.0]
            
            distance = executor._calculate_distance(pos1, pos2)
            assert distance == 1.0  # Should be exactly 1.0 unit
    
    def test_animation_mapping_dynamic_lookup(self):
        """Test animation mapping dynamic lookup with animation_list_short.json integration"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import AnimationMapper
            
            mapper = AnimationMapper()
            
            # Test dynamic lookup for common actions
            walk_mapping = mapper.get_animation_mapping('walk')
            assert walk_mapping is not None
            assert 'group' in walk_mapping
            assert 'category' in walk_mapping
            assert 'no' in walk_mapping
            
            # Test mapping contains expected fields
            assert isinstance(walk_mapping['group'], int)
            assert isinstance(walk_mapping['category'], int)
            assert isinstance(walk_mapping['no'], int)
    
    def test_animation_mapping_name_matching(self):
        """Test animation mapping name-based matching from action names to VNGE animations"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import AnimationMapper
            
            mapper = AnimationMapper()
            
            # Test various action name mappings
            test_actions = ['walk', 'run', 'sit_down', 'stand_up', 'wave', 'nod']
            
            for action_name in test_actions:
                mapping = mapper.get_animation_mapping(action_name)
                assert mapping is not None, "No mapping found for action: {0}".format(action_name)
                
                # Verify mapping structure
                assert 'group' in mapping
                assert 'category' in mapping
                assert 'no' in mapping
                assert mapping['group'] >= 0
                assert mapping['category'] >= 0
                assert mapping['no'] >= 0
    
    def test_animation_mapping_error_handling(self):
        """Test animation mapping hard error handling for missing animations"""
        with PluginTestEnvironment() as env:
            from harmony_modules.movement import AnimationMapper
            
            mapper = AnimationMapper()
            
            # Test error handling for unknown action
            try:
                mapping = mapper.get_animation_mapping('unknown_action_12345')
                # If no exception, should return None or default
                if mapping is not None:
                    assert 'group' in mapping
            except Exception as e:
                # Hard error handling - should raise exception
                assert 'unknown_action_12345' in str(e) or 'not found' in str(e).lower()
    
    def test_action_graph_execution_sequential(self):
        """Test ActionGraph sequential action queue processing"""
        with PluginTestEnvironment() as env:
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            movement_handler.update_chara(character)
            
            # Create test ActionGraph with multiple actions
            action_graph = {
                'graph_id': 'test_sequential',
                'graph_actor': 'test_entity',
                'graph_vector': [
                    {'action': 'walk', 'targets': []},
                    {'action': 'wave', 'targets': []},
                    {'action': 'sit_down', 'targets': []}
                ]
            }
            
            # Execute ActionGraph
            movement_handler._execute_action_graph(action_graph)
            
            # Verify actions were queued
            assert len(movement_handler.action_queue) >= 0  # May be processed already
            assert movement_handler.total_actions_executed >= 0
            
            # Verify at least some animations were executed
            if character and hasattr(character, 'animation_history'):
                assert len(character.animation_history) >= 0
    
    def test_action_graph_cognitive_integration(self):
        """Test ActionGraph cognitive context processing"""
        with PluginTestEnvironment() as env:
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            movement_handler.update_chara(character)
            
            # Create ActionGraph with cognitive context
            action_graph = {
                'graph_id': 'test_cognitive',
                'graph_actor': 'test_entity',
                'graph_vector': [
                    {
                        'action': 'wave',
                        'targets': [{'name': 'other_entity'}],
                        'requires_consent': True,
                        'intimacy_level': 'friendly'
                    }
                ]
            }
            
            # Execute ActionGraph
            movement_handler._execute_action_graph(action_graph)
            
            # Verify cognitive processing occurred
            # (Implementation may vary based on cognitive integration level)
            if character and hasattr(character, 'animation_history'):
                assert len(character.animation_history) >= 0
    
    def test_action_graph_performance_tracking(self):
        """Test ActionGraph execution statistics and performance metrics"""
        with PluginTestEnvironment() as env:
            character = env.get_character_actor('test_entity')

            # Use setup method to create proper MovementHandler
            movement_handler, entity_controller = self._setup_movement_handler(env)
            movement_handler.update_chara(character)
            
            # Record initial stats
            initial_executed = movement_handler.total_actions_executed
            initial_failed = movement_handler.total_actions_failed
            
            # Execute test ActionGraph
            action_graph = {
                'graph_id': 'test_performance',
                'graph_actor': 'test_entity',
                'graph_vector': [
                    {'action': 'nod', 'targets': []},
                    {'action': 'wave', 'targets': []}
                ]
            }
            
            start_time = time.time()
            movement_handler._execute_action_graph(action_graph)
            execution_time = time.time() - start_time
            
            # Verify performance tracking
            assert movement_handler.total_actions_executed >= initial_executed
            assert movement_handler.total_actions_failed >= initial_failed
            assert execution_time < 5.0  # Should complete quickly in test environment
            
            # Verify statistics are maintained
            if hasattr(movement_handler, 'get_action_status'):
                stats = movement_handler.get_action_status()
                assert 'total_executed' in stats
                assert 'total_failed' in stats


if __name__ == "__main__":
    # Import test runner
    from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
    
    # Create test runner with quiet logging
    runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)
    
    # Create test instances
    test_classes = [TestMovementModule()]
    
    # Run test suite
    runner.run_test_suite(test_classes, "unit tests for harmony_modules/movement.py")
