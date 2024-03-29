# Harmony Link Plugin for VNGE
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This file contains an individual implementation of Countenance handling based on Harmony Link AIState Events.
#
# At a later point it is intended to have Harmony Link calculate countenance params internally and clients
# just need to visualize these.
#
# However this is also a valid way to go in case the capabilities of the Event API are insufficient.

# Import Backend base Module
from harmony_modules.common import *

# VNGE
from Studio import Info
from vngameengine import vnge_game as game
from vnlibfaceexpressions import conf_neo_male, conf_neo_female
from vnactor import char_act_funcs

from threading import Thread
import time
import json

#
registered_actions = [
    # Basic movement and interaction
    {
        'name': 'move',
        'description': 'normal walking',
        'examples': [
            '{{character}} starts walking',
            '{{character}} starts moving',
            '{{character}} walks over to {{other_character}}',
            '{{character}} walks over to {{object}}',
            '{{character}} walks past {{object}} to {{other_object}}',
            '{{character}} walks past {{other_character}} to {{other_object}}',
            '{{character}} walks past {{other_character}} to {{character_group}}',
            '{{character}} walks past {{character_group}} to {{other_character_group}}',
            '{{character}} walks past {{object}} to {{other_character}}',
            '{{character}} takes a step forward',
            '{{character}} strides towards {{object}}',
            '{{character}} strolls around {{object}}',
            '{{character}} marches towards {{other_character}}',
            '{{character}} saunters towards the {{object_collection}}',
            '{{character}} advances toward {{character_group}}',
            '{{character}} tip-toes closer to {{other_character}}',
            '{{character}} quietly sneaks up on {{other_character}}',
            '{{character}} tiptoes toward {{object}}'
        ],
        'confirmations': [
            # '{{none}}'
        ],
        'rejections': [
            # '{{none}}'
        ]
    },
    {
        'name': 'walk',
        'description': 'fast walking',
        'examples': [
            '{{character}} jogs',
            '{{character}} hurries',
            '{{character}} rushes',
            '{{character}} moves quickly',
            '{{character}} speeds up',
            '{{character}} walks briskly',
            '{{character}} strides',
            '{{character}} marches',
            '{{character}} hastens',
            '{{character}} trots',
            '{{character}} scurries',
            '{{character}} dashes',
            '{{character}} bolts',
            '{{character}} sprints'
        ],
        'confirmations': [
            # '{{none}}'
        ],
        'rejections': [
            # '{{none}}'
        ]
    },
    {
        "name": "run",
        "description": "running",
        "examples": [
            "{{character}} runs forward quickly",
            "{{character}} sprints ahead",
            "{{character}} dashes past {{object}}",
            "{{character}} rushes towards {{other_character}}",
            "{{character}} bolts from {{character_group}} to {{other_character_group}}",
            "{{character}} jogs around {{object_collection}}",
            "{{character}} hurries while carrying {{object}}",
            "{{character}} rapidly moves away from danger",
            "{{character}} escapes by running fast",
            "{{character}} outpaces {{other_character}} easily"
        ],
        "confirmations": [
            # '{{none}}'
        ],
        "rejections": [
            # '{{none}}'
        ]
    },
    {
        "name": "sit_down",
        "description": "sit down on the ground or an object",
        "examples": [
            "{{character}} sits down on the {{object}}",
            "{{character}} lowers himself onto the {{object}}",
            "{{character}} plops down on the {{object}}",
            "{{character}} takes a seat on the {{object}}",
            "{{character}} perches on the {{object}}",
            "{{character}} settles into the {{object}}",
            "{{character}} squats down on the {{object}}",
            "{{character}} kneels down next to {{object}}",
            "{{character}} sits cross-legged on the {{object}}",
            "{{character}} hunkers down behind the {{object}}"
        ],
        "confirmations": [
            # '{{none}}'
        ],
        "rejections": [
            # '{{none}}'
        ]
    },
    {
        "name": "lean_against",
        "description": "sit down on the ground or an object",
        "examples": [
            "{{character}} leans against the {{object}}",
            "{{character}} rests his back against the {{object}}",
            "{{character}} finds support by leaning against the {{object}}",
            "{{character}} uses the {{object}} as a prop to lean against",
            "{{character}} relaxes by leaning against the {{object}}",
            "{{character}} takes a break and leans against the {{object}}",
            "{{character}} leans his weight against the {{object}}",
            "{{character}} leans on the {{object}} for support",
            "{{character}} finds comfort in leaning against the {{object}}",
            "{{character}} enjoys the feeling of leaning against the {{object}}",
            "{{character}} appreciates the sturdiness of the {{object}} while leaning against it"
        ],
        "confirmations": [
            # '{{none}}'
        ],
        "rejections": [
            # '{{none}}'
        ]
    },
    {
        'name': 'lay_down',
        'description': 'lay down on the ground or an object',
        'examples': [
            "{{character}} lies down on the {{object}}",
            "{{character}} curls up on the {{object}}",
            "{{character}} sprawls out on the {{object}}",
            "{{character}} takes a rest by laying down on the {{object}}",
            "{{character}} finds a comfortable spot and lays down",
            "{{character}} decides to take a nap on the {{object}}",
            "{{character}} settles down for a quick rest on the {{object}}",
            "{{character}} stretches out on the {{object}}",
            "{{character}} gently lowers themselves onto the {{object}}",
            "{{character}} lays down next to {{other_character}} on the {{object}}",
            "{{character}} lays down their head on the {{object}}",
            "{{character}} makes a pillow of their arms and lays down on the {{object}}",
            "{{character}} lays down on the {{object}}, gently swinging back and forth",
            "{{character}} carefully lays down on the {{object}}",
            "{{character}} cautiously lays down on the {{object}}"
        ],
        'confirmations': [
            # '{{none}}'
        ],
        'rejections': [
            # '{{none}}'
        ]
    },
    {
        'name': 'stand_up',
        'description': 'stand up from sitting or lying position',
        'examples': [
            '{{character}} rises from their seated position',
            '{{character}} gets up from the {{object}}',
            '{{character}} stands up after resting on {{object}}',
            '{{character}} lifts themselves off {{object}}',
            '{{character}} pushes themselves up from {{object}}',
            '{{character}} climbs back onto their feet',
            '{{character}} raises from a kneeling posture',
            '{{character}} unfolds themself from a squatting stance',
            '{{character}} rises slowly from {{object}}',
            '{{character}} swiftly gets up from a prone position',
            '{{character}} jumps up from {{object}}',
            '{{character}} ascends from a crouching state',
            '{{character}} elevates themself from {{object}}',
            '{{character}} emerges from underneath {{object}}',
            '{{character}} disengages from a sprawled layout'
        ],
        'confirmations': [
            # '{{none}}'
        ],
        'rejections': [
            # '{{none}}'
        ]
    },
    {
        'name': 'jump_fixed',
        'description': 'jump at current position',
        'examples': [
            '{{character}} jumps in place',
            '{{character}} leaps up from {{object}}',
            '{{character}} springs into the air',
            '{{character}} makes a vertical jump',
            '{{character}} jumps straight up',
            '{{character}} launches off {{object}}',
            '{{character}} bounces upwards',
            '{{character}} performs a standing jump',
            '{{character}} executes a quick hop',
            '{{character}} does a small lift',
            '{{character}} makes a tiny leap'
        ],
        'confirmations': [
            # '{{none}}'
        ],
        'rejections': [
            # '{{none}}'
        ]
    },
    {
        'name': 'jump_over',
        'description': 'jump over an object',
        'examples': [
            '{{character}} jumps over {{object}}',
            '{{character}} leaps over {{object}}',
            '{{character}} hops over {{object}}',
            '{{character}} jumps high over {{object}}',
            '{{character}} jumps far over {{object}}',
            '{{character}} jumps quickly over {{object}}',
            '{{character}} stumbles while jumping over {{object}}',
            '{{character}} barely clears {{object}} with a jump',
            '{{character}} struggles to jump over {{object}}'
        ],
        'confirmations': [
            '{{character}} makes it over {{object}}',
            '{{character}} lands on the other side of {{object}} after jumping over it',
            '{{character}} succeeds in jumping over {{object}}'
        ],
        'rejections': [
            '{{character}} doesn\'t make it over {{object}}',
            '{{character}} fails to jump over {{object}}',
            '{{character}} fails to jump over {{object}} and falls',
            '{{character}} trips over {{object}} while trying to jump over it'
        ]
    },
    {
        'name': 'pick_up_left_hand',
        'description': 'pick up an object with left hand',
        'examples': [
            '{{character}} picks up {{object}} with their left hand',
            '{{character}} uses their left hand to lift {{object}}',
            '{{character}} grabs {{object}} with their left hand',
            '{{character}} lifts {{object}} using their left hand',
            '{{character}} picks up {{object}} from the ground with their left hand',
            '{{character}} retrieves {{object}} with their left hand',
            '{{character}} collects {{object}} with their left hand',
            '{{character}} acquires {{object}} with their left hand',
            '{{character}} secures {{object}} with their left hand',
            '{{character}} obtains {{object}} with their left hand',
            '{{character}} grasps {{object}} with their left hand'
        ],
        'confirmations': [
            '{{object}} is now in {{character}}\'s left hand',
            '{{character}} has picked up {{object}} with their left hand',
            '{{object}} is successfully held by {{character}}\'s left hand'
        ],
        'rejections': [
            '{{object}} is too heavy for {{character}}\'s left hand',
            '{{object}} slips out of {{character}}\'s left hand',
            '{{character}}\'s left hand cannot hold {{object}}'
        ]
    },
    {
        'name': 'pick_up_right_hand',
        'description': 'pick up an object with right hand',
        'examples': [
            '{{character}} picks up {{object}} with their right hand',
            '{{character}} uses their right hand to lift {{object}}',
            '{{character}} grabs {{object}} with their right hand',
            '{{character}} lifts {{object}} using their right hand',
            '{{character}} picks up {{object}} from the ground with their right hand',
            '{{character}} retrieves {{object}} with their right hand',
            '{{character}} collects {{object}} with their right hand',
            '{{character}} acquires {{object}} with their right hand',
            '{{character}} secures {{object}} with their right hand',
            '{{character}} obtains {{object}} with their right hand',
            '{{character}} grasps {{object}} with their right hand'
        ],
        'confirmations': [
            '{{object}} is now in {{character}}\'s right hand',
            '{{character}} has picked up {{object}} with their right hand',
            '{{object}} is successfully held by {{character}}\'s right hand'
        ],
        'rejections': [
            '{{object}} is too heavy for {{character}}\'s right hand',
            '{{object}} slips out of {{character}}\'s right hand',
            '{{character}}\'s right hand cannot hold {{object}}'
        ]
    },
    {
        'name': 'pick_up_both_hands',
        'description': 'pick up an object with both hands',
        'examples': [
            '{{character}} reaches for {{object}} with both hands',
            '{{character}} grabs {{object}} using both hands',
            '{{character}} lifts {{object}} with both hands',
            '{{character}} carefully picks up {{object}} with both hands',
            '{{character}} positions both hands to lift {{object}}',
            '{{character}} readies both hands to pick up {{object}}',
            '{{character}} uses both hands to securely hold {{object}}',
            '{{character}} brings both hands together to pick up {{object}}',
            '{{character}} gathers both hands around {{object}} to lift it',
            '{{character}} interlocks fingers to lift {{object}}'
        ],
        'confirmations': [
            '{{character}} successfully lifts {{object}}',
            '{{object}} is now held by {{character}} with both hands',
            '{{character}} has picked up {{object}} with both hands'
        ],
        'rejections': [
            '{{object}} is too heavy for {{character}} to lift with both hands',
            '{{object}} cannot be lifted with both hands',
            '{{character}} struggles to lift {{object}} with both hands',
            '{{character}} fails to pick up {{object}} with both hands'
        ]
    },
    {
        "name": "drop_item",
        "description": "drop item currently in hands to the ground",
        "examples": [
            "{{character}} drops {{object}} on the ground",
            "{{character}} lets go of {{object}}",
            "{{character}} releases {{object}}",
            "{{character}} throws {{object}} down",
            "{{character}} tosses {{object}} aside",
            "{{character}} places {{object}} on the floor",
            "{{character}} sets {{object}} down",
            "{{character}} puts {{object}} on the ground",
            "{{character}} lays {{object}} on the ground",
            "{{character}} leaves {{object}} on the ground"
        ],
        "confirmations": [
            # '{{none}}'
        ],
        "rejections": [
            # '{{none}}'
        ]
    },
    {
        'name': 'store_item',
        'description': 'store item in hand in pocket / inventory',
        'examples': [
            '{{character}} puts {{object}} into their pocket',
            '{{character}} stores {{object}} in their inventory',
            '{{character}} stows away {{object}} in their bag',
            '{{character}} hides {{object}} in their sleeve',
            '{{character}} secures {{object}} in their belt',
            '{{character}} places {{object}} in their backpack',
            '{{character}} tucks {{object}} into their shirt',
            '{{character}} slots {{object}} into their holster',
            '{{character}} inserts {{object}} into their sheath',
            '{{character}} deposits {{object}} in their container',
            '{{character}} saves {{object}} in their storage'
        ],
        'confirmations': [
            '{{object}} is now stored',
            '{{object}} is securely in your possession',
            '{{object}} is put away safely',
            '{{object}} is in your inventory'
        ],
        'rejections': [
            '{{object}} does not fit',
            '{{object}} is too large',
            '{{object}} is not suitable for storage'
        ]
    },
    {

        'name': 'retrieve_item',

        'description': 'retrieve item from pocket / inventory into hand',

        'examples': [
            '{{character}} reaches into {{character}}\'s pocket and pulls out {{object}}',
            '{{character}} grabs {{object}} from {{character}}\'s inventory',
            '{{character}} withdraws {{object}} from {{character}}\'s backpack',
            '{{character}} takes {{object}} out of {{character}}\'s bag',
            '{{character}} removes {{object}} from {{character}}\'s satchel',
            '{{character}} fetches {{object}} from {{character}}\'s belt',
            '{{character}} picks up {{object}} from {{character}}\'s holster',
            '{{character}} lifts {{object}} out of {{character}}\'s pouch',
            '{{character}} extracts {{object}} from {{character}}\'s sheath',
            '{{character}} draws {{object}} from {{character}}\'s scabbard'
        ],
        'confirmations': [
            '{{character}} holds {{object}} in hand',
            '{{object}} now equipped by {{character}}',
            '{{object}} ready to use in {{character}}\'s hand'
        ],
        'rejections': [
            '{{object}} not found in {{character}}\'s possession',
            '{{object}} stuck in {{character}}\'s pocket',
            '{{object}} broken or damaged beyond repair'
        ]
    },
    {
        "name": "place_item",
        "description": "place item currently in hands on the ground or an object",
        "examples": [
            "{{character}} lays down {{object}} on {{other_object}}",
            "{{character}} sets {{object}} on {{other_object}}",
            "{{character}} places {{object}} into {{other_object}}",
            "{{character}} puts {{object}} next to {{other_object}}",
            "{{character}} drops {{object}} at {{other_character}}\'s feet",
            "{{character}} leaves {{object}} behind",
            "{{character}} positions {{object}} carefully on {{other_object}}",
            "{{character}} throws {{object}} onto {{other_object}}",
            "{{character}} plops {{object}} down on {{other_object}}",
            "{{character}} hangs {{object}} on {{other_object}}"
        ],
        "confirmations": [
            "{{object}} has been placed",
            "{{object}} is now on {{other_object}}",
            "{{other_character}} sees {{object}} where it was placed"
        ],
        "rejections": [
            "{{object}} cannot be placed there",
            "{{object}} doesn't fit"
        ]
    },
    {
        'name': 'drop_item',
        'description': 'drop item currently in hands to the ground',
        'examples': [
            '{{character}} drops {{object}} on the ground',
            '{{character}} lets go of {{object}}',
            '{{character}} releases {{object}}',
            '{{character}} throws {{object}} down',
            '{{character}} tosses {{object}} away',
            '{{character}} sets {{object}} down',
            '{{character}} unloads {{object}} from their inventory onto {{other_object}}',
            '{{character}} discards {{object}}',
            '{{character}} gets rid of {{object}} by dropping it'
        ],
        'confirmations': [
            '{{object}} hits the ground',
            '{{object}} falls to the floor',
            '{{object}} lands with a thud',
            '{{character}} sees {{object}} on the ground'
        ],
        'rejections': [
            '{{character}} can\'t get rif of {{object}}',
            '{{object}} bounces off and finds itself back in {{character}}\s hands',
            '{{object}} keeps sticking to {{character}}'
        ]
    },

    # Chara interaction
    {
        'name': 'give_item',
        'description': 'give item in hand to the other chara\'s hand',
        'examples': [
            '{{character}} passes {{object}} to {{other_character}}',
            '{{character}} transfers {{object}} to {{other_character}}',
            '{{character}} presents {{object}} to {{other_character}}',
            '{{character}} offers {{object}} to {{other_character}}',
            '{{character}} holds out {{object}} to {{other_character}}',
            '{{character}} extends {{object}} towards {{other_character}}',
            '{{character}} puts {{object}} into {{other_character}}\'s hand',
            '{{character}} lays {{object}} in {{other_character}}\'s palm',
            '{{character}} sets {{object}} down next to {{other_character}}',
            '{{character}} places {{object}} by {{other_character}}'
        ],
        'confirmations': [
            '{{other_character}} receives {{object}}',
            '{{other_character}} grasps {{object}}',
            '{{other_character}} catches {{object}}',
            '{{other_character}} takes hold of {{object}}',
            '{{other_character}} clutches {{object}}'
        ],
        'rejections': [
            '{{other_character}} declines {{object}}',
            '{{other_character}} pushes {{object}} away',
            '{{other_character}} avoids {{object}}',
            '{{other_character}} shuns {{object}}',
            '{{other_character}} ignores {{object}}'
        ]
    },
    {
        'name': 'take_hand',
        'description': 'take hand of the other chara, depending on position, and interlock',
        'examples': [
            '{{character}} reaches out to take {{other_character}}\'s hand',
            '{{character}} extends a hand towards {{other_character}}',
            '{{character}} offers a handshake to {{other_character}}',
            '{{character}} grasps {{other_character}}\'s hand',
            '{{character}} interlocks fingers with {{other_character}}',
            '{{character}} holds hands with {{other_character}}',
            '{{character}} takes {{other_character}}\'s hand in their own',
            '{{character}} gently clasps {{other_character}}\'s hand',
            '{{character}} links arms with {{other_character}}',
            '{{character}} grabs {{other_character}}\'s hand',
            '{{character}} seizes {{other_character}}\'s hand',
            '{{character}} clutches {{other_character}}\'s hand'
        ],
        'confirmations': [
            '{{other_character}} reciprocates the gesture',
            '{{other_character}} tightens their grip',
            '{{other_character}} squeezes {{character}}\'s hand back',
            '{{other_character}} smiles and holds on',
            '{{other_character}} returns the handshake firmly',
            '{{other_character}} interlocks fingers with {{character}}'
        ],
        'rejections': [
            '{{other_character}} pulls their hand away',
            '{{other_character}} shakes their head and steps back',
            '{{other_character}} recoils at the touch',
            '{{other_character}} looks uncomfortable and avoids eye contact',
            '{{other_character}} ignores the gesture'
        ]
    },
    {
        'name': 'caress_cheek',
        'description': 'caress cheek of the other chara',
        'examples': [
            '{{character}} gently caresses {{other_character}}\'s cheek',
            '{{character}} softly touches {{other_character}}\'s face',
            '{{character}} runs their fingers along {{other_character}}\'s cheek',
            '{{character}} leans in and caresses {{other_character}}\'s cheek',
            '{{character}} smiles and caresses {{other_character}}\'s cheek',
            '{{character}} lovingly strokes {{other_character}}\'s cheek',
            '{{character}} tenderly caresses {{other_character}}\'s cheek',
            '{{character}} sweetly touches {{other_character}}\'s cheek',
            '{{character}} kindly caresses {{other_character}}\'s cheek',
            '{{character}} carefully strokes {{other_character}}\'s cheek',
            '{{character}} delicately touches {{other_character}}\'s cheek'
        ],
        'confirmations': [
            '{{other_character}} leans into the touch',
            '{{other_character}} closes their eyes',
            '{{other_character}} smiles',
            '{{other_character}} blushes',
            '{{other_character}} sighs contentedly'
        ],
        'rejections': [
            '{{other_character}} flinches',
            '{{other_character}} pulls away',
            '{{other_character}} looks uncomfortable',
            '{{other_character}} tenses up',
            '{{other_character}} glares at {{character}}'
        ]
    },
    {
        'name': 'caress_head',
        'description': 'caress head of the other chara',
        'examples': [
            '{{character}} gently strokes {{other_character}}\'s hair',
            '{{character}} caresses {{other_character}}\'s head',
            '{{character}} runs fingers through {{other_character}}\'s hair',
            '{{character}} softly combs {{other_character}}\'s hair with fingers',
            '{{character}} tenderly touches {{other_character}}\'s forehead',
            '{{character}} sweetly scratches {{other_character}}\'s temple',
            '{{character}} leans in and lovingly tucks {{other_character}}\'s hair behind their ear',
            '{{character}} delicately traces patterns on {{other_character}}\'s head with fingertips',
            '{{character}} affectionately ruffles {{other_character}}\'s hair',
            '{{character}} kindly soothes {{other_character}}\'s temples',
            '{{character}} carefully brushes back {{other_character}}\'s bangs',
            '{{character}} playfully messes up {{other_character}}\'s hairstyle',
            '{{character}} curiously examines {{other_character}}\'s hair texture',
            '{{character}} lovingly embraces {{other_character}}\'s head against their chest'
        ],
        'confirmations': [
            '{{other_character}} purrs contentedly under your touch',
            '{{other_character}} sighs pleasantly as you stroke their hair',
            '{{other_character}} smiles warmly at your gentle gesture',
            '{{other_character}} relaxes visibly in your comforting presence',
            '{{other_character}} leans into your touch, seeking more connection',
            '{{other_character}} nuzzles closer to you, enjoying the moment'
        ],
        'rejections': [
            '{{other_character}} stiffens and moves away from your touch',
            '{{other_character}} flinches slightly at your sudden movement',
            '{{other_character}} frowns and expresses discomfort',
            '{{other_character}} raises their hand to halt your actions',
            '{{other_character}} steps back, creating distance between you both',
            '{{other_character}} looks uncomfortable and avoids eye contact'
        ]
    },
    {
        'name': 'kiss_hand',
        'description': 'take hand of the other chara, and kiss it in a romantic way',
        'examples': [
            '{{character}} gently takes {{other_character}}\'s hand',
            '{{character}} reaches for {{other_character}}\'s hand',
            '{{character}} brings {{other_character}}\'s hand to their lips',
            '{{character}} softly kisses {{other_character}}\'s hand',
            '{{character}} holds {{other_character}}\'s hand to their cheek',
            '{{character}} gazes into {{other_character}}\'s eyes while kissing their hand',
            '{{character}} intertwines their fingers with {{other_character}}\'s before kissing their hand',
            '{{character}} lifts {{other_character}}\'s hand to their mouth',
            '{{character}} presses a tender kiss to {{other_character}}\'s knuckles',
            '{{character}} slowly traces {{other_character}}\'s fingers with their lips'
        ],
        'confirmations': [
            '{{other_character}} blushes at the gesture',
            '{{other_character}} smiles warmly at {{character}}',
            '{{other_character}} squeezes {{character}}\'s hand back',
            '{{other_character}} leans closer to {{character}}',
            '{{other_character}} returns the gaze',
            '{{other_character}} thanks {{character}} quietly'
        ],
        'rejections': [
            '{{other_character}} pulls their hand away',
            '{{other_character}} looks uncomfortable',
            '{{other_character}} steps back from {{character}}',
            '{{other_character}} avoids eye contact',
            '{{other_character}} clears their throat awkwardly'
        ]
    },
    {
        'name': 'kiss_cheek',
        'description': 'kiss cheek of the other chara',
        'examples': [
            '{{character}} leans towards {{other_character}} and kisses {{other_character}}\'s cheek',
            '{{character}} gently plants a kiss on {{other_character}}\'s cheek',
            '{{character}} softly presses lips against {{other_character}}\'s cheek',
            '{{character}} approaches {{other_character}}, smiling, then kisses {{other_character}}\'s cheek',
            '{{character}} whispers something sweet into {{other_character}}\'s ear before kissing {{other_character}}\'s cheek',
            '{{character}} reaches out and affectionately kisses {{other_character}}\'s cheek',
            '{{character}} warmly embraces {{other_character}} and kisses {{other_character}}\'s cheek',
            '{{character}} comfortingly wraps arm around {{other_character}} and tenderly kisses {{other_character}}\'s cheek',
            '{{character}} appreciatively thanks {{other_character}} with a gentle kiss on the cheek'
        ],
        'confirmations': [
            '{{other_character}} blushes slightly and smiles back at {{character}}',
            '{{other_character}} chuckles and returns the gesture, giving a quick peck on {{character}}\'s cheek',
            '{{other_character}} shyly giggles and leans closer to {{character}}',
            '{{other_character}} gazes into {{character}}\'s eyes and moves even closer, reciprocating the kiss',
            '{{other_character}} feels flattered by {{character}}\'s affectionate act, responding positively',
            '{{other_character}} seems touched and responds with a loving smile'
        ],
        'rejections': [
            '{{other_character}} awkwardly pulls back and avoids eye contact',
            '{{other_character}} hesitates before taking a step back, looking uncomfortable',
            '{{other_character}} tries to maintain distance and politely declines',
            '{{other_character}} raises a hand in protest, creating some space between them and {{character}}',
            '{{other_character}} ducks away while averting \' gaze, displaying discomfort',
            '{{other_character}} frowns and steps aside, signaling that they aren\'t interested in such gestures'
        ]
    },
    {
        'name': 'kiss_forehead',
        'description': 'kiss forehead of the other chara',
        'examples': [
            '{{character}} leans in and kisses {{other_character}} on the forehead',
            '{{character}} gently presses their lips to {{other_character}}\'s forehead',
            '{{character}} softly plants a kiss on {{other_character}}\'s forehead',
            '{{character}} reaches out and kisses {{other_character}}\'s forehead',
            '{{character}} approaches {{other_character}} and kisses them on the forehead',
            '{{character}} moves closer to {{other_character}} and kisses their forehead',
            '{{character}} steps towards {{other_character}} and gives them a kiss on their forehead',
            '{{character}} gets nearer to {{other_character}} and presses a kiss to their forehead',
            '{{character}} comes close to {{other_character}} and kisses their forehead affectionately',
            '{{character}} draws close to {{other_character}} and plants a tender kiss on their forehead'
        ],
        'confirmations': [
            '{{other_character}} smiles',
            '{{other_character}} blushes',
            '{{other_character}} giggles',
            '{{other_character}} closes their eyes',
            '{{other_character}} sighs contentedly',
            '{{other_character}} leans into the kiss'
        ],
        'rejections': [
            '{{other_character}} turns their head away',
            '{{other_character}} pulls back',
            '{{other_character}} frowns',
            '{{other_character}} looks uncomfortable',
            '{{other_character}} pushes {{character}} away'
        ]
    },
    {
        'name': 'kiss_lips',
        'description': 'kiss the other chara',
        'examples': [
            '{{character}} leans in and kisses {{other_character}} on the lips',
            '{{character}} presses their lips against {{other_character}}\'s lips',
            '{{character}} and {{other_character}} share a passionate kiss',
            '{{character}} initiates a tender kiss with {{other_character}}',
            '{{character}} softly brushes their lips against {{other_character}} mouth',
            '{{character}} pulls {{other_character}} in for a deep kiss',
            '{{character}} and {{other_character}} exchange a quick peck on the lips',
            '{{character}} can\'t help but steal a kiss from {{other_character}}',
            '{{character}} plants a gentle kiss on {{other_character}}\'s lips',
            '{{character}} and {{other_character}} engage in a lingering kiss',
            '{{character}} whispers sweet nothings as they kiss {{other_character}}'
        ],
        'confirmations': [
            '{{other_character}} blushes and enjoys the kissing with {{character}}',
            '{{other_character}} returns the kiss',
            '{{other_character}} sighs contentedly after the kiss',
            '{{other_character}} smiles at {{character}} after the kiss',
            '{{other_character}} wraps their arms around {{character}} during the kiss'
        ],
        'rejections': [
            '{{other_character}} turns their head away from the kiss',
            '{{other_character}} stiffens up during the kiss',
            '{{other_character}} pulls back abruptly from the kiss',
            '{{other_character}} looks uncomfortable after the kiss',
            '{{other_character}} wipes their lips after the kiss'
        ]
    },
    {
        "name": "push_away",
        "description": "push away the other chara",
        "examples": [
            "{{character}} forcefully pushes {{other_character}} away",
            "{{character}} pushes {{other_character}} with both hands",
            "{{character}} shoves {{other_character}} aside",
            "{{character}} nudges {{other_character}} out of the way",
            "{{character}} elbows {{other_character}} out of the way",
            "{{character}} forcefully moves {{other_character}} backwards",
            "{{character}} makes {{other_character}} stumble back",
            "{{character}} sends {{other_character}} flying with a powerful push",
            "{{character}} uses their arm to push {{other_character}} back"
        ],
        "confirmations": [
            "{{other_character}} falls backwards",
            "{{other_character}} loses balance and topples over",
            "{{other_character}} steps back surprisedly",
            "{{other_character}} recoils from the sudden movement",
            "{{other_character}} takes a step back from {{character}}"
        ],
        "rejections": [
            "{{other_character}} resists the push",
            "{{other_character}} grabs onto something nearby to keep standing",
            "{{other_character}} braces themselves against the impact",
            "{{other_character}} resists the attempt and remains steady",
            "{{other_character}} sidesteps the push easily",
            "{{other_character}} counters with a push of their own",
        ]
    },
]


