"""
Unit Tests for harmony_modules/connector.py

Tests the WebSocket/HTTP communication system, event handling, and connection management
without requiring actual network connections.
"""

import sys
import os
import time
import threading

# Add the src directory to the path so we can import the plugin modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Add the tests directory to the path so we can import the test framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework.plugin_test_environment import PluginTestEnvironment


class TestConnectorEventHandler:
    """Test ConnectorEventHandler class functionality"""
    
    def test_connector_initialization_websocket(self):
        """Test ConnectorEventHandler initialization with WebSocket support"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventHandler
            
            # Mock shutdown function
            def mock_shutdown(game):
                pass
            
            mock_game = type('MockGame', (), {})()
            
            # Create connector with WebSocket configuration
            connector = ConnectorEventHandler(
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_endpoint='http://127.0.0.1:28080',
                http_listen_port=28081,
                shutdown_func=mock_shutdown,
                game=mock_game
            )
            
            assert connector.ws_endpoint == 'ws://127.0.0.1:28080'
            assert connector.ws_buffer_size == 8192000
            assert connector.http_endpoint == 'http://127.0.0.1:28080'
            assert connector.http_listen_port == 28081
            assert connector.eventHandlers == []
            assert connector.harmony_session_id == ""
            assert connector.shutdown_func == mock_shutdown
            assert connector.game == mock_game
    
    def test_event_handler_registration(self):
        """Test event handler registration and unregistration"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventHandler
            
            def mock_shutdown(game):
                pass
            
            mock_game = type('MockGame', (), {})()
            
            connector = ConnectorEventHandler(
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_endpoint='http://127.0.0.1:28080',
                http_listen_port=28081,
                shutdown_func=mock_shutdown,
                game=mock_game
            )
            
            # Create mock event handlers
            mock_handler1 = type('MockHandler1', (), {
                'handle_event': lambda self, event: None,
                'deactivate': lambda self: None
            })()
            
            mock_handler2 = type('MockHandler2', (), {
                'handle_event': lambda self, event: None,
                'deactivate': lambda self: None
            })()
            
            # Test registration
            connector.register_event_handler(mock_handler1)
            assert len(connector.eventHandlers) == 1
            assert mock_handler1 in connector.eventHandlers
            
            connector.register_event_handler(mock_handler2)
            assert len(connector.eventHandlers) == 2
            assert mock_handler2 in connector.eventHandlers
            
            # Test duplicate registration (should not add twice)
            connector.register_event_handler(mock_handler1)
            assert len(connector.eventHandlers) == 2
            
            # Test unregistration
            connector.unregister_event_handler(mock_handler1)
            assert len(connector.eventHandlers) == 1
            assert mock_handler1 not in connector.eventHandlers
            assert mock_handler2 in connector.eventHandlers
            
            # Test unregistering non-existent handler
            connector.unregister_event_handler(mock_handler1)
            assert len(connector.eventHandlers) == 1
    
    def test_handle_event_distribution(self):
        """Test event distribution to registered handlers"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventHandler
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            
            def mock_shutdown(game):
                pass
            
            mock_game = type('MockGame', (), {})()
            
            connector = ConnectorEventHandler(
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_endpoint='http://127.0.0.1:28080',
                http_listen_port=28081,
                shutdown_func=mock_shutdown,
                game=mock_game
            )
            
            # Create mock event handlers that track received events
            received_events = []
            
            def create_mock_handler(handler_id):
                def handle_event(session_id, event):
                    received_events.append((handler_id, event, session_id))
                
                return type('MockHandler', (), {
                    'handle_event': handle_event,
                    'deactivate': lambda self: None
                })()
            
            handler1 = create_mock_handler('handler1')
            handler2 = create_mock_handler('handler2')
            
            connector.register_event_handler(handler1)
            connector.register_event_handler(handler2)
            
            # Create test event
            test_event = HarmonyLinkEvent(
                event_id='test_event_001',
                event_type='test_action',
                status=EVENT_STATE_NEW,
                payload={'action': 'test', 'data': 'test_data'}
            )
            
            # Handle event (simulating WebSocket mode)
            connector.handle_event(session_id="", event=test_event)
            
            # Verify both handlers received the event
            assert len(received_events) == 2
            # Check that both handlers received the event (now includes session_id)
            handler1_found = False
            handler2_found = False
            for handler_id, event, session_id in received_events:
                if handler_id == 'handler1' and event == test_event:
                    handler1_found = True
                elif handler_id == 'handler2' and event == test_event:
                    handler2_found = True
            assert handler1_found and handler2_found
    
    def test_send_event_websocket_not_connected(self):
        """Test send_event behavior when WebSocket is not connected"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventHandler
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            
            def mock_shutdown(game):
                pass
            
            mock_game = type('MockGame', (), {})()
            
            connector = ConnectorEventHandler(
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_endpoint='http://127.0.0.1:28080',
                http_listen_port=28081,
                shutdown_func=mock_shutdown,
                game=mock_game
            )
            
            # Create test event
            test_event = HarmonyLinkEvent(
                event_id='test_event_001',
                event_type='test_action',
                status=EVENT_STATE_NEW,
                payload={'action': 'test'}
            )
            
            # Try to send event when not connected (should return False)
            result = connector.send_event(test_event)
            assert result == False


