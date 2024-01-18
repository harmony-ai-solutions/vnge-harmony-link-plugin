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
# Chat LLM
EVENT_TYPE_CHAT_HISTORY = 'CHAT_HISTORY'
EVENT_TYPE_AI_STATUS = 'AI_STATUS'
EVENT_TYPE_AI_SPEECH = 'AI_SPEECH'
EVENT_TYPE_AI_ACTION = 'AI_ACTION'
EVENT_TYPE_USER_UTTERANCE = 'USER_UTTERANCE'
# Countenance
EVENT_TYPE_AI_COUNTENANCE_UPDATE = 'AI_COUNTENANCE_UPDATE'
# STT
EVENT_TYPE_STT_START_LISTEN = 'STT_START_LISTEN'
EVENT_TYPE_STT_STOP_LISTEN = 'STT_STOP_LISTEN'
# TTS
EVENT_TYPE_TTS_PLAYBACK_DONE = 'TTS_PLAYBACK_DONE'
EVENT_TYPE_TTS_GENERATE_SPEECH = 'TTS_GENERATE_SPEECH'
# Movement


# Utterance Types
UTTERANCE_COMBINED = 'UTTERANCE_COMBINED'
UTTERANCE_VERBAL = 'UTTERANCE_VERBAL'
UTTERANCE_NONVERBAL = 'UTTERANCE_NONVERBAL'
UTTERANCE_NONVERBAL_DELAYED = 'UTTERANCE_NONVERBAL_DELAYED'

# HarmonyClientModuleBase - used for registering further modules for handling events
class HarmonyClientModuleBase:
    def __init__(self, backend_connector):
        self.backend_connector = backend_connector
        self.active = False
        # AI State Details
        self.ai_state = None
        self.countenance_state = None
        # Chara Details
        self.chara = None

    def activate(self):
        self.backend_connector.register_event_handler(self)
        self.active = True

    def deactivate(self):
        self.backend_connector.unregister_event_handler(self)
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

    def update_countenance_state(self, countenance_state):
        print '[{0}]: Updated Countenance State:'.format(self.__class__.__name__)

        if countenance_state is None or len(countenance_state) == 0:
            self.countenance_state = None
            print '[{0}]: Countenance State set to none'.format(self.__class__.__name__)

        if self.countenance_state is None:
            self.countenance_state = CountenanceState()

        self.countenance_state.emotional_state = countenance_state["emotional_state"]
        self.countenance_state.facial_expression = countenance_state["facial_expression"]

        if isinstance(self.countenance_state, CountenanceState):
            print '[{0}]: Emotional State: {1}.'.format(self.__class__.__name__, self.countenance_state.emotional_state)
            print '[{0}]: Facial Expression: {1}.'.format(self.__class__.__name__, self.countenance_state.facial_expression)

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


# AIState - describes the current state of an AI character
class AIState:
    def __init__(self, gender="", name="", mood="", behaviour="", persona="", status_message=""):
        self.gender = gender
        self.name = name
        self.mood = mood
        self.behaviour = behaviour
        self.persona = persona
        self.status_message = status_message


# CountenanceState - describes the current state of an AI character
class CountenanceState:
    def __init__(self, emotional_state="", facial_expression=""):
        self.emotional_state = emotional_state
        self.facial_expression = facial_expression