# CountenanceHandler - module main class
class MovementHandler(HarmonyClientModuleBase):
    def __init__(self, entity_controller, movement_config):
        # execute the base constructor
        HarmonyClientModuleBase.__init__(self, entity_controller=entity_controller)
        # Set config
        self.config = movement_config
        # Movement related data
        self.animations_map = {}

        # Debug trigger for building animation list
        if int(self.config["debug_mode"]) == 2:
            self._debug_print_animation_list()

    def _debug_print_animation_list(self):
        # Debug: List all Animations existing in the game
        #
        # REMARK:
        # This was the quickest hacky way to get the full animation list out of Chara Studio
        # Coding this code above to iterate through objects was way more effort than it should be.
        # But anyways, it's done now.
        # Commented out sections can be used for little more detail, but it's mostly empty in my case, so not worth it.
        #

        # Get Info Object, which holds all the data we need
        info = Info.Instance
        # print(json.dumps(dir(info))) -> dir() is helpful to get an idea of what the structure of an object even is

        animations = {}
        animation_groups = dict(info.dicAGroupCategory)
        for group_id, group_info in animation_groups.items():
            animations[group_id] = {
                "name": group_info.name,
                "categories": {}
            }
            categories = dict(animation_groups[group_id].dicCategory)
            # print(json.dumps(categories))
            for category_id, category_name in categories.items():
                # Not all groups which exist in the Group Category list exist / have animations;
                # this may cause reference errors, therefore double check here if the values exist
                if group_id in info.dicAnimeLoadInfo:
                    animation_info_group = info.dicAnimeLoadInfo[group_id]
                    if category_id in animation_info_group:
                        # Iterate over category items and add them to the animations list
                        animation_items = dict(animation_info_group[category_id])
                        animations[group_id]["categories"][category_id] = {
                            "name": category_name,
                            "animation_items": [],
                            "animation_item_details": {}
                        }
                        for item_info in animation_items.values():
                            animations[group_id]["categories"][category_id]["animation_items"].append(item_info.name)
                            # animations[group_id]["categories"][category_id]["animation_items"][item_info.name] = dir(item_info)
                            animations[group_id]["categories"][category_id]["animation_item_details"][item_info.name] = {
                                "bundlePath": item_info.bundlePath,
                                "clip": item_info.clip,
                                "fileName": item_info.fileName,
                                "manifest": item_info.manifest,
                                "name": item_info.name,
                                # "option": item_info.option, -> Not serializable
                            }

        # Print list to console
        # print(json.dumps(animations))

        # Write to output file in chara dir
        animation_data = json.dumps(animations)
        file_handle = open('animation_list.json', 'w')
        file_handle.write(animation_data)
        file_handle.close()

        # raise RuntimeError("Dont want to start if debug")

    def init_animations_map(self):
        # This creates a map of
        self.animations_map = {

        }


    def handle_event(
        self,
        event  # HarmonyLinkEvent
    ):
        # AI State update
        # if event.event_type == EVENT_TYPE_AI_STATUS and event.status == EVENT_STATE_DONE:
        #     self.update_ai_state(ai_state=event.payload)
        #     # Update face expression based on status context
        #     self.update_chara_from_state()
        #
        # if event.event_type == EVENT_TYPE_AI_COUNTENANCE_UPDATE and event.status == EVENT_STATE_DONE:
        #     self.update_countenance_state(countenance_state=event.payload)
        #     # Update face expression based on status context
        #     self.update_chara_from_state()

        # if event.event_type == EVENT_TYPE_AI_SPEECH and event.status == EVENT_STATE_DONE:
        #
        #     utterance_data = event.payload
        #
        #     if utterance_data["type"] == "UTTERANCE_NONVERBAL" and len(utterance_data["content"]) > 0:
        #         # Update face expression based on nonverbal action context
        #         self.update_chara_from_action(utterance_data["content"])

        return

    def update_chara_from_state(self):
        if self.chara is None or self.countenance_state is None:
            return

        # Update Countenance
        # self.countenance_update('', self.countenance_state.emotional_state, self.countenance_state.facial_expression)

    # def countenance_update(self, gender, emotion_name, expression_name):
    #     emotion = emotions_default['neutral']
    #     if emotion_name in emotions_default:
    #         emotion.update(emotions_default[emotion_name])
    #
    #     expression = expressions_default['normal']
    #     if expression_name in expressions_default:
    #         expression.update(expressions_default[expression_name])
    #
    #     # Check for gender specific emotions
    #     if gender == "F" and emotion_name in emotions_female:
    #         emotion = emotions_female['neutral']
    #         if emotion_name in emotions_female:
    #             emotion.update(emotions_female[emotion_name])
    #
    #         expression = expressions_female['normal']
    #         if expression_name in expressions_female:
    #             expression.update(expressions_female[expression_name])
    #     elif gender == "M" and emotion_name in emotions_male:
    #         emotion = emotions_male['neutral']
    #         if emotion_name in emotions_male:
    #             emotion.update(emotions_male[emotion_name])
    #
    #         expression = expressions_male['normal']
    #         if expression_name in expressions_male:
    #             expression.update(expressions_male[expression_name])
    #
    #     # Expression on top of emotion
    #     target_state = emotion
    #     target_state.update(expression)
    #
    #     for function in target_state:
    #         if function in char_act_funcs:
    #             char_act_funcs[function][0](self.chara.actor, target_state[function])