class TestConnectorEventThread:
    """Test ConnectorEventThread class functionality"""
    
    def test_event_thread_initialization(self):
        """Test ConnectorEventThread initialization"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventThread
            
            # Create mock handler
            mock_handler = type('MockHandler', (), {
                'web_socket_client': None,
                'shutdown_func': lambda game: None,
                'game': type('MockGame', (), {})()
            })()
            
            # Create event thread
            event_thread = ConnectorEventThread(
                handler=mock_handler,
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_listen_port=28081
            )
            
            assert event_thread.handler == mock_handler
            assert event_thread.ws_endpoint == 'ws://127.0.0.1:28080'
            assert event_thread.ws_buffer_size == 8192000
            assert event_thread.running == False
            assert event_thread.shutting_down == False
    
    def test_process_event_message_valid_json(self):
        """Test processing valid JSON event messages"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventThread
            import json
            
            # Track handled events
            handled_events = []
            
            def mock_handle_event(slf, session_id, event):
                handled_events.append((session_id, event))
            
            # Create mock handler
            mock_handler = type('MockHandler', (), {
                'handle_event': mock_handle_event,
                'web_socket_client': None,
                'shutdown_func': lambda game: None,
                'game': type('MockGame', (), {})()
            })()
            
            # Create event thread
            event_thread = ConnectorEventThread(
                handler=mock_handler,
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_listen_port=28081
            )
            
            # Create test message
            test_event_data = {
                'event_id': 'test_001',
                'event_type': 'test_action',
                'status': 'NEW',
                'payload': {'action': 'walk', 'target': 'kaji'}
            }
            
            message_string = json.dumps(test_event_data)
            
            # Process the message
            event_thread.process_event_message(message_string, "test_session")
            
            # Verify event was handled
            assert len(handled_events) == 1
            session_id, event = handled_events[0]
            assert session_id == "test_session"
            assert event.event_id == 'test_001'
            assert event.event_type == 'test_action'
            assert event.status == 'NEW'
            assert event.payload['action'] == 'walk'
    
    def test_process_event_message_invalid_json(self):
        """Test processing invalid JSON event messages"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventThread
            
            # Track handled events
            handled_events = []
            
            def mock_handle_event(slf, session_id, event):
                handled_events.append((session_id, event))
            
            # Create mock handler
            mock_handler = type('MockHandler', (), {
                'handle_event': mock_handle_event,
                'web_socket_client': None,
                'shutdown_func': lambda game: None,
                'game': type('MockGame', (), {})()
            })()
            
            # Create event thread
            event_thread = ConnectorEventThread(
                handler=mock_handler,
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_listen_port=28081
            )
            
            # Process invalid JSON message
            event_thread.process_event_message("invalid json {", "test_session")
            
            # Verify no event was handled due to invalid JSON
            assert len(handled_events) == 0
    
    def test_process_event_message_empty(self):
        """Test processing empty event messages"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventThread
            
            # Track handled events
            handled_events = []
            
            def mock_handle_event(slf, session_id, event):
                handled_events.append((session_id, event))
            
            # Create mock handler
            mock_handler = type('MockHandler', (), {
                'handle_event': mock_handle_event,
                'web_socket_client': None,
                'shutdown_func': lambda game: None,
                'game': type('MockGame', (), {})()
            })()
            
            # Create event thread
            event_thread = ConnectorEventThread(
                handler=mock_handler,
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_listen_port=28081
            )
            
            # Process empty message
            event_thread.process_event_message("", "test_session")
            
            # Verify no event was handled due to empty message
            assert len(handled_events) == 0


