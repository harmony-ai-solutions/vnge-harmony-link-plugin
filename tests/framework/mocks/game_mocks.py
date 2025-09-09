"""
Game Environment Mock Classes for VNGE Harmony Link Plugin Testing

This module provides comprehensive mock implementations of the game environment
and related classes that are used by the plugin, enabling testing without game dependencies.
"""

import sys
import time
import threading
from collections import defaultdict, deque


class MockGame:
    """Mock implementation of the game object passed to plugin functions"""
    
    def __init__(self):
        # Scene management
        self.sceneDir = "harmony/test_engine/"
        self.scenedata = MockSceneData()
        
        # UI state
        self.current_text = ""
        self.current_buttons = []
        self.current_button_actions = []
        
        # Timer system
        self.timers = []
        self.timer_id_counter = 0
        self._timer_lock = threading.Lock()
        
        # Window system
        self.windows = {}
        self.window_id_counter = 0
        
        # Event system
        self.event_listeners = defaultdict(list)
        
        # Blocking message system
        self.blocking_message = None
        self.blocking_message_visible = False
        
        # Test state
        self._setup_dialog = None
        self._harmony_startup_aborted = False
        self._harmony_user_entity = None
        
        # Scene loading
        self.loaded_scenes = []
        self.current_scene = None
        
        # Camera system
        self.current_camera = 0
        
        # Lip sync
        self.lip_sync_active = False
    
    def set_text(self, text_id, text):
        """Set text display"""
        self.current_text = text
        print("Game text set: {}".format(text))
    
    def set_buttons(self, button_texts, button_actions):
        """Set button display and actions"""
        self.current_buttons = button_texts or []
        self.current_button_actions = button_actions or []
        print("Game buttons set: {}".format(self.current_buttons))
    
    def set_timer(self, delay_seconds, callback_func):
        """Set a timer to call a function after delay"""
        with self._timer_lock:
            timer_id = self.timer_id_counter
            self.timer_id_counter += 1
            
            def timer_callback():
                time.sleep(delay_seconds)
                try:
                    callback_func(self)
                except Exception as e:
                    print("Timer callback error: {}".format(e))
                finally:
                    # Remove timer from list
                    with self._timer_lock:
                        self.timers = [t for t in self.timers if t['id'] != timer_id]
            
            timer_info = {
                'id': timer_id,
                'delay': delay_seconds,
                'callback': callback_func,
                'thread': threading.Thread(target=timer_callback, daemon=True)
            }
            
            self.timers.append(timer_info)
            timer_info['thread'].start()
            
            return timer_id
    
    def cancel_timer(self, timer_id):
        """Cancel a timer (limited functionality in mock)"""
        with self._timer_lock:
            self.timers = [t for t in self.timers if t['id'] != timer_id]
    
    def get_active_timer_count(self):
        """Get number of active timers (for testing)"""
        with self._timer_lock:
            return len(self.timers)
    
    def wait_for_timers(self, timeout=10.0):
        """Wait for all timers to complete (for testing)"""
        start_time = time.time()
        while self.get_active_timer_count() > 0 and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        return self.get_active_timer_count() == 0
    
    def load_scene(self, scene_name):
        """Load a scene"""
        self.loaded_scenes.append(scene_name)
        self.current_scene = scene_name
        print("Scene loaded: {}".format(scene_name))
    
    def get_scene_dir(self):
        """Get scene directory"""
        return "test_scenes/"
    
    def scenef_register_actorsprops(self):
        """Register actors and props in scene"""
        print("Registered actors and props")
    
    def scenef_get_all_actors(self):
        """Get all actors in scene"""
        return self.scenedata.actors.copy()
    
    def scenef_get_actor(self, entity_id):
        """Get specific actor by entity ID"""
        return self.scenedata.actors.get(entity_id)
    
    def scenef_get_all_props(self):
        """Get all props in scene"""
        return list(self.scenedata.props.keys())
    
    def scenef_get_prop(self, prop_id):
        """Get specific prop by ID"""
        return self.scenedata.props.get(prop_id)
    
    def new_extra_window_skin(self, skin):
        """Create new extra window with skin"""
        window_id = self.window_id_counter
        self.window_id_counter += 1
        
        window = MockWindow(window_id, skin)
        self.windows[window_id] = window
        
        print("Created window {}".format(window_id))
        return window_id
    
    def get_extra_window(self, window_id):
        """Get extra window by ID"""
        return self.windows.get(window_id)
    
    def close_extra_window(self, window_id):
        """Close extra window"""
        if window_id in self.windows:
            del self.windows[window_id]
            print("Closed window {}".format(window_id))
    
    def event_reg_listener(self, event_name, callback):
        """Register event listener"""
        self.event_listeners[event_name].append(callback)
    
    def event_unreg_listener(self, event_name, callback):
        """Unregister event listener"""
        if callback in self.event_listeners[event_name]:
            self.event_listeners[event_name].remove(callback)
    
    def trigger_event(self, event_name, *args):
        """Trigger event (for testing)"""
        for callback in self.event_listeners[event_name]:
            try:
                callback(self, event_name, *args)
            except Exception as e:
                print("Event callback error: {}".format(e))
    
    def show_blocking_message(self, message):
        """Show blocking message"""
        self.blocking_message = message
        self.blocking_message_visible = True
        print("Blocking message: {}".format(message))
    
    def hide_blocking_message(self):
        """Hide blocking message"""
        self.blocking_message_visible = False
        print("Blocking message hidden")
    
    def to_camera(self, camera_id):
        """Move to camera instantly"""
        self.current_camera = camera_id
        print("Moved to camera {}".format(camera_id))
    
    def anim_to_camera_num(self, duration, camera_id, style="linear"):
        """Animate to camera"""
        self.current_camera = camera_id
        print("Animating to camera {} over {}s with style {}".format(camera_id, duration, style))
    
    def fake_lipsync_stop(self):
        """Stop fake lip sync"""
        self.lip_sync_active = False
        print("Lip sync stopped")
    
    def return_to_start_screen_clear(self):
        """Return to start screen"""
        print("Returning to start screen")
    
    # Test helper methods
    def simulate_button_click(self, button_index):
        """Simulate clicking a button (for testing)"""
        if 0 <= button_index < len(self.current_button_actions):
            action = self.current_button_actions[button_index]
            if callable(action):
                action(self)
            elif isinstance(action, list) and len(action) > 0 and callable(action[0]):
                action[0](self)
    
    def add_mock_actor(self, entity_id, actor=None):
        """Add mock actor to scene (for testing)"""
        if actor is None:
            from framework.mocks.vnge_mocks import create_mock_character_actor
            actor = create_mock_character_actor(entity_id)
        self.scenedata.actors[entity_id] = actor
        return actor
    
    def add_mock_prop(self, prop_id, prop_object=None):
        """Add mock prop to scene (for testing)"""
        if prop_object is None:
            from framework.mocks.vnge_mocks import create_mock_game_object
            prop_object = create_mock_game_object(prop_id)
        self.scenedata.props[prop_id] = prop_object
        return prop_object
    
    def clear_scene(self):
        """Clear scene data (for testing)"""
        self.scenedata.actors.clear()
        self.scenedata.props.clear()
        self.loaded_scenes.clear()
        self.current_scene = None


