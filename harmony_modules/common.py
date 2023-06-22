# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains basic types required by all plugin modules.


# Event States
EVENT_STATE_DONE = 'SUCCESS'  # Event was handled and returned successfully.
EVENT_STATE_ERROR = 'ERROR'  # Event processing failed for some reason.
EVENT_STATE_NEW = 'NEW'  # Event is new and has not been processed yet
EVENT_STATE_PENDING = 'PENDING'  # Event is in pending state (currently being processed)

# Event Types
EVENT_TYPE_AI_STATUS = 'AI_STATUS'
EVENT_TYPE_AI_SPEECH = 'AI_SPEECH'
EVENT_TYPE_STT_START_LISTEN = 'STT_START_LISTEN'
EVENT_TYPE_STT_STOP_LISTEN = 'STT_STOP_LISTEN'

# HarmonyClientModuleBase - used for registering further modules for handling events
class HarmonyClientModuleBase:
    def __init__(self, backend_handler):
        self.backendHandler = backend_handler
        self.active = False
        # AI State Details
        self.ai_state = None
        # Chara Details
        self.chara = None

    def activate(self):
        self.backendHandler.register_event_handler(self)
        self.active = True

    def deactivate(self):
        self.backendHandler.unregister_event_handler(self)
        self.active = False

    def update_ai_state(self, ai_state):
        print '[{0}]: Updated AI State:'.format(self.__class__.__name__)

        if ai_state is None or len(ai_state) == 0:
            self.ai_state = None
            print '[{0}]: AI State set to none'.format(self.__class__.__name__)

        if self.ai_state is None:
            self.ai_state = AIState()

        self.ai_state.gender = ai_state["gender"]
        self.ai_state.name = ai_state["name"]
        self.ai_state.mood = ai_state["mood"]
        self.ai_state.behaviour = ai_state["behaviour"]
        self.ai_state.persona = ai_state["persona"]
        self.ai_state.status_message = ai_state["status_message"]

        if isinstance(self.ai_state, AIState):
            print '[{0}]: Gender: {1}.'.format(self.__class__.__name__, self.ai_state.gender)
            print '[{0}]: Name: {1}.'.format(self.__class__.__name__, self.ai_state.name)
            print '[{0}]: Mood: {1}.'.format(self.__class__.__name__, self.ai_state.mood)
            print '[{0}]: Behaviour: {1}.'.format(self.__class__.__name__, self.ai_state.behaviour)
            print '[{0}]: Persona: {1}.'.format(self.__class__.__name__, self.ai_state.persona)
            print '[{0}]: Status Message: {1}.'.format(self.__class__.__name__, self.ai_state.status_message)

    def update_chara(self, chara):
        print '[{0}]: Updated Chara:'.format(self.__class__.__name__)
        self.chara = chara

    def handle_event(
            self,
            event  # HarmonyLinkEvent
    ):
        # To be implemented in subclasses
        return


# HarmonyLinkEvent - Base class for exchanging data with harmony link
class HarmonyLinkEvent:
    def __init__(self, event_id, event_type, status, payload):
        self.event_id = event_id
        self.event_type = event_type
        self.status = status
        self.payload = payload


# AIStatus - describes the current state of an AI character
class AIState:
    def __init__(self, gender="", name="", mood="", behaviour="", persona="", status_message=""):
        self.gender = gender
        self.name = name
        self.mood = mood
        self.behaviour = behaviour
        self.persona = persona
        self.status_message = status_message