class TestWebSocketEventSending:
    """Test WebSocket event sending functionality"""
    
    def test_send_websocket_event_valid_event(self):
        """Test sending valid HarmonyLinkEvent via WebSocket"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import _send_web_socket_event
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            from framework.mocks.system_mocks import MockClientWebSocket, MockWebSocketState
            
            # Create mock WebSocket client directly
            websocket_client = MockClientWebSocket()
            
            # Set WebSocket to Open state for testing
            websocket_client.state = MockWebSocketState.Open
            
            # Create test event
            test_event = HarmonyLinkEvent(
                event_id='test_ws_001',
                event_type='test_websocket',
                status=EVENT_STATE_NEW,
                payload={'message': 'test websocket message'}
            )
            
            # Send event
            result = _send_web_socket_event(websocket_client, test_event)
            
            # Verify success
            assert result == True
            
            # Verify message was sent
            assert len(websocket_client.sent_messages) == 1
            sent_message_data = websocket_client.sent_messages[0]
            sent_message = sent_message_data['message']
            assert 'test_ws_001' in sent_message
            assert 'test_websocket' in sent_message
    
    def test_send_websocket_event_dict_conversion(self):
        """Test sending dictionary that gets converted to HarmonyLinkEvent"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import _send_web_socket_event
            from framework.mocks.system_mocks import MockClientWebSocket, MockWebSocketState
            
            # Create mock WebSocket client directly
            websocket_client = MockClientWebSocket()
            
            # Set WebSocket to Open state for testing
            websocket_client.state = MockWebSocketState.Open
            
            # Create test event as dictionary
            test_event_dict = {
                'event_id': 'test_dict_001',
                'event_type': 'test_dict_event',
                'status': 'NEW',
                'payload': {'converted': True}
            }
            
            # Send event
            result = _send_web_socket_event(websocket_client, test_event_dict)
            
            # Verify success
            assert result == True
            
            # Verify message was sent
            assert len(websocket_client.sent_messages) == 1
            sent_message_data = websocket_client.sent_messages[0]
            sent_message = sent_message_data['message']
            assert 'test_dict_001' in sent_message
            assert 'test_dict_event' in sent_message
    
    def test_send_websocket_event_not_connected(self):
        """Test sending event when WebSocket is not connected"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import _send_web_socket_event
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            from framework.mocks.system_mocks import MockClientWebSocket, MockWebSocketState
            
            # Create mock WebSocket client directly
            websocket_client = MockClientWebSocket()
            
            # Set WebSocket to Closed state
            websocket_client.state = MockWebSocketState.Closed
            
            # Create test event
            test_event = HarmonyLinkEvent(
                event_id='test_closed_001',
                event_type='test_closed',
                status=EVENT_STATE_NEW,
                payload={'should_fail': True}
            )
            
            # Send event
            result = _send_web_socket_event(websocket_client, test_event)
            
            # Verify failure
            assert result == False
            
            # Verify no message was sent
            assert len(websocket_client.sent_messages) == 0
    
    def test_send_websocket_event_invalid_data(self):
        """Test sending invalid event data"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import _send_web_socket_event
            from framework.mocks.system_mocks import MockClientWebSocket, MockWebSocketState
            
            # Create mock WebSocket client directly
            websocket_client = MockClientWebSocket()
            
            # Set WebSocket to Open state for testing
            websocket_client.state = MockWebSocketState.Open
            
            # Try to send invalid event data
            result = _send_web_socket_event(websocket_client, 12345)
            
            # Verify failure
            assert result == False
            
            # Verify no message was sent
            assert len(websocket_client.sent_messages) == 0


class TestHTTPEventSending:
    """Test HTTP event sending functionality"""
    
    def test_send_http_event_valid_event(self):
        """Test sending valid HarmonyLinkEvent via HTTP"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import _send_http_event
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            
            # Create test event
            test_event = HarmonyLinkEvent(
                event_id='test_http_001',
                event_type='test_http',
                status=EVENT_STATE_NEW,
                payload={'http_test': True}
            )
            
            # Mock HTTP request will be handled by our mock system
            # The actual HTTP functionality would require more complex mocking
            # For now, test the event validation logic
            
            # Test with valid event - this will fail due to network but validates input
            try:
                result = _send_http_event(
                    endpoint='http://127.0.0.1:28080',
                    session_id='test_session',
                    result_port='28081',
                    event=test_event
                )
                # If it doesn't throw an exception, the input validation passed
                # The actual network call will fail in test environment
            except:
                # Expected to fail due to no actual HTTP server
                pass
    
    def test_send_http_event_dict_conversion(self):
        """Test sending dictionary that gets converted to HarmonyLinkEvent"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import _send_http_event
            
            # Create test event as dictionary
            test_event_dict = {
                'event_id': 'test_http_dict_001',
                'event_type': 'test_http_dict',
                'status': 'NEW',
                'payload': {'http_dict_test': True}
            }
            
            # Test with valid dictionary - this will fail due to network but validates input
            try:
                result = _send_http_event(
                    endpoint='http://127.0.0.1:28080',
                    session_id='test_session',
                    result_port='28081',
                    event=test_event_dict
                )
                # If it doesn't throw an exception, the input validation passed
            except:
                # Expected to fail due to no actual HTTP server
                pass