class MockSceneData:
    """Mock implementation of scene data"""
    
    def __init__(self):
        self.actors = {}  # entity_id -> MockCharacterActor
        self.props = {}   # prop_id -> MockGameObject
        self.scene_config = {}
        self.registered_props = {}
        self.active_entities = {}
        self.user_controlled_entity_id = None


class MockWindow:
    """Mock implementation of extra window"""
    
    def __init__(self, window_id, skin):
        self.window_id = window_id
        self.skin = skin
        self.windowRect = getattr(skin, 'windowRect', None)
        if self.windowRect is None:
            from framework.mocks.unity_mocks import MockRect
            self.windowRect = MockRect(100, 100, 400, 300)
    
    def close(self):
        """Close window"""
        print("Window {} closed".format(self.window_id))


class MockConfigParser:
    """Mock implementation of ConfigParser for testing"""
    
    def __init__(self):
        self.sections = {}
    
    def read(self, filename):
        """Mock read config file"""
        # For testing, we'll populate with default values
        self.sections = {
            'Harmony': {
                'autostart': '0',
                'autostart_delay': '1',
                'start_warmup_time': '0.5'
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
        print("Mock config loaded from {}".format(filename))
    
    def get(self, section, option):
        """Get config value"""
        return self.sections.get(section, {}).get(option, '')
    
    def items(self, section):
        """Get all items in section"""
        return list(self.sections.get(section, {}).items())
    
    def add_section(self, section):
        """Add config section"""
        if section not in self.sections:
            self.sections[section] = {}
    
    def set(self, section, option, value):
        """Set config value"""
        if section not in self.sections:
            self.sections[section] = {}
        self.sections[section][option] = value


def setup_game_mocks():
    """
    Set up game environment mocks in the global namespace.
    This function should be called before importing any plugin modules.
    """
    # Create mock ConfigParser module
    configparser_module = type(sys)('ConfigParser')
    configparser_module.SafeConfigParser = MockConfigParser
    
    # Add to sys.modules
    sys.modules['ConfigParser'] = configparser_module
    
    try:
        from framework.base import get_logger
        logger = get_logger("GameMocks")
        logger.debug("Game environment mocks initialized")
    except ImportError:
        print("Game environment mocks initialized")


def create_mock_game():
    """Create a mock game instance for testing"""
    return MockGame()


def create_mock_config():
    """Create a mock config parser for testing"""
    config = MockConfigParser()
    config.read("test_config.ini")  # This will populate with defaults
    return config
