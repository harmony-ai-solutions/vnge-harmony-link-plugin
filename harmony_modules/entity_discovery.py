# Harmony Link Plugin for VNGE - Entity Discovery Module
# (c) 2023-2025 Project Harmony.AI (contact@project-harmony.ai)
#
# This module handles discovery of available entities from Harmony Link

import time
from harmony_modules.common import HarmonyLinkEvent, EVENT_STATE_NEW, EVENT_STATE_DONE, EVENT_TYPE_FETCH_CONFIGURED_ENTITIES
from harmony_modules.connector import ConnectorEventHandler

class EntityDiscoveryHandler:
    """
    Temporary handler for discovering available entities from Harmony Link.
    Creates its own connector to avoid interfering with main entity connections.
    """
    
    def __init__(self, config):
        """
        Initialize the discovery handler with configuration.
        
        Args:
            config: ConfigParser object with Harmony Link connection settings
        """
        self.config = config
        self.available_entities = []
        self.response_received = False
        self.connector = None
        
    def fetch_entities(self):
        """
        Fetch available entities from Harmony Link.
        
        Returns:
            list: List of entity dictionaries with 'id' and 'configured_providers' fields
        """
        try:
            # Create a temporary connector for discovery
            # Use a different port to avoid conflicts
            base_port = int(self.config.get('Connector', 'http_listen_port'))
            discovery_port = base_port + 100  # Use offset of 100 for discovery
            
            self.connector = ConnectorEventHandler(
                ws_endpoint=self.config.get('Connector', 'ws_endpoint'),
                ws_buffer_size=int(self.config.get('Connector', 'ws_buffer_size')),
                http_endpoint=self.config.get('Connector', 'http_endpoint'),
                http_listen_port=discovery_port,
                shutdown_func=lambda x: None,  # Dummy shutdown function
                game=None
            )
            
            # Register this handler to receive events
            self.connector.register_event_handler(self)
            
            # Start the connector
            self.connector.start()
            
            # Send discovery event
            discovery_event = HarmonyLinkEvent(
                event_id='fetch_entities',
                event_type=EVENT_TYPE_FETCH_CONFIGURED_ENTITIES,
                status=EVENT_STATE_NEW,
                payload={}
            )
            
            print('Harmony Link: Fetching available entities...')
            success = self.connector.send_event(discovery_event)
            
            if success:
                # Wait for response (up to 5 seconds)
                timeout = 5.0
                start_time = time.time()
                
                while not self.response_received and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                if not self.response_received:
                    print('Harmony Link: Timeout waiting for entity list')
            else:
                print('Harmony Link: Failed to send entity discovery request')
            
        except Exception as e:
            print('Harmony Link: Error during entity discovery: {0}'.format(str(e)))
            
        finally:
            # Always cleanup the connector
            if self.connector:
                try:
                    self.connector.stop()
                except:
                    pass
                self.connector = None
        
        return self.available_entities
    
    def handle_event(self, event):
        """
        Handle events from Harmony Link.
        
        Args:
            event: HarmonyLinkEvent object
        """
        if event.event_type == EVENT_TYPE_FETCH_CONFIGURED_ENTITIES and event.status == EVENT_STATE_DONE:
            try:
                # Parse the entity list from the payload
                if isinstance(event.payload, list):
                    self.available_entities = event.payload
                else:
                    # If payload is a dict or string, try to extract entities
                    import json
                    if isinstance(event.payload, str):
                        self.available_entities = json.loads(event.payload)
                    elif isinstance(event.payload, dict) and 'entities' in event.payload:
                        self.available_entities = event.payload['entities']
                    else:
                        self.available_entities = []
                
                print('Harmony Link: Received {0} entities'.format(len(self.available_entities)))
                for entity in self.available_entities:
                    print('  - Entity: {0}'.format(entity.get('id', 'unknown')))
                    
                self.response_received = True
                
            except Exception as e:
                print('Harmony Link: Error parsing entity list: {0}'.format(str(e)))
                self.response_received = True  # Stop waiting even on error
    
    def activate(self):
        """Compatibility method - not used for discovery"""
        pass
    
    def deactivate(self):
        """Compatibility method - cleanup handled in fetch_entities"""
        pass
