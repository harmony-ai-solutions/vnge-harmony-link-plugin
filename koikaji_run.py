# Execution test script
# (c) 2023 RuntimeRacer (runtimeracer@gmail.com)
#
# This script simulates the part of initializing VNGE & all support libs for testing the initialization flow
# However, it cannot test the actual game loop
#

import sys
sys.path.append(r"E:\Koikatsu Party After Party\BepInEx\plugins\Console")
sys.path.append(r"E:\Koikatsu Party After Party\CharaStudio_Data\Managed")

import clr
# Pre-Load
# clr.AddReference('Microsoft.Scripting.Metadata')
# clr.AddReference('Microsoft.Scripting.Core')
# clr.AddReference('Microsoft.Scripting')
# clr.AddReference('Microsoft.Dynamic')
# clr.AddReference('Unity.Console')
# clr.AddReference('Assembly-UnityScript')
# clr.AddReference('IronPython')
# clr.AddReference('IronPython.Modules')

# Hot-Load
clr.AddReference('StdLib')
clr.AddReference('UnityEngine')
clr.AddReference('UnityEngine.UI')
clr.AddReference('Unity.Python.Modules')
clr.AddReference('Assembly-CSharp')
clr.AddReference('Assembly-CSharp-firstpass')
clr.AddReference('InputSimulator')
clr.AddReference('NLayer')

import koikaji


class FakeGData:
    def __init__(self):
        pass


class FakeGameObj:
    def __init__(self):
        self.init_start_params()

    def init_start_params(self):
        self.isShowDevConsole = False

        self.isSceneAutorunAnimDisabled = False

        # menu
        self._menuStack = []
        self.menu_result = None

        self.isHideGameButtons = False
        self.onSetTextCallback = None
        self.camAnimeTID = -1  # timer id for camera animation
        self.onDumpSceneOverride = None

        self.isHideWindowDuringCameraAnimation = False

        self.isFuncLocked = False
        self.funcLockedText = "SYSTEM: Unknown default lock"

        # some settings - may be localized
        self.btnNextText = "Next >"
        # self.autostart = False
        # self.isDevDumpButtons = False - no use
        self.sceneDir = ""

        self.gdata = FakeGData()
        self.gpersdata = {}
        self.scenedata = FakeGData()

        self._scenef_actors = {}  # for actors
        self._scenef_props = {}  # for props

        self.current_game = ""

        # lip sync
        self.isfAutoLipSync = False
        self.fAutoLipSyncVer = "v10"

        self.readingChar = None
        self.readingSpeed = 12.0
        self.readingProgress = 0
        self.lipAnimeTID = -1  # timer id for lip sync animation

        # self._eventListenerDic = {}

        # advanced clean, keep persistent stuff
        # for eventid in self._eventListenerDic:
        #     newlis = []
        #     for evt in self._eventListenerDic[eventid]:
        #         if evt[2]:  # if persistent
        #             newlis.append(evt)
        #     self._eventListenerDic[eventid] = newlis
        #
        # self.windowStyle = self.windowStyleDefault
        # self.skin_set(self.skin_default)


# Run game start method
koikaji.start(FakeGameObj())
