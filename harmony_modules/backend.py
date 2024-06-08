# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains all handling to be done with the Harmony Link Backend Module

# Import Backend base Module
from harmony_modules.common import *


# BackendHandler - module main class
class BackendHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, backend_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = backend_config

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # AI State update
        if event.event_type == EVENT_TYPE_AI_STATUS and event.status == EVENT_STATE_DONE:
            self.update_ai_state(ai_state=event.payload)

        return