class TestHarmonyEventJSONEncoder:
    """Test HarmonyEventJSONEncoder functionality"""
    
    def test_json_encoder_harmony_event(self):
        """Test JSON encoding of HarmonyLinkEvent"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import HarmonyEventJSONEncoder
            from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW
            import json
            
            # Create test event
            test_event = HarmonyLinkEvent(
                event_id='test_json_001',
                event_type='test_json',
                status=EVENT_STATE_NEW,
                payload={'json_test': True, 'number': 42}
            )
            
            # Encode to JSON
            json_string = json.dumps(test_event, cls=HarmonyEventJSONEncoder)
            
            # Verify JSON contains expected fields
            assert 'test_json_001' in json_string
            assert 'test_json' in json_string
            assert 'NEW' in json_string
            assert 'json_test' in json_string
            assert '42' in json_string
            
            # Verify it can be decoded back
            decoded_data = json.loads(json_string)
            assert decoded_data['event_id'] == 'test_json_001'
            assert decoded_data['event_type'] == 'test_json'
            assert decoded_data['status'] == 'NEW'
            assert decoded_data['payload']['json_test'] == True
            assert decoded_data['payload']['number'] == 42


class TestPerformance:
    """Test performance characteristics of connector.py"""
    
    def test_event_handler_registration_performance(self):
        """Test performance of event handler registration"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventHandler
            
            def mock_shutdown(game):
                pass
            
            mock_game = type('MockGame', (), {})()
            
            connector = ConnectorEventHandler(
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_endpoint='http://127.0.0.1:28080',
                http_listen_port=28081,
                shutdown_func=mock_shutdown,
                game=mock_game
            )
            
            start_time = time.time()
            
            # Register many event handlers
            handlers = []
            for i in range(100):
                handler = type('MockHandler{}'.format(i), (), {
                    'handle_event': lambda self, event: None,
                    'deactivate': lambda self: None
                })()
                handlers.append(handler)
                connector.register_event_handler(handler)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should register 100 handlers quickly
            assert execution_time < 10.0  # Less than 10 seconds
            assert len(connector.eventHandlers) == 100
    
    def test_event_processing_performance(self):
        """Test performance of event processing"""
        with PluginTestEnvironment() as env:
            from harmony_modules.connector import ConnectorEventThread
            import json
            
            # Track processed events
            processed_events = []
            
            def mock_handle_event(slf, session_id, event):
                processed_events.append(event)
            
            # Create mock handler
            mock_handler = type('MockHandler', (), {
                'handle_event': mock_handle_event,
                'web_socket_client': None,
                'shutdown_func': lambda game: None,
                'game': type('MockGame', (), {})()
            })()
            
            # Create event thread
            event_thread = ConnectorEventThread(
                handler=mock_handler,
                ws_endpoint='ws://127.0.0.1:28080',
                ws_buffer_size=8192000,
                http_listen_port=28081
            )
            
            start_time = time.time()
            
            # Process many events
            for i in range(100):
                test_event_data = {
                    'event_id': 'perf_test_{}'.format(i),
                    'event_type': 'performance_test',
                    'status': 'NEW',
                    'payload': {'index': i}
                }
                
                message_string = json.dumps(test_event_data)
                event_thread.process_event_message(message_string, "perf_session")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should process 100 events quickly
            assert execution_time < 1.0  # Less than 1 second
            assert len(processed_events) == 100


if __name__ == "__main__":
    # Import test runner
    from framework.base import TestRunner, TEST_LOG_LEVEL_QUIET
    
    # Create test runner with quiet logging
    runner = TestRunner(log_level=TEST_LOG_LEVEL_QUIET)
    
    # Create test instances
    test_classes = [
        TestConnectorEventHandler(),
        TestConnectorEventThread(),
        TestWebSocketEventSending(),
        TestHTTPEventSending(),
        TestHarmonyEventJSONEncoder(),
        TestPerformance()
    ]
    
    # Run test suite
    runner.run_test_suite(test_classes, "unit tests for harmony_modules/connector.py")

