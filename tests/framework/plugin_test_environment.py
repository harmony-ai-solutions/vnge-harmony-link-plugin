"""
Plugin Test Environment - Integrates all mock systems for comprehensive testing
"""
import sys
import os
import threading
import time
from contextlib import contextmanager

# Add the tests directory to Python path for imports
tests_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)

from framework.mocks.unity_mocks import *
from framework.mocks.system_mocks import *
from framework.mocks.vnge_mocks import *
from framework.mocks.game_mocks import *


class PluginTestEnvironment(object):
    """
    Comprehensive test environment that orchestrates all mock systems
    for testing the VNGE Harmony Link Plugin
    """
    
    def __init__(self, config=None):
        """Initialize the test environment with optional configuration"""
        self.config = config or {}
        self.mocks = {}
        self.is_initialized = False
        self.cleanup_callbacks = []
        self._lock = threading.Lock()
        
        # Default test configuration
        self.default_config = {
            'websocket_endpoint': 'ws://127.0.0.1:28080',
            'entities': ['kaji', 'user'],
            'user_entity': 'user',
            'scene_file': None,
            'warmup_time': 1.0,
            'enable_gui': True,
            'enable_timers': True,
            'animation_database': True,
            'mock_websocket_server': True
        }
        
        # Merge with provided config
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
    
    def setup(self):
        """Set up the complete mock environment"""
        with self._lock:
            if self.is_initialized:
                return
            
            print("Setting up Plugin Test Environment...")
            
            # Initialize Unity mocks
            self._setup_unity_mocks()
            
            # Initialize System.Net mocks
            self._setup_system_mocks()
            
            # Initialize VNGE mocks
            self._setup_vnge_mocks()
            
            # Initialize Game environment mocks
            self._setup_game_mocks()
            
            # Set up module path injection
            self._setup_module_injection()
            
            self.is_initialized = True
            print("Plugin Test Environment setup complete")
    
    def _setup_unity_mocks(self):
        """Initialize Unity Engine mock system"""
        print("  - Setting up Unity mocks...")
        
        # Create mock instances
        self.mocks['unity_input'] = MockInput()
        self.mocks['unity_gui'] = MockGUI()
        self.mocks['unity_screen'] = MockScreen()
        
        # Configure GUI if enabled - MockGUI doesn't need special configuration
        if self.config.get('enable_gui', True):
            pass  # MockGUI is ready to use by default
        
        # Set up cleanup
        self.cleanup_callbacks.append(self._cleanup_unity_mocks)
    
    def _setup_system_mocks(self):
        """Initialize System.Net mock system"""
        print("  - Setting up System.Net mocks...")
        
        # Create WebSocket client mock
        self.mocks['websocket_client'] = MockClientWebSocket()
        
        # Add WebSocketState enum to the mock for easy access
        self.mocks['websocket_client'].WebSocketState = MockWebSocketState
        
        # Configure WebSocket endpoint - store for later use
        endpoint = self.config.get('websocket_endpoint', 'ws://127.0.0.1:28080')
        # MockClientWebSocket doesn't need endpoint configuration for testing
        
        # Set up cleanup
        self.cleanup_callbacks.append(self._cleanup_system_mocks)
    
    def _setup_vnge_mocks(self):
        """Initialize VNGE engine mock system"""
        print("  - Setting up VNGE mocks...")
        
        # Create Studio.Info mock with animation database
        self.mocks['studio_info'] = MockStudioInfo()
        # Animation database is loaded automatically in MockStudioInfo.__init__
        
        # Create character actors for configured entities
        entities = self.config.get('entities', ['kaji', 'user'])
        self.mocks['character_actors'] = {}
        
        for entity_id in entities:
            actor = MockCharacterActor(entity_id)
            self.mocks['character_actors'][entity_id] = actor
            print("    - Created character actor: {}".format(entity_id))
        
        # Set up cleanup
        self.cleanup_callbacks.append(self._cleanup_vnge_mocks)
    
    def _setup_game_mocks(self):
        """Initialize game environment mock system"""
        print("  - Setting up Game environment mocks...")
        
        # Create game instance
        entities = self.config.get('entities', ['kaji', 'user'])
        self.mocks['game'] = MockGame()
        
        # Add mock actors for configured entities
        for entity_id in entities:
            self.mocks['game'].add_mock_actor(entity_id)
        
        # Timers are enabled by default in MockGame
        
        # Set up cleanup
        self.cleanup_callbacks.append(self._cleanup_game_mocks)
    
    def _setup_module_injection(self):
        """Set up module path injection to prioritize mocks"""
        print("  - Setting up module injection...")
        
        # Use setup methods from all mock modules for consistency
        setup_system_mocks()
        setup_unity_mocks()
        setup_vnge_mocks()
        setup_game_mocks()
    
    def teardown(self):
        """Clean up the test environment"""
        with self._lock:
            if not self.is_initialized:
                return
            
            print("Tearing down Plugin Test Environment...")
            
            # Run cleanup callbacks in reverse order
            for cleanup_callback in reversed(self.cleanup_callbacks):
                try:
                    cleanup_callback()
                except AttributeError as e:
                    # Handle cases where lists don't have clear() method in older Python
                    if "'list' object has no attribute 'clear'" in str(e):
                        pass  # Ignore this specific error
                    else:
                        print("Warning: Cleanup callback failed: {}".format(e))
                except Exception as e:
                    print("Warning: Cleanup callback failed: {}".format(e))
            
            # Restore original modules
            # Since we're using setup functions that handle sys.modules directly,
            # we don't need to manually restore modules in this simplified approach
            # The setup functions manage their own module registration
            pass
            
            self.is_initialized = False
            print("Plugin Test Environment teardown complete")
    
    def _cleanup_unity_mocks(self):
        """Clean up Unity mocks"""
        if 'unity_gui' in self.mocks:
            self.mocks['unity_gui'].reset_state()
        if 'unity_input' in self.mocks:
            self.mocks['unity_input'].reset_state()
    
    def _cleanup_system_mocks(self):
        """Clean up System.Net mocks"""
        if 'websocket_client' in self.mocks:
            self.mocks['websocket_client'].reset_for_test()
    
    def _cleanup_vnge_mocks(self):
        """Clean up VNGE mocks"""
        if 'character_actors' in self.mocks:
            for actor in self.mocks['character_actors'].values():
                actor.reset_for_test()
    
    def _cleanup_game_mocks(self):
        """Clean up game environment mocks"""
        if 'game' in self.mocks:
            # MockGame doesn't have cleanup method, just clear scene
            self.mocks['game'].clear_scene()
    
    def __enter__(self):
        """Context manager entry"""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.teardown()
        return False
    
    @contextmanager
    def plugin_context(self):
        """Context manager for plugin testing"""
        self.setup()
        try:
            yield self
        finally:
            self.teardown()
    
    def get_mock(self, mock_name):
        """Get a specific mock object by name"""
        return self.mocks.get(mock_name)
    
    def get_character_actor(self, entity_id):
        """Get a character actor mock by entity ID"""
        actors = self.mocks.get('character_actors', {})
        return actors.get(entity_id)
    
    def simulate_plugin_startup(self, warmup_time=None):
        """Simulate plugin startup sequence"""
        if warmup_time is None:
            warmup_time = self.config.get('warmup_time', 1.0)
        
        print("Simulating plugin startup...")
        
        # Simulate initialization delay
        time.sleep(warmup_time)
        
        # Initialize entities
        entities = self.config.get('entities', ['kaji', 'user'])
        for entity_id in entities:
            actor = self.get_character_actor(entity_id)
            if actor:
                # MockCharacterActor doesn't have initialize_for_test method
                # Just mark as initialized for testing
                actor.is_initialized = True
                print("  - Initialized entity: {}".format(entity_id))
        
        print("Plugin startup simulation complete")
    
    def create_test_action_graph(self, actions=None, targets=None, graph_id=None):
        """Create a test ActionGraph structure"""
        if actions is None:
            actions = ['walk', 'wave']
        if targets is None:
            targets = self.config.get('entities', ['kaji'])
        if graph_id is None:
            graph_id = "test_graph_{}".format(int(time.time()))
        
        return {
            'id': graph_id,
            'version': 'v1',
            'actions': [
                {
                    'type': action,
                    'target': target,
                    'parameters': {}
                }
                for action in actions
                for target in targets
            ]
        }
    
    def send_mock_harmony_event(self, event_type, payload, target_entity=None):
        """Send a mock event from Harmony Link to the plugin"""
        websocket_client = self.get_mock('websocket_client')
        if websocket_client:
            event_data = {
                'type': event_type,
                'payload': payload,
                'target': target_entity,
                'timestamp': time.time()
            }
            websocket_client.simulate_received_message(event_data)
            return True
        return False
    
    def wait_for_animation_execution(self, entity_id, animation_name, timeout=5.0):
        """Wait for a specific animation to be executed"""
        actor = self.get_character_actor(entity_id)
        if not actor:
            return False
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if animation was executed by looking at animation history
            for anim_record in actor.animation_history:
                if animation_name in anim_record.get('animation', ''):
                    return True
            time.sleep(0.1)
        
        return False
    
    def get_execution_metrics(self):
        """Get plugin execution metrics"""
        metrics = {
            'websocket_messages_sent': 0,
            'websocket_messages_received': 0,
            'animations_executed': 0,
            'gui_interactions': 0,
            'entities_initialized': 0
        }
        
        # Collect metrics from mocks
        websocket_client = self.get_mock('websocket_client')
        if websocket_client:
            metrics['websocket_messages_sent'] = len(websocket_client.sent_messages)
            metrics['websocket_messages_received'] = len(websocket_client.received_messages)
        
        if 'character_actors' in self.mocks:
            for actor in self.mocks['character_actors'].values():
                metrics['animations_executed'] += len(actor.animation_history)
                if hasattr(actor, 'is_initialized') and actor.is_initialized:
                    metrics['entities_initialized'] += 1
        
        unity_gui = self.get_mock('unity_gui')
        if unity_gui:
            metrics['gui_interactions'] = len(unity_gui.interaction_history)
        
        return metrics


# Convenience functions for test setup
def create_test_environment(config=None):
    """Create a new test environment instance"""
    return PluginTestEnvironment(config)


def setup_basic_test_environment():
    """Set up a basic test environment with default configuration"""
    env = PluginTestEnvironment()
    env.setup()
    return env


def setup_integration_test_environment(entities=None, websocket_endpoint=None):
    """Set up an integration test environment with specified entities"""
    config = {}
    if entities:
        config['entities'] = entities
    if websocket_endpoint:
        config['websocket_endpoint'] = websocket_endpoint
    
    env = PluginTestEnvironment(config)
    env.setup()
    return env
