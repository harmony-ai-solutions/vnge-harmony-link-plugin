#vngame;all;Utilities/Scene Save State
from vngameengine import vnge_version
mod_version = vnge_version
"""
SceneSaveState
For HS NEO, PlayHome Studio, Koikatsu CharaStudio
(Lightweight version of SceneConsole mod)

Allows you to:
- save/load scene states and cameras inside scene
- export this states as VNSceneScript (to use in VNs)

Usage:
- load/create scene
- add some charas or folders/items to tracking list ("Tracking" tab)
- change theirs properties and save this changes as state ("Add Scene" button)
- switch between scenes and cameras

By @keitaro1978 
Original code was made by @chickenManX to SceneConsole mod (thanks!)
Some cool features (including Wizard for cmds) by @countd360

1.1
- fixed a non-loading bug
1.2
- fixed a Vector2 bug in PlayHome
2.0
- depends on libjsoncoder lib
- added posesavestate (as Pose Library)
- added sceneutils (as Scene Utils)
- return auto-backup during close
- adapted for skin system 
2.0.1
- small bugfix for saving props in posesavestate
2.5
- ability to save scene sys environment in states (Track/UnTrack in Tracking menu)
3.0
- faces lib
- sceneutils contain body changer
3.1
- fixed bug with duplicate keyboard shortcuts processing
- advanced option: "Try to skip clothes change during scene change"
- VNSceneScript export changed: scene will be saved in VN only if Cam 1 is VN cam, otherwise skipped
4.0
- !!Optimized compact save!!
- function "Copy selected status to tracking char with same name"
- VN: help buttons for switch between "Who say" (from VNFrame, thanks to @countd360)
- VN: export/import cam texts to external text file - so, you can edit script in text editor if you want
5.0
- VN: added button "Delete (X)" and "..." for "What say"
- some bugs fixed (tracking and close)
- VN: adv vn cmds available
- VN: redone output for VNSceneScript - updated to 2.5, vnframe12
- VN: fixed bug for non-correct VN output for AdvancedIK (NEO)
6.0
- "Ministates" tab
- buttons for animated move to cameras
- "Tracking" tab - fast buttons to hide/show and select actor/prop
- autostates elements
6.5
- ministates sorted by alphabet
- ministates optimized layout for scrolling
- "verify save" function
- !!optimized in-scene save, that reuses old folders
- on close - backup is made only if save != current scene set (verify check used)
- correct rendering of camera (with 3 decimals after ,) - thanks to @countd360
- VNSS export supports "clothes skip" option - thanks to @countd360 (this maybe temporarily)
- support camera anim render - use camoanim:{camstr} call (more options will be available later)
- NEO: fixed bug with "CheckSelect" error in 6.0
6.6
- return always backup back
- backup is auto-make to file (name_backup) or (backup_backup) (it's quick) 
- more correct Verify save data
7.0
- auto-backup by timer (you can change duration it in line self.backupTimeDuration = float(600) # seconds )
- run VN from arbitrary state after export
- !!VNAnime support (read vnscenescriptext_vnanime10.py for details)
- VN: "More" wizard page
- you can target cam using formula (scene*100+cam)  
- support {name} set for cams (you can name scene like "kitchen" and use cmd: addbtn:Go to kitchen:{kitchen})
- fixed bug with duplicate scene (correct copy made) 
- Wizard Adv Options 1: camera anim, hide, hideui, timernext, skip setting camera
- !!Cool wizard for Advanced commands (thanks to @countd360!)
- bug fix at line about 436: make a deepcopy for cam_addprops to avoid reference link.
- update at line about 1589 and 2827: make a function to run vnss. and build 3 run button beside export button. Because sometimes I just want to run VNSS, no need to export it again.
- update at line about 2915: when the first cam of a scene is named, scene will share the name with cam 0.
7.5
- bug fixed: now you can return to VNGE UI after Collapse/Expand function (UI wasn't restored before)
New config file scenesavestate_config.ini 
- your own default X,Y pos of Window
- your own default Window Width,Height (use with caution)
- auto-backup time duration
changes in VN Wizard by @countd360:
- Wizard: support 'next' keyword for addbtn/addbtnrnd cmd
- Wizard: support runms command, choice and name check for runms/addbtnms
- Wizard: VNFrame ext support track system info
PoseSaveState 2.1
- fix bug: empty Tags during save will lead to Base tag, not error
- X buttons for text fields during save
7.6
- Adv buttons: VN all cameras on/off
7.9
- beta support for NeoV2 (AI-Shoujo)
- SceneUtils 2.8 - support for AI-Shoujo, BodySliders
8.0
- SceneUtils 3.0 - with advanced support and interface for BodySliders, FaceSliders and setting VNActor's param
(thanks to countd360!! he did almost everything!)
- support for synch VN command - to sync actors in animation (setting AUX param)
- removed unnecessary console output
8.1
- PoseSaveState 2.2 - fix bug for no MFaces tab 
9.0 
- Check and run vnss advanced properties when switch cam. Allow to run VNAnime and VNFrame small animations in SSS.
- "Add selected" support track light and route
- Advanced: button "VN: add Fake Lip Sync Ext, if no". Add fake lip sync just in SSS!
9.8 (countd360)
- delete old cam name setting when create a new cam
-scenesavestate_vnssext.py
-v1.5
 - Detect necessary ext on export, support vnframe12,vnanime10,vntext10,objcam10,blackrain10,gameutil10
 - VNSS fast export mode: try update folders instead of delete and re-create all. EXPERIMENTAL, can be turn off in ini.
 - Skip export 'txtf' cmd when detect 'txtfv' or 'printvar' cmd (blackrain)
 - fix a bug param data linked after copy cam, back button can cancel param data change now.
 - Wizard: support 'f_height'/'f_breast'
 - Wizard: support some of the Blackrain commands
 - Wizard: support VNText commands
 - Wizard: support GameUtil commands
 - Wizard: VNFrame ext support manual mode
-sceneutil.py
-v3.2
 - add "VNText Editor" for every game engine 
10.0 (Keitaro)
- correct reg/unreg for update event
- button for Clear scenes
- handle on Studio scene load - if load, replace actual content of scenes (adjustable in .INI)
10.5
- Pose Library 3.0
- Support save: FStatus, MStatus, Left hand, Right hand
19.0
- synced with VNGE version
- support load/save from scene PNG file
30.0
- support load/save advanced data from scene PNG file
- pass param when export VNSS
- new ui for setup fake lip sync
- new ui for change char's color and title in dialog
- new button text for "Track scene environment" button
39.0
- optimized scene load sequence
- bug fix: scene number always start from 1
"""

from vngameengine import HSNeoOCIFolder, HSNeoOCI, HSNeoOCIProp, HSNeoOCILight, HSNeoOCIRoute, HSNeoOCIText, parseKeyCode
from vnactor import *
import vnframe
from Studio import OCIFolder, OCIChar, Studio, OCIItem, Studio
from UnityEngine import GUI, GUILayout, GUIStyle, GUIUtility, Screen, Rect, Vector3, Vector2, Input, KeyCode
from UnityEngine import Event, EventType, WaitForSeconds, GameObject, Color, Time
from System import String, Array
import os
from System import Single, Byte
import json
from json import encoder
import copy
import sys
# import codecs
# from poseconsole import ActorSC, PropSC
# import poseconsole
from libjsoncoder import *
import posesavestate
import scenesavestate_vnssext
from libministates import *

from vngameengine import BytesPNG2Texture2D, Texture2D2BytesPNG
from vnactor import bytearray_to_str64, str64_to_bytearray

_sc = None
""":type _sc:SceneConsole"""
_pc = None
_conv_dict = {}
_step = 0  # debug purpose

from vngameengine import import_or_reload
import_or_reload("vnactor")
import_or_reload("scenesavestate_vnssext")
import_or_reload("libministates")
#import_or_reload("sceneutils")
import posesavestate
#import_or_reload("posesavestate")

# :::::::::: JSON Derulo ::::::::::::
encoder.FLOAT_REPR = lambda o: format(o, '.3f')
from libjsoncoder import *

# --------------- autorun and in-scene save and load ---------------

def autorun_start(game):
    """:type game:vngameengine.VNNeoController"""
    if game.isClassicStudio:
        return

    global _sc
    #if _sc == None:
    _sc = SceneConsole(game)
    print 'autorun',len(_sc.block)

def scene_saved(game):
    """:type game:vngameengine.VNNeoController"""
    global _sc
    print "SSS: scene_saving..."
    game.dataPNG_save("vnge_sss",_sc.saveToStr(),_sc.versionSaveInSceneData)
    game.dataPNG_save("vnge_sssadv",_sc.saveAdvancedToStr(),_sc.versionSaveInSceneData)
    print "SSS: scene_saved!..."


def scene_loaded(game):
    """:type game:vngameengine.VNNeoController"""
    from extplugins import ExtensibleSaveFormat
    global _sc

    print "SSS: scene_loading..."
    data,version = game.dataPNG_load_checkversion("vnge_sss",["19.0","29.9"])
    if data != None:

        mas = _sc.loadFromStr(data)
        _sc.loadSceneDataInternalDict(mas,True,version)

        # set to first
        if len(_sc.block) > 0:
            _sc.cur_index = 0
            _sc.cur_cam = 0

        _sc.show_blocking_message_time_sc("Scene data was auto-loaded from file internals!")
        print "SSS: scene_loaded1!... version=",version
        #print data

    else:
        _sc.clear_scenes()
        print "SSS: scene_loaded2!..."

    # advanced data
    data,version = game.dataPNG_load_checkversion("vnge_sssadv",["29.9"])
    if data != None:
        mas = _sc.loadFromStr(data) # decode JSON
        _sc.loadAdvancedFromDict(mas)

    update_tlbBtn_state()


# :::::::::: For debug only ::::::::::::
newWndId = None

def start_toolbar(p1="",p2=""):
    from vngameengine import vnge_game
    start(vnge_game)

def start(game):
    """:type game:vngameengine.VNNeoController"""
    if game.isClassicStudio:
        game.show_blocking_message_time("This only for NEO-engines, sorry")
        return

    from vngameengine import tlbBtn_setColor, tlbBtn_VNGESSS
    from UnityEngine import Color



    if newWndId == None:
        game.gdata.hook_update_allowed = True

        # if _sc == None:
        #
        #     _sc = SceneConsole(game)

        print len(_sc.block)
        sceneConsoleGUIStart(game)

        game.scenef_register_actorsprops()

        # if no blocks - autoload
        if len(_sc.block) == 0:
            if HSNeoOCIFolder.find_single_startswith("-scenesavestate:") != None:
                _sc.loadSceneData()
                _sc.show_blocking_message_time_sc("Scene data was auto-loaded!")

        tlbBtn_setColor(tlbBtn_VNGESSS,Color.green)

    else:
        game.get_extra_window(newWndId).visible = not game.get_extra_window(newWndId).visible
        update_tlbBtn_state()


def update_tlbBtn_state():
    global newWndId
    global _sc

    from vngameengine import tlbBtn_setColor, tlbBtn_VNGESSS, tlbBtn_UpdateBtnColor
    from vngameengine import vnge_game

    if newWndId != None:
        tlbBtn_UpdateBtnColor(tlbBtn_VNGESSS, vnge_game.get_extra_window(newWndId).visible, len(_sc.block) > 0)
    else:
        tlbBtn_UpdateBtnColor(tlbBtn_VNGESSS, False, len(_sc.block) > 0)

# main class
class SceneConsole():
    def __init__(self, game):
        # init dict
        # initWordDict()

        # --- Some constants ---
        self._normalwidth = 500
        self._normalheight = 350
        # self.drag_rect = Rect(0, 0, 10000, 50)

        # --- Basic settings ---
        self.game = game
        """:type :vngameengine.VNNeoController"""
        self.originalwindowwidth = 0
        self.originalwindowheight = 0
        self.originalWindowCallback = None
        self.guiOnShow = False
        self.windowwidth = self._normalwidth
        self.windowheight = self._normalheight
        self.windowindex = 0
        self.subwinindex = 0

        # --- Essential Data ---
        self.versionSceneDataParsing = "7.0"
        self.versionSaveInSceneData = "29.9"


        self.dict = []
        self.sdict = []
        self.dictparse = {}
        self.scenefile = ""
        self.block = []
        self.basechars = [[], []]
        self.dupchars = [[], []]
        self.last_acc_id = 0
        self.all_acc = {}  # all acc dict (eg. {acc_id : acc object})
        self.baseacc = {}  # base acc (eg. {tree:{itemname:1}}) tree includes char name
        self.accstate = {}

        self.propfldtag = []
        self.basepropflds = {}
        self.proptag = []
        self.baseprops = {}

        # self.basechars = self.getAllBaseChars()
        # self.dupchars = self.getAllDupChars()
        # self.updateNameset()

        # :::: UI Data ::::
        self.consolenames = Array[String](("SceneSaveState", "Pose Library", "Scene Utils", "Clip Manager"))
        self.options = Array[String](("Edit", "Tracking", "Load/Save", "Advanced", "Ministates"))
        self.warning_param = None  # tuple for warning_win func
        # -- Main --
        self.sel_font_col = "#f24115"  # font color for selected
        self.nor_font_col = "#f9f9f9"  # font color for not-selected

        self.scene_scroll = Vector2(0, 0)
        self.cam_scroll = Vector2(0, 0)
        # self.mset_scroll = Vector2(0, 0)
        # self.fset_scroll = Vector2(0, 0)
        self.miniset_scroll = Vector2(0, 0)
        self.tracking_scroll = Vector2(0, 0)
        self.saveload_scroll =  Vector2(0, 0)
        self.fset_index = 0  # Current fem index
        self.mset_index = 0  # Current male index
        self.viewwidth = 180
        self.viewheight = 200
        self.camviewwidth = 120
        # self.char_name = ""
        self.cam_whosay = ""
        self.cam_whatsay = ""
        self.cam_addvncmds = ""
        self.cam_addparam = False
        self.cam_addprops = {"a1": False, "a2": False}

        self.newid = ""
        self.newCharColor = ""
        self.newCharTitle = ""
        self.mininewid = ""
        self.autoshownewid = ""
        self.isUseMsAuto = False

        self.uiTrackingShowAdvanced = False

        self.uiShowLoadSave = not game.isSceneDataSaveSupported

        # -- Load/Save --
        self.svname = ""
        self.ldname = ""
        # self.optionint = 0



        # -- Advanced --
        self.adv_scroll = Vector2(0, 0)
        self.temp_states = None
        self.charname = ""
        self.autoLoad = True
        self.autoAddCam = True
        self.promptOnDelete = True
        self.skipClothesChanges = False
        self.vnExportFakeLipSync = False
        self.vnExportFakeLipSyncVer = "v10"
        self.vnExportFakeLipSyncSpd = "12.0"
        self.shortcuts = {}  # shortcuts dict (init with loadConfig)

        self.paramAnimCamDuration = "1.5"
        self.paramAnimCamStyle = "fast-slow"
        self.paramAnimCamZoomOut = "0.0"
        self.paramAnimCamIfPossible = is_ini_value_true("AnimateCamIfPossible")

        self.paramSceneListShowThumb = is_ini_value_true("SceneListShowThumb",True)
        self.paramSceneListShowLabel = is_ini_value_true("SceneListShowLabel",True)

        self.HideAddSelectedToTrackInPreviousScenes = is_ini_value_true("HideAddSelectedToTrackInPreviousScenes", False)
        self.AddCamInsertsRightAfter = is_ini_value_true("AddCamInsertsRightAfter", False)

        # self.nwindowRect = None

        # -- Edit window --
        # Common data
        #self.nameset = [[],
        #                []]  # Array[Array[String]](((),())) #,Array[String](())] # nameset[0] = female names, nameset[1] = male names
        #self.scene_strings = []
        #self.scene_str_array = Array[String](())
        #self.scene_cam_str = Array[String](())
        self.cur_index = -1  # Current scene index
        self.prev_index = -1
        self.cur_cam = -1
        self.prev_cam = -1

        self.camset = []

        self.clipboard_status = {}
        self.clipboard_status2 = {}

        self.isSaveCompact = True
        self.isSaveVerify = True
        self.isSaveOld = False

        self.updAutoStatesTimer = 0
        self.arAutoStatesItemsVis = []
        self.arAutoStatesItemsChoice = []

        self.backupTimeDuration = float(get_ini_value_def_int("AutoBackupTimeInSeconds", 600)) #float(600) # seconds
        self.backupTimeCur = self.backupTimeDuration

        self.vnFastIsRunImmediately = False
        self.vnExportToPNG = False
        if game.isSceneDataSaveSupported:
            self.vnExportToPNG = True

        # blocking message
        self.funcLockedText = "..."
        self.isFuncLocked = False

        # skin_default internal
        import skin_default
        self.skinDefault = skin_default.SkinDefault()
        self.skinDefault.controller = game
        self.skinDefault_sideApp = ""

        # skin for console
        from skin_customwindow import SkinCustomWindow
        skin = SkinCustomWindow()
        skin.funcSetup = sceneConsoleSkinSetup
        skin.funcWindowGUI = sceneConsoleSkinWindowGUI
        self.skin = skin

        # hook
        self.hook_update_allowed = True

    # Blocking message functions
    def show_blocking_message(self, text="..."):
        self.funcLockedText = text
        self.isFuncLocked = True

    def hide_blocking_message(self, game=None):
        self.isFuncLocked = False

    def show_blocking_message_time_sc(self, text="...", duration=3):
        self.show_blocking_message(text)
        self.game.set_timer(duration, self.hide_blocking_message)

    # other
    #def updateSceneStrings(self):
    #    self.scene_strings = []
    #    for id in range(0, len(self.block)):
    #        self.scene_strings.append("Scene %d" % (id + 1))
    #    self.scene_str_array = Array[String](self.scene_strings)

    def clear_scenes(self):
        self.block = []
        self.cur_index = -1
        #self.scene_strings = []
        #self.scene_str_array = Array[String](self.scene_strings)



    # ---------- ministates ------------
    def addSelectedAutoShow(self, param):
        # get list of sel objs
        arSel = self.get_selected_objs()

        if len(arSel) == 0:
            self.show_blocking_message_time_sc("No selection!")
            return

        for actprop in arSel:
            #print actprop

            #if hasattr(actprop, 'as_prop'):
            if isinstance(actprop,HSNeoOCIChar):
                pass # not for chars!
                #id = self.find_item_in_objlist(actprop.objctrl)
            else:
                txtname = self.autoshownewid
                if txtname == "":
                    txtname = actprop.text_name

                fld = HSNeoOCIFolder.add("-msauto:"+param+":"+txtname)
                #objSave["__id%s"%(str(id))] = actprop.export_full_status()
                fld.set_parent(actprop)

        recalc_autostates()
        self.autoshownewid = ""

    def delSelectedAutoShow(self):
        # get list of sel objs
        arSel = self.get_selected_objs()

        if len(arSel) == 0:
            self.show_blocking_message_time_sc("No selection!")
            return

        arSel0 = arSel[0]

        folders = HSNeoOCIFolder.find_all_startswith("-msauto:")
        for folder in folders:
            if folder.treeNodeObject.parent == arSel0.treeNodeObject:
                folder.delete()

        recalc_autostates()


    def addSelectedMini(self):
        # find mini

        fld = HSNeoOCIFolder.find_single("-ministates:1.0")
        if fld == None:
            fld = HSNeoOCIFolder.add("-ministates:1.0")


        # calc name
        name = self.mininewid
        if name == "":
            name = "state"

        # get list of sel objs
        arSel = self.get_selected_objs()

        if len(arSel) == 0:
            self.show_blocking_message_time_sc("No selection!")
            return

        objSave = {}
        for actprop in arSel:
            #if isinstance(actprop, Actor):
            id = self.find_item_in_objlist(actprop.objctrl)
            objSave["__id%s"%(str(id))] = actprop.export_full_status()
            #elif isinstance(actprop, Actor):
        #print objSave

        fldName = folder_add_child(fld,name)
        for k in objSave:
            #fldObj = folder_add_child(fldName,json_encode(objSave))
            folder_add_child(fldName,json_encode({k: objSave[k]}))

        # fldName = HSNeoOCIFolder.add(name)
        # fldName.set_parent(fld)
        #
        # fldObj = HSNeoOCIFolder.add(json_encode(objSave))
        # fldObj.set_parent(fldName)

        self.mininewid = ""

    def find_item_in_objlist(self, obj):
        dobjctrl = self.game.studio.dicObjectCtrl
        for key in dobjctrl.Keys:
            objctrl = dobjctrl[key]
            if objctrl == obj:
                return key

        return None

    def get_selected_objs(self):
        mtreeman = self.game.studio.treeNodeCtrl
        ar = []
        for node in mtreeman.selectNodes:
            ochar = HSNeoOCI.create_from_treenode(node)
            # ar.append(HSNeoOCI.create_from_treenode(node))
            if isinstance(ochar, HSNeoOCIChar):
                ar.append(ochar.as_actor)
            else:
                ar.append(ochar.as_prop)
        return ar

    # Add stuff
    def addScene(self, insert=False):
        if insert == False:
            self.cur_index = len(self.block)
            self.prev_index = self.cur_index
        else:
            self.cur_index += 1
        self.block.insert(self.cur_index, Scene())

        #self.updateSceneStrings()

    #def getSceneCamString(self):
    #    cam_str = []
    #    for i in range(0, len(self.block[self.cur_index].cams)):
    #        cam_str.append("Cam " + str(i))
    #    self.scene_cam_str = Array[String](cam_str)

    def addCam(self, showMessage=False):
        self.changeSceneCam("add")
        if showMessage:
            self.game.logger_log_message("Cam added!", "SSS: ")

    def addCamWithMessage(self):
        self.addCam(True)

    def changeSceneCam(self, task=""):
        #global _sc
        studio = Studio.Instance
        c = studio.cameraCtrl
        cdata = c.cameraData
        # fov = cdata.parse
        import copy
        addata = {'addparam':self.cam_addparam, 'whosay': self.cam_whosay, 'whatsay': self.cam_whatsay, 'addvncmds': self.cam_addvncmds, "addprops": copy.deepcopy(self.cam_addprops) }
        cam_data = (cdata.pos, cdata.distance, cdata.rotate, cdata.parse, addata)
        if task == "" or task == "add":
            if "a1o" in addata["addprops"]:
                addata["addprops"]["a1o"]["name"] = ""
            self.cur_cam = self.block[self.cur_index].addCam(cam_data)

        elif task == "upd":
            self.block[self.cur_index].updateCam(self.cur_cam, cam_data)
        elif task == "del":
            self.cur_cam = self.block[self.cur_index].deleteCam(self.cur_cam)
            if self.cur_cam > -1:
                self.setCamera()
        #if not task == "upd":
        #    self.getSceneCamString()

    def setCamera(self, isAnimated = None):
        camera_data = self.block[self.cur_index].cams[self.cur_cam]

        if isAnimated == None:
            isAnimated = self.paramAnimCamIfPossible

        # check and run adv command
        keepCamera = False
        if len(camera_data) > 4:
            keepCamera = scenesavestate_vnssext.runAdvVNSS(self, camera_data[4])

        # actual set
        if keepCamera:
            pass
        elif isAnimated:
            # self.game.anim_to_camera(1.5, pos=camera_data[0], distance=camera_data[1], rotate=camera_data[2], fov=camera_data[3], style={'style': "fast-slow",'target_camera_zooming_in': 2})
            style = {'style': "fast-slow"}
            if get_ini_value_def_int("ExpCameraQuatNotVect",1) == 1:
                style['rot_lerp'] = 1
            if float(self.paramAnimCamZoomOut) != 0.0:
                style['target_camera_zooming_in'] = float(self.paramAnimCamZoomOut)

            self.game.anim_to_camera(float(self.paramAnimCamDuration), pos=camera_data[0], distance=camera_data[1], rotate=camera_data[2],
                                     fov=camera_data[3], style=style)
        else:
            self.game.move_camera(pos=camera_data[0], distance=camera_data[1], rotate=camera_data[2], fov=camera_data[3])

        if len(camera_data) > 4:
            addata = camera_data[4]
            self.cam_addparam = addata["addparam"]
            self.cam_whosay = addata["whosay"]
            self.cam_whatsay = addata["whatsay"]
            if "addvncmds" in addata:
                self.cam_addvncmds = addata["addvncmds"]
            else:
                self.cam_addvncmds = ""

            if "addprops" in addata:
                self.cam_addprops = addata["addprops"]
            else:
                self.cam_addprops = {"a1":False,"a2":False}
        else:
            self.cam_addparam = False
            self.cam_whosay = ""
            self.cam_whatsay = ""
            self.cam_addvncmds = ""
            self.cam_addprops = {"a1": False, "a2": False}

    def addAuto(self, insert=False, addsc=True, allbase=True):
        if addsc == True:
            self.addScene(insert)
            if self.autoAddCam == True:
                self.changeSceneCam("add")

        curscene = self.block[self.cur_index]
        """:type curscene:Scene"""
        options = {}
        if self.isSysTracking():
            options["sys"] = True
        curscene.importCurScene(self.game, options)

        self.game.logger_log_message("Scene added!", "SSS: ")



    # Remove stuff
    def removeScene(self):
        if len(_sc.block) > 0:
            self.block.pop(_sc.cur_index)
            _sc.cur_index = _sc.cur_index - 1
            #self.scene_strings.pop(-1)
            #self.scene_str_array = Array[String](self.scene_strings)



    # Load scene
    def loadCurrentScene(self, setZeroCamera = True):
        self.setSceneState()
        if setZeroCamera:
            if len(_sc.block) > 0 and len(self.block[self.cur_index].cams) > 0:
                self.cur_cam = 0
                self.setCamera()

    def setSceneState(self, index=None):
        if index == None:
            index = self.cur_index

        curscene = self.block[index]
        """:type curscene:Scene"""
        curscene.setSceneState(self.game)

    def copySelectedStatusToTracking(self, exclude = []):
        elem = HSNeoOCI.create_from_selected()
        if isinstance(elem, HSNeoOCIChar):
            tmp_status = elem.as_actor.export_full_status()
            actors = self.game.scenef_get_all_actors()
            for key in actors:
                actor = actors[key]
                if actor.text_name == elem.as_actor.text_name:
                    for keyEx in exclude:
                        del tmp_status[keyEx]
                    actor.import_status(tmp_status)
                    return

            self.show_blocking_message_time_sc("Can't find tracking char with same name")
        else:
            self.show_blocking_message_time_sc("Can't copy status")

    def copySelectedStatus(self):
        elem = HSNeoOCI.create_from_selected()
        if isinstance(elem, HSNeoOCIChar):
            self.clipboard_status = elem.as_actor.export_full_status()

        elif isinstance(elem, HSNeoOCIProp):
            self.clipboard_status = elem.as_prop.export_full_status()

        else:
            self.show_blocking_message_time_sc("Can't copy status")



    def pasteSelectedStatus(self):
        elem = HSNeoOCI.create_from_selected()
        if isinstance(elem, HSNeoOCIChar):
            elem.as_actor.import_status(self.clipboard_status)

        elif isinstance(elem, HSNeoOCIProp):
            elem.as_prop.import_status(self.clipboard_status)

        else:
            self.show_blocking_message_time_sc("Can't paste status")

    def copySelectedStatus2(self):
        elem = HSNeoOCI.create_from_selected()
        if isinstance(elem, HSNeoOCIChar):
            self.clipboard_status2 = elem.as_actor.export_full_status()

        elif isinstance(elem, HSNeoOCIProp):
            self.clipboard_status2 = elem.as_prop.export_full_status()

        else:
            self.show_blocking_message_time_sc("Can't copy status 2")



    def pasteSelectedStatus2(self):
        elem = HSNeoOCI.create_from_selected()
        if isinstance(elem, HSNeoOCIChar):
            elem.as_actor.import_status(self.clipboard_status2)

        elif isinstance(elem, HSNeoOCIProp):
            elem.as_prop.import_status(self.clipboard_status2)

        else:
            self.show_blocking_message_time_sc("Can't paste status 2")

    def isSysTracking(self):
        if len(self.block) > 0:
            if "sys" in self.block[0].actors:
                return True

        return False

    def addSysTracking(self):
        if len(self.block) > 0:
            curstatus = export_sys_status(self.game)
            for i in range(len(self.block)):
                scene = self.block[i]
                scene.actors["sys"] = curstatus
        else:
            _sc.show_blocking_message_time_sc("Please, add at least 1 state to add system environment tracking")

    def delSysTracking(self):
        for i in range(len(self.block)):
            scene = self.block[i]
            del scene.actors["sys"]

    def addSelectedToTrack(self):
        elem = HSNeoOCI.create_from_selected()
        if elem == None:
            self.show_blocking_message_time_sc("Nothing selected")
            return

        if isinstance(elem, HSNeoOCIChar):
            actors = self.game.scenef_get_all_actors()

            id = ""
            for i in range(0,1000):
                id = "act"+str(i)
                if id in actors:
                    pass
                else:
                    break

            tagfld = HSNeoOCIFolder.add("-actor:"+id)
            tagfld.set_parent_treenodeobject(elem.treeNodeObject.child[0].child[0])

            self.game.scenef_register_actorsprops()

            curstatus = elem.as_actor.export_full_status()
            # CertainLSP: If enabled, copy curstatus into a new dictionary, set visible to false, then use this dictionary for all previous scenes
            #
            # for i in range(len(self.block)):
            #     scene = self.block[i]
            #     scene.actors[id] = curstatus
            #
            if self.HideAddSelectedToTrackInPreviousScenes:
                curstatusinvisible = dict(curstatus)
                curstatusinvisible["visible"] = 0
                for i in range(0, self.cur_index):
                    scene = self.block[i]
                    scene.actors[id] = curstatusinvisible
            else:
                for i in range(0, self.cur_index):
                    scene = self.block[i]
                    scene.actors[id] = curstatus

        elif isinstance(elem, HSNeoOCIProp):

            props = self.game.scenef_get_all_props()

            id = ""
            for i in range(0, 1000):
                id = "prp" + str(i)
                if id in props:
                    pass
                else:
                    break

            if isinstance(elem, HSNeoOCILight):
                tagfld = HSNeoOCIFolder.add("-propchild:" + id)
                elem.set_parent(tagfld)
            elif isinstance(elem, HSNeoOCIRoute):
                tagfld = HSNeoOCIFolder.add("-propgrandpa:" + id)
                tagfld.set_parent_treenodeobject(elem.treeNodeObject.child[0])
            elif isinstance(elem, HSNeoOCIText):
                tagfld = HSNeoOCIFolder.add("-propchild:" + id)
                elem.set_parent(tagfld)
            else:
                tagfld = HSNeoOCIFolder.add("-prop:" + id)
                tagfld.set_parent_treenodeobject(elem.treeNodeObject)

            self.game.scenef_register_actorsprops()

            curstatus = elem.as_prop.export_full_status()
            # CertainLSP: If enabled, copy curstatus into a new dictionary, set visible to false, then use this dictionary for all previous scenes
            #
            # for i in range(len(self.block)):
            #     scene = self.block[i]
            #     scene.props[id] = curstatus
            #
            if self.HideAddSelectedToTrackInPreviousScenes:
                curstatusinvisible = dict(curstatus)
                curstatusinvisible["visible"] = 0
                for i in range(0, self.cur_index):
                    scene = self.block[i]
                    scene.props[id] = curstatusinvisible
            else:
                for i in range(0, self.cur_index):
                    scene = self.block[i]
                    scene.props[id] = curstatus

        # updating set

    def changeSelTrackID(self, toId):
        if toId == "":
            self.show_blocking_message_time_sc("Please, set ID to change to first")
            return

        elem = HSNeoOCI.create_from_selected()

        if elem == None:
            self.show_blocking_message_time_sc("Nothing selected")
            return

        if isinstance(elem, HSNeoOCIChar):
            actors = self.game.scenef_get_all_actors()

            actid = ""
            for actid in actors:
                if actors[actid].objctrl == elem.objctrl:
                    # found
                    break

            #self.delActorFromTrack(actid)
            if actid == "":
                self.show_blocking_message_time_sc("Can't find actor to change ID")
                return

            # actually changing ID
            self.changeActorTrackId(actid, toId)

        if isinstance(elem, HSNeoOCIProp):
            props = self.game.scenef_get_all_props()

            propid = ""
            for propid in props:
                if props[propid].objctrl == elem.objctrl:
                    # found
                    break

            # self.delActorFromTrack(actid)
            if propid == "":
                self.show_blocking_message_time_sc("Can't find prop to change ID")
                return

            # actually changing ID
            self.changePropTrackId(propid, toId)

        # updating set
        self.game.scenef_register_actorsprops()

    def changeSelColorTitle(self, toColor, toTitle):
        try:
            if len(toColor) not in (0, 6, 8):
                raise Exception()
            if len(toColor):
                temp = int(toColor, 16)
        except:
            self.show_blocking_message_time_sc("Please, set a valid color code to change to first.\nUse HEX HTML color code like RRGGBB, for example, 'ff0000' for red. Empty color code will clear color/title setting")
            return

        elem = HSNeoOCI.create_from_selected()
        if elem == None or not isinstance(elem, HSNeoOCIChar):
            self.show_blocking_message_time_sc("Nothing or Non-character selected")
            return

        else:
            actors = self.game.scenef_get_all_actors()

            actid = ""
            for actid in actors:
                if actors[actid].objctrl == elem.objctrl:
                    # found
                    break

            #self.delActorFromTrack(actid)
            if actid == "":
                self.show_blocking_message_time_sc("Can't find actor to change color and title, character must be tracked first.")
                return

        # actually changing color and title
        fld = HSNeoOCIFolder.find_single_startswith("-actor:" + actid)
        newTag = "-actor:" + actid
        msg = "Done!\n"
        if len(toColor):
            newTag += ":" + toColor
            if len(toTitle):
                newTag += ":" + toTitle
            else:
                toTitle = elem.text_name
            msg += "Actor <%s> will be rendered as <<color=#%s>%s</color>> in VNSS dialog window title now."%(actid, toColor, toTitle)
        else:
            if actid in self.game.registeredChars:
                del self.game.registeredChars[actid]
            msg += "Actor <%s>'s color/title setting is cleared."%actid
        fld.name = newTag

        # updating set
        self.game.scenef_register_actorsprops()
        self.show_blocking_message_time_sc(msg)


    def delSelectedFromTrack(self):
        elem = HSNeoOCI.create_from_selected()

        if elem == None:
            self.show_blocking_message_time_sc("Nothing selected")
            return

        if isinstance(elem, HSNeoOCIChar):
            actors = self.game.scenef_get_all_actors()

            actid = ""
            for actid in actors:
                if actors[actid].objctrl == elem.objctrl:
                    # found
                    break

            if actid == "":
                self.show_blocking_message_time_sc("Can't delete; seems this actor is not tracking yet")
                return

            self.delActorFromTrack(actid)

        elif isinstance(elem, HSNeoOCIProp):
            props = self.game.scenef_get_all_props()

            propid = ""
            for propid in props:
                if props[propid].objctrl == elem.objctrl:
                    # found
                    break

            self.delPropFromTrack(propid)

        # updating set
        self.game.scenef_register_actorsprops()

    def delActorFromTrack(self,actid):
        if actid != "":
            # we found this char
            fld = HSNeoOCIFolder.find_single("-actor:" + actid)
            if fld == None:
                fld = HSNeoOCIFolder.find_single_startswith("-actor:" + actid + ":")

            # found
            if fld != None:
                fld.delete()

            for i in range(len(self.block)):
                scene = self.block[i]
                del scene.actors[actid]

    def changeActorTrackId(self,actid,toid):
        if actid != "":
            # we found this char
            fld = HSNeoOCIFolder.find_single("-actor:" + actid)
            if fld == None:
                fld = HSNeoOCIFolder.find_single_startswith("-actor:" + actid + ":")

            # found
            #if fld != None:
            #    fld.delete()
            fldoldname = fld.name
            lastelems = fldoldname[len("-actor:" + actid):]
            #print lastelems
            fld.name = "-actor:" + toid + lastelems
            #
            for i in range(len(self.block)):
                scene = self.block[i]
                scene.actors[toid] = scene.actors[actid]
                del scene.actors[actid]

                for camid in range(len(scene.cams)):
                    cam = scene.cams[camid]
                    info = cam[4]
                    if info["whosay"] == actid:
                        info["whosay"] = toid

    def changePropTrackId(self,propid,toid):
        if propid != "":
            # we found this prop
            fld = HSNeoOCIFolder.find_single("-prop:" + propid)
            if fld == None:
                fld = HSNeoOCIFolder.find_single_startswith("-prop:" + propid + ":")

            # found
            #if fld != None:
            #    fld.delete()
            fldoldname = fld.name
            lastelems = fldoldname[len("-prop:" + propid):]
            #print lastelems
            fld.name = "-prop:" + toid + lastelems
            #
            for i in range(len(self.block)):
                scene = self.block[i]
                scene.props[toid] = scene.props[propid]
                del scene.props[propid]

                for camid in range(len(scene.cams)):
                    cam = scene.cams[camid]
                    info = cam[4]
                    if info["whosay"] == propid:
                        info["whosay"] = toid

    def delUnusedCharsProps(self):
        self.game.scenef_register_actorsprops()
        actors = self.game.scenef_get_all_actors()
        props = self.game.scenef_get_all_props()

        cntremoved = 0

        for i in range(len(self.block)):
            scene = self.block[i]

            toremove = []

            for actid in scene.actors:
                if actid == "sys":
                    pass
                elif actid in actors.Keys:
                    pass
                else:
                    toremove.append(actid)

            cntremoved += len(toremove)
            for toremoveid in toremove:
                del scene.actors[toremoveid]

            # props
            toremove = []

            for propid in scene.props:
                if propid in props.Keys:
                    pass
                else:
                    toremove.append(propid)

            cntremoved += len(toremove)
            for toremoveid in toremove:
                del scene.props[toremoveid]

        return "Cleanup complete, %s unrelated data removed!"%(str(cntremoved))

    def delPropFromTrack(self,propid):
        if propid != "":
            # we found this prop
            fld = HSNeoOCIFolder.find_single("-prop:" + propid)

            # found
            if fld != None:
                fld.delete()

            for i in range(len(self.block)):
                scene = self.block[i]
                del scene.props[propid]

    def createFld(self, txt, parent=None, ret=True):
        fld = HSNeoOCIFolder.add(txt)
        if isinstance(parent, HSNeoOCIFolder):
            fld.set_parent(parent)
        if ret == True:
            return fld

    def createFldIfNo(self,txt,parent,childNum):
        if isinstance(parent, HSNeoOCIFolder):
            if len(parent.treeNodeObject.child) <= childNum:
                #print "create folder! %s" % txt
                fld = HSNeoOCIFolder.add(txt)
                fld.set_parent(parent)
                return fld
            else:
                chld = parent.treeNodeObject.child[childNum]
                fld = HSNeoOCI.create_from_treenode(chld)
                if chld.textName != txt:
                    #print "hit! upd folder! %s" % txt
                    fld.name = txt
                    #return fld
                else:
                    #print "hit!! no creation! %s" % txt
                    pass
                return fld

    # Parse/Save/Load
    def findAndLoadSceneData(self, backup=False):
        flds = self.game.scene_get_all_folders_raw()
        for fld in flds:
            if fld.name.startswith("-scenesavestate:") and backup == False:
                ver = fld.name.split(":")[1]
                if ver == "1.0" or ver == "2.5" or ver == "4.0" or ver == "5.0" or ver == "7.0":
                    #return self.parseFlds(fld)  # returns dict
                    block_dict = self.parseFlds(fld)  # returns dict

                    # using compact resolve
                    if ver == "4.0" or ver == "5.0" or ver == "7.0":
                        for key in sorted(block_dict.iterkeys(), key=int):
                            #print 'key, %s' % str(key)
                            #print isinstance(key, int)
                            #print isinstance(key, str)
                            block = block_dict[key]
                            for actorkey in block["actors"]:
                                char_data = block["actors"][actorkey]
                                if '_diff' in char_data:
                                    ind = char_data["_diff"][0]
                                    patch = char_data["_diff"][1]
                                    #print
                                    res = merge_two_dicts(block_dict[str(int(ind)+1)]["actors"][actorkey],patch) # +1 needed for correct calc
                                    block["actors"][actorkey] = res

                            for propkey in block["props"]:
                                char_data = block["props"][propkey]
                                if '_diff' in char_data:
                                    ind = char_data["_diff"][0]
                                    patch = char_data["_diff"][1]
                                    #print
                                    res = merge_two_dicts(block_dict[str(int(ind)+1)]["props"][propkey],patch) # +1 needed for correct calc
                                    block["props"][propkey] = res

                    return block_dict


                else:
                    self.show_blocking_message_time_sc("Error: unknown version "+ver+" of scene data.\nPlease, upgrade SceneSaveState to load it.")
                    return
                # break
            if fld.name == "-scenesavestatebackup" and backup == True:
                return self.parseFlds(fld, backup=True)  # returns dict
                # break

        self.show_blocking_message_time_sc("Error: can't find data to load")
        return

    # parseFlds works for 1.0 or 2.5 version
    def parseFlds(self, fld=None, backup=False):
        if (fld.name.startswith("-scenesavestate:") and backup == False) or (fld.name == "-scenesavestatebackup" and backup == True):
            #print "ok"
            dict = {}
            for scene_fld in fld.treeNodeObject.child:
                scene_fld = HSNeoOCIFolder.create_from_treenode(scene_fld)
                # scene_id = int(scene_fld.name.strip("-scene:"))
                dict_data = self.parseFlds(scene_fld)
                dict[dict_data[0]] = dict_data[1]
            return dict  # returns scene dict
        elif "-scene:" in fld.name:
            sc_dict = {"actors": {}, "props": {}, "cams": {}}  # incomplete
            for sc_elements in fld.treeNodeObject.child:
                sc_elements = HSNeoOCIFolder.create_from_treenode(sc_elements)
                sc_element_data = self.parseFlds(sc_elements)  # tuple (string,state dict) ; eg. ("fchars",fchars)
                sc_dict[sc_element_data[0]] = sc_element_data[1]
            return (fld.name.strip("-scene:"), sc_dict)
        elif fld.name == "-actors":
            char_dict = {}
            for char in fld.treeNodeObject.child:
                char = HSNeoOCIFolder.create_from_treenode(char)
                if char.name.startswith("{"):
                    #char_data = self.parseFlds(char)
                    char_data = json.loads(char.name, object_hook=sceneDecoder)
                    char_dict.update(char_data)
                else:
                    char_fld = HSNeoOCIFolder.create_from_treenode(char.treeNodeObject.child[0])
                    char_data = json.loads(char_fld.name, object_hook=sceneDecoder)
                    char_dict[char.name] = char_data  # tuple (string, dict) ; eg. ("John",dict)
            return (fld.name.strip("-"), char_dict)
        # Props
        elif fld.name == "-props":
            prop_dict = {}
            for prop in fld.treeNodeObject.child:
                prop = HSNeoOCIFolder.create_from_treenode(prop)
                prop_name = prop.name
                if prop_name.startswith("{"):
                    prop_data = json.loads(prop_name, object_hook=sceneDecoder)
                    prop_dict.update(prop_data)
                else:
                    prop_fld = HSNeoOCIFolder.create_from_treenode(prop.treeNodeObject.child[0])
                    prop_data = json.loads(prop_fld.name, object_hook=sceneDecoder)
                    prop_dict[prop_name] = prop_data  # tuple (int, dict)
            return (fld.name.strip("-"), prop_dict)
        # elif "-propitem:" in fld.name:
        #     prop_state = {}
        #     #id = fld.name.strip("-propitem:")
        #     id = fld.name[10:]
        #     state_fld = HSNeoOCIFolder.create_from_treenode(fld.treeNodeObject.child[0])
        #     prop_state = json.loads(state_fld.name, object_hook=sceneDecoder)
        #     return (id, prop_state)
        # cams
        elif fld.name == "-cams":
            cams_dict = {}
            for cam in fld.treeNodeObject.child:
                cam = HSNeoOCIFolder.create_from_treenode(cam)
                cam_data = self.parseFlds(cam)
                cams_dict[cam_data[0]] = cam_data[1]  # tuple (int, dict)
            return (fld.name.strip("-"), cams_dict)
        elif "-cam:" in fld.name:
            cam_state = {}
            id = int(fld.name.strip("-cam:"))
            state_fld = HSNeoOCIFolder.create_from_treenode(fld.treeNodeObject.child[0])
            cam_state = json.loads(state_fld.name, object_hook=sceneDecoder)
            return (id, cam_state)

    def restrict_to_child(self, fld, numchilds):
        fld = fld
        """:type fld:HSNeoOCIFolder"""
        if len(fld.treeNodeObject.child) > numchilds:
            ar = fld.treeNodeObject.child
            ar2 = []
            for treeobj in ar:
                ar2.append(HSNeoOCI.create_from_treenode(treeobj))

            for i in range(len(ar2)):
                if i >= numchilds:
                    print "deleted! %s" % str(i)
                    ar2[i].delete()


    def saveSceneData(self, fld=None, backup=False):
        # self.saveSceneDataOld(fld,backup)
        # return

        # delete existing scenedata fld
        if backup:
            data_fld = HSNeoOCIFolder.find_single("-scenesavestatebackup")
            # correct... but be super-confident

            # if data_fld:
            #     pass
            # else:
            #     data_fld = self.createFld("-scenesavestatebackup")
            if data_fld:
                data_fld.delete()

            data_fld = self.createFld("-scenesavestatebackup")
        else:
            data_fld = HSNeoOCIFolder.find_single_startswith("-scenesavestate:")
            txt = "-scenesavestate:"+self.versionSceneDataParsing
            if data_fld:
                data_fld.name = txt
            else:
                data_fld = self.createFld(txt)



        # save data as flds
        # template = {"fchars":{}, "mchars":{}, "propflds":{}, "cams":[], "accs":{}, "props":{}}
        sdict = []
        for scene in self.block:
            sdict.append(
                {"actors": scene.actors, "cams": scene.cams, "props": scene.props})

        # Create folders as scenedata
        if self.isSaveOld:

            # txt = data_fld.name
            # data_fld.delete()
            # data_fld = HSNeoOCIFolder.add(txt)
            data_fld.delete_all_children() # just delete all
        else:
            self.restrict_to_child(data_fld, len(sdict)) # start reusing old folders...
        #self.restrict_to_child(data_fld, 0)


        # Create scene data
        #print len(sdict)
        scene_id = 1
        for scene in sdict:
            # Making parent folders
            scene_fld = self.createFldIfNo(("-scene:" + str(scene_id)), data_fld, scene_id-1)
            #scene_fld.delete_all_children()
            actor_fld = self.createFldIfNo("-actors", scene_fld, 0)
            props_fld = self.createFldIfNo("-props", scene_fld, 1)
            cams_fld = self.createFldIfNo("-cams", scene_fld, 2)

            # Making children folders
            self.restrict_to_child(actor_fld, len(scene["actors"]))
            k = 0
            for ch_name, ch_content in scene["actors"].items():
                #ch_name_fld = self.createFld(ch_name, actor_fld)

                bestInd = -1
                bestRes = 100000
                bestResDiff = {}

                if self.isSaveCompact and not backup: # optimization - calc diff, only for normal saves
                    if scene_id > 1:
                        for j in range(scene_id-1):
                            if ch_name in sdict[j]["actors"]:
                                diff = get_status_diff_optimized(sdict[j]["actors"][ch_name], ch_content)
                                if len(diff) < bestRes:
                                    bestInd = j
                                    bestRes = len(diff)
                                    bestResDiff = diff
                                if len(diff) == 0: # ideal - immediately break
                                    break

                if bestInd == -1:
                    # no optimization
                    #print "non-opt"
                    #self.createFld(json.dumps(ch_content, cls=SceneEncoder), ch_name_fld)
                    self.createFldIfNo(json.dumps({ch_name:ch_content}, cls=SceneEncoder), actor_fld, k)
                else:
                    #self.createFld(json.dumps({'_diff':[bestInd, bestResDiff]}, cls=SceneEncoder), ch_name_fld)
                    self.createFldIfNo(json.dumps({ch_name: {'_diff':[bestInd, bestResDiff]}}, cls=SceneEncoder), actor_fld, k)
                k += 1

            self.restrict_to_child(cams_fld, len(scene["cams"]))
            for i in range(0, len(scene["cams"])):
                cam_id_fld = self.createFldIfNo("-cam:" + str(i), cams_fld, i)
                self.createFldIfNo(json.dumps(scene["cams"][i], cls=SceneEncoder), cam_id_fld, 0)

            self.restrict_to_child(props_fld, len(scene["props"]))
            k = 0
            for prop_id, prop_state in scene["props"].items():
                #print "prop"
                #prop_id_fld = self.createFld(prop_id, props_fld)

                bestInd = -1
                bestRes = 100000
                bestResDiff = {}

                if self.isSaveCompact and not backup:  # optimization - calc diff, only for normal saves
                    if scene_id > 1:
                        for j in range(scene_id - 1):
                            if prop_id in sdict[j]["props"]:
                                diff = get_status_diff_optimized(sdict[j]["props"][prop_id], prop_state)
                                if len(diff) < bestRes:
                                    bestInd = j
                                    bestRes = len(diff)
                                    bestResDiff = diff
                                if len(diff) == 0:  # ideal - immediately break
                                    break

                if bestInd == -1:
                    # no optimization
                    # print "non-opt"
                    #self.createFld(json.dumps(prop_state, cls=SceneEncoder), prop_id_fld)
                    self.createFldIfNo(json.dumps({prop_id: prop_state}, cls=SceneEncoder), props_fld, k)
                else:
                    #self.createFld(json.dumps({'_diff': [bestInd, bestResDiff]}, cls=SceneEncoder), prop_id_fld)
                    self.createFldIfNo(json.dumps({prop_id: {'_diff': [bestInd, bestResDiff]}}, cls=SceneEncoder), props_fld, k)
                k += 1


            scene_id = scene_id + 1

        data_fld.visible_treenode = False
        self.game.set_timer(0.1,self.onDataSaved)

    def verify_load(self):
        try:
            blockold = self.block
            try:
                self.loadSceneData(setToFirst=False)
                blocknew = self.block
                self.block = blockold
            except Exception, e:
                self.block = blockold
                print "Error verify loading data - %s" % (str(e))
                return -100000

            diffs = 0
            if len(blocknew) == len(blockold):
                for i in range(len(blocknew)):
                    # diff = get_status_diff_optimized(blocknew[i],blockold[i])
                    # if len(diff) > 0:
                    #     diffs += 1
                    if not blocknew[i].isEqual(blockold[i]):
                        print "Verify: Non-eq scene: %s" % str(i+1)
                        diffs += 1
            else:
                diffs = len(blocknew) - len(blockold)
                print "Diff scene length: %s" % str(diffs)

            if diffs == 0:
                # self.show_blocking_message_time_sc("Data saved! (Verify error: %s differences!)" % (str(len(diff))))
                #self.show_blocking_message_time_sc("Data saved! (Verify: OK)")
                return 0
            else:
                # self.show_blocking_message_time_sc(
                #     "Data saved! (Verify: %s potential problems, see Console!)" % (str(diffs)))
                return diffs

        except Exception, e:
            #self.show_blocking_message_time_sc("Data saved! (Verify: INTERNAL ERROR!)")
            print "Error verify %s" % (str(e))
            return -100000


    def onDataSaved(self,game):
        #dt = Time.deltaTime
        #self.show_blocking_message_time_sc("Data saved in %.1f s!" % (dt))
        if not self.isSaveVerify:
            self.show_blocking_message_time_sc("Data saved!")
        else:
            #diff = get_status_diff_optimized(blockold,blocknew)
            diffs = self.verify_load()
            if diffs == 0:
                self.show_blocking_message_time_sc("Data saved! (Verify: OK)")
            elif diffs == -100000:
                self.show_blocking_message_time_sc("Data saved! (Verify: INTERNAL ERROR!)")
            else:
                if self.isSaveOld:
                    self.show_blocking_message_time_sc(
                        "Data saved! (Verify: OK)\n(some %s potential misequals, seems be ok)" % (str(diffs)))
                else:
                    self.show_blocking_message_time_sc(
                         "Data saved! (Verify: %s potential problems, see Console!)" % (str(diffs)))

    def saveToFile(self, backup=False):
        # Template
        # template = {"fchars":{}, "mchars":{}, "propflds":{}, "cams":[], "accs":{}, "props":{}}

        if self.svname == "":
            fld = getFolder(self.game, "-scfile:", False)
            if not fld == None:
                self.svname = fld.text_name.strip("-scfile:")
        else:
            fld = getFolder(self.game, "-scfile:" + self.svname, True)
            if fld == None:
                # create pointer fld
                self.createFld("-scfile:" + self.svname, parent=None, ret=False)
        if not self.svname == "":
            if backup == False:
                filename = str(self.svname)
            else:
                filename = str(self.svname) + "_backup"

            self.saveToFileDirect(filename)

    def saveToStr(self):
        save_data = {}
        #save_data["version"] = self.versionSaveInSceneData # already included in PNG
        #save_data["blocks"] = {}
        for i in range(0, len(self.block)):
            actors = _sc.block[i].actors
            cams = _sc.block[i].cams
            props = _sc.block[i].props



            save_data[i] = {"actors": actors, "cams": cams, "props": props}

            if _sc.block[i].thumbTex != None:
                from vngameengine import Texture2D2BytesPNG
                from vnactor import bytearray_to_str64
                ba = Texture2D2BytesPNG(_sc.block[i].thumbTex)
                save_data[i]["thumb64"] = bytearray_to_str64(ba)

        # include advanced setting data
        #save_data["advanced"] = self.saveAdvancedToDict()

        return json.dumps(save_data, cls=SceneEncoder)

    def saveAdvancedToStr(self):
        return json.dumps(self.saveAdvancedToDict(), cls=SceneEncoder)

    def saveAdvancedToDict(self):
        adv_data = {}
        adv_data["skipClothesChanges"] = self.skipClothesChanges
        adv_data["vnExportFakeLipSync"] = self.vnExportFakeLipSync
        adv_data["vnExportFakeLipSyncVer"] = self.vnExportFakeLipSyncVer
        adv_data["vnExportFakeLipSyncSpd"] = self.vnExportFakeLipSyncSpd
        return adv_data

    def loadAdvancedFromDict(self, adv_data):
        # load if exist
        if "skipClothesChanges" in adv_data:
            self.skipClothesChanges = adv_data["skipClothesChanges"]
        if "vnExportFakeLipSync" in adv_data:
            self.vnExportFakeLipSync = adv_data["vnExportFakeLipSync"]
        if "vnExportFakeLipSyncVer" in adv_data:
            self.vnExportFakeLipSyncVer = adv_data["vnExportFakeLipSyncVer"]
        if "vnExportFakeLipSyncSpd" in adv_data:
            self.vnExportFakeLipSyncSpd = adv_data["vnExportFakeLipSyncSpd"]

    def saveToFileDirect(self,filename):


        # save file
        script_dir = os.path.dirname(__file__)
        folder_path = "sssdata/"
        #if backup == False:
        file_path = folder_path + str(filename) + ".txt"
        #else:
        #file_path = folder_path + str(self.svname) + "_backup.txt"
        abs_file_path = os.path.join(script_dir, file_path)

        f = open(abs_file_path, "w")
        f.write(self.saveToStr())  # , indent = 4, separators = (","," : ")))
        f.close()

    def loadFromFileDirect(self,filename):
        script_dir = os.path.dirname(__file__)
        folder_path = "sssdata/"

        file_path = folder_path + str(filename) + ".txt"
        abs_file_path = os.path.join(script_dir, file_path)

        if os.path.isfile(abs_file_path):
            f = open(abs_file_path, "r")
            block_dict = self.loadFromStr(f.read()) #json.loads(f.read(), object_hook=sceneDecoder)  # , indent = 4, separators = (","," : ")))
            f.close()

            return block_dict

        return None

    def loadFromStr(self,str):
        return json.loads(str, object_hook=sceneDecoder)  # , indent = 4, separators = (","," : ")))

    def loadSceneDataInternalDict(self,data_dict,file,version=None):
        if not data_dict == None:

            # init zero
            self.dict = []
            self.dictparse = {}
            self.scenefile = ""
            self.block = []
            self.baseacc = {}  # base acc set
            self.accstate = {}
            #self.nameset = [[],
            #                []]  # Array[Array[String]](((),())) #,Array[String](())] # nameset[0] = female names, nameset[1] = male names
            #self.scene_strings = []

            # check version
            # if "version" in data_dict:
            #     # new data struct from save version 20.0
            #     ver = float(data_dict["version"])
            #     if ver < 20.0:
            #         print "Unexpected sss save data version!?"
            #         return
            #     # contains advanced setting data, and block info
            #     self.loadAdvancedFromDict(data_dict["advanced"])
            #     block_dict = data_dict["blocks"]
            # else:
            #     # old data struct, all data is block info
            #     block_dict = data_dict

            if version == "19.0" or version == "29.9" or version == None:
                block_dict = data_dict
            elif version == "30.0": # was only internal, never public released
                self.loadAdvancedFromDict(data_dict["advanced"])
                block_dict = data_dict["blocks"]
            else:
                self.game.logger_log_warning("Unexpected SSS save data version!? %s"%version, True)
                self.game.logger_log_message("Please, upgrade to new VNGE!!")
                return

            # attaining data
            """
            block_dict = {}
            for fld in flds:
                if fld.objctrl.name == "-scenedata":
                    block_dict = self.parseFlds(fld)
                    break
            """

            for key in sorted(block_dict.iterkeys(), key=int):
                actors = block_dict[key]["actors"]
                props = block_dict[key]["props"]
                cams = []
                if file == True:
                    cams = block_dict[key]["cams"]
                    # cams.append(block_dict[key]["cams"][id])
                else:
                    for id in sorted(block_dict[key]["cams"]):
                        #print key, id

                        cams.append(block_dict[key]["cams"][id])
                #print actors
                #print props
                #print cams
                if "thumb64" in block_dict[key].keys():
                    self.block.append(Scene(actors,props,cams,str64_to_bytearray(block_dict[key]["thumb64"])))
                else:
                    self.block.append(Scene(actors,props,cams))

                #self.scene_strings.append("Scene " + str(key))


                # id = int(key)
                # for id in range(0,len(block_dict)):
                # fchars = block_dict[key]["fchars"]
                # mchars = block_dict[key]["mchars"]
                # propflds = block_dict[key]["propflds"]
                # accs = block_dict[key]["accs"]
                # props = block_dict[key]["props"]
                # cams = []
                # if file == True:
                #     cams = block_dict[key]["cams"]
                #     # cams.append(block_dict[key]["cams"][id])
                # else:
                #     for id in sorted(block_dict[key]["cams"]):
                #         cams.append(block_dict[key]["cams"][id])
                # self.block.append(Scene(fchars, mchars, propflds, accs, cams, props))
                # self.scene_strings.append("Scene " + str(key))

                # self.updateAllSceneChars(tag, newch)
            # self.updateNameset()
            # self.updateTagChars()
            # self.updateTagItems()
            # self.updateTagPropFlds()
            # self.updateTagProps()
            #self.show_blocking_message_time_sc("Scene data loaded!")

    def loadSceneDataBackupTimer(self):
        block_dict = self.loadFromFileDirect("_backuptimer")
        self.loadSceneDataInternalDict(block_dict, True)

    def loadSceneData(self, file=False, backup=False, setToFirst = True):
        self.game.scenef_register_actorsprops()

        block_dict = None
        if file == False:
            # get scenedata
            block_dict = self.findAndLoadSceneData(backup=backup) #self.parseFlds(fld=None, backup=backup)
        else:
            if self.svname == "":
                fld = getFolder(self.game, "-scfile:", False)
                if not fld == None:
                    self.svname = fld.text_name.strip("-scfile:")
            if backup == False:
                filename = str(self.svname)
            else:
                filename = str(self.svname) + "_backup"
            # abs_file_path = os.path.join(script_dir, file_path)
            # if os.path.isfile(abs_file_path):
            #     f = open(abs_file_path, "r")
            #     block_dict = json.loads(f.read(), object_hook=sceneDecoder)  # , indent = 4, separators = (","," : ")))
            #     f.close()
            block_dict = self.loadFromFileDirect(filename)

        self.loadSceneDataInternalDict(block_dict,file)

        # loading
        if setToFirst:
            if len(self.block) > 0:
                self.cur_index = 0
                self.cur_cam = 0

    # Change name
    def changeCharName(self, name):
        char = getSelectedChar(self.game)
        old_name = char.text_name
        char.objctrl.treeNodeObject.textName = name

        # for sex in range(len(self.basechars)):
        #     if old_name in self.nameset[sex]:
        #         self.changeSceneChars((1 - sex), tag="upd")
        #         break


    # Duplicate scene
    def dupScene(self):
        if len(self.block) > 0:
            #import copy

            # we have a problem with copy, so... just serialize and back it
            #objstr = json_encode(self.block[self.cur_index])
            self.block.insert(self.cur_index, self.block[self.cur_index].copy())
            #self.updateSceneStrings()

    # Copy/paste cam set
    def copyCamSet(self):
        if self.cur_index > -1:
            if not self.camset == []:
                self.camset = []
            self.camset = copy.copy(self.block[self.cur_index].cams)

    def pasteCamSet(self):
        if self.cur_index > -1:
            self.block[self.cur_index].cams.extend(self.camset)

    # Move cam (up/down)
    def move_cam_up(self):
        if self.cur_index > -1 and self.cur_cam > 0:
            curcam = self.block[self.cur_index].cams[self.cur_cam]
            self.block[self.cur_index].cams[self.cur_cam] = self.block[self.cur_index].cams[self.cur_cam - 1]
            self.cur_cam -= 1
            self.block[self.cur_index].cams[self.cur_cam] = curcam

    def move_cam_down(self):
        if self.cur_index > -1 and self.cur_cam < (len(self.block[self.cur_index].cams) - 1):
            curcam = self.block[self.cur_index].cams[self.cur_cam]
            self.block[self.cur_index].cams[self.cur_cam] = self.block[self.cur_index].cams[self.cur_cam + 1]
            self.cur_cam += 1
            self.block[self.cur_index].cams[self.cur_cam] = curcam

    # Move scene(up/down)
    def move_scene_up(self):
        if self.cur_index > 0:
            cursc = self.block[self.cur_index]
            self.block[self.cur_index] = self.block[self.cur_index - 1]
            self.cur_index -= 1
            self.block[self.cur_index] = cursc

    def move_scene_down(self):
        if self.cur_index < (len(self.block) - 1):
            cursc = self.block[self.cur_index]
            self.block[self.cur_index] = self.block[self.cur_index + 1]
            self.cur_index += 1
            self.block[self.cur_index] = cursc

    # Goto next/prev
    def goto_first(self):
        self.cur_index = 0
        self.loadCurrentScene()
        self.prev_index = self.cur_index

    def goto_next(self):
        if len(self.block) > 0:
            if len(self.block[self.cur_index].cams) > 0 and self.cur_cam < (len(self.block[self.cur_index].cams) - 1):
                self.cur_cam += 1
                self.setCamera()
            # elif self.cur_index < (len(self.block) - 1):
            # self.cur_index += 1
            else:
                self.goto_next_sc()

    def goto_prev(self):
        if len(self.block) > 0:
            self.prev_index = self.cur_index
            self.prev_cam = self.cur_cam
            if self.cur_cam > 0:
                self.cur_cam -= 1
                self.setCamera()
            # elif self.cur_index > 0:
            # self.cur_index -= 1
            else:
                self.goto_prev_sc(lastcam=True)

    def goto_next_sc(self):
        if len(self.block) > 0 and self.cur_index < (len(self.block) - 1):
            self.cur_index += 1
            self.loadCurrentScene()
            self.prev_index = self.cur_index

    def goto_prev_sc(self, lastcam=False):
        if len(self.block) > 0 and self.cur_index > 0:
            self.cur_index -= 1
            self.loadCurrentScene()
            self.prev_index = self.cur_index
            if lastcam == True and len(self.block[self.cur_index].cams) > 0:
                self.cur_cam = len(self.block[self.cur_index].cams) - 1
                self.setCamera()

    # export cam texts
    def exportCamTexts(self):
        import codecs
        filename = "sss_camtexts.txt"
        try:
            f = codecs.open(filename, 'w+', encoding="utf-8")
            f.write("[\n")
            for i in range(len(self.block)):
                scene = self.block[i]
                """:type scene:Scene"""

                # only process scene if 1 cam is VN cam - other, skip
                #cam = scene.cams[0]
                for j in range(len(scene.cams)):
                    cam = scene.cams[j]
                    addparams = cam[4]
                    #if addparams["addparam"]:  # only process if 1 cam is VN cam
                    #fullobj = {'z_sc': i+1, 'z_cam': j, 'who': addparams["whosay"], "say": addparams["whatsay"] }
                    fullobj = [ i + 1, j, addparams["addparam"], addparams["whosay"], addparams["whatsay"]]
                    res = json.dumps(fullobj, cls=SceneEncoder)
                    f.write("%s,\n" % res)

            f.write("{}\n")
            f.write("]\n")


            f.close()

        except Exception, e:
            self.show_blocking_message_time_sc("Can't write to file %s in game root folder\nerr: %s" % (filename,str(e)))
            return

        self.show_blocking_message_time_sc("Cam VN texts exported to sss_camtexts.txt!\nFormat: scene, cam, isVNcam, whosay, whatsay")

    # export cam texts
    def importCamTexts(self):
        import codecs
        filename = "sss_camtexts.txt"



        try:
            filecont = self.game.file_get_content_utf8(filename)
            arr = json.loads(filecont, object_hook=sceneDecoder)

            for elem in arr:
                if len(elem) > 0:
                    scene = self.block[elem[0]-1]
                    cam = scene.cams[elem[1]]
                    cam[4]["addparam"] = elem[2]
                    cam[4]["whosay"] = elem[3]
                    cam[4]["whatsay"] = elem[4]
                    #cam[4] = elem["param"]
                    #camar = list(cam)
                    #camar[4] = elem["param"]
                    #scene.cams[elem["cam"]] = tuple(camar)

        except Exception, e:
            self.show_blocking_message_time_sc(
                "Can't import file %s in game root folder\nerr: %s" % (filename, str(e)))
            return

        self.show_blocking_message_time_sc("Cam VN texts import success!")

    def camSetAll(self,state):
        for i in range(len(self.block)):
            scene = self.block[i]
            """:type scene:Scene"""

            # only process scene if 1 cam is VN cam - other, skip
            # cam = scene.cams[0]
            for j in range(len(scene.cams)):
                cam = scene.cams[j]
                #addparams = cam[4]
                cam[4]["addparam"] = state

        self.show_blocking_message_time_sc("Cams changed!")

    # export to VNSceneScript
    def exportToVNSS(self):
        params = {
            'toPNG': self.vnExportToPNG, 
            'useFakeLipSync': self.vnExportFakeLipSync,
            'fakeLipSyncVer': self.vnExportFakeLipSyncVer,
            'fakeLipSyncSpd': self.vnExportFakeLipSyncSpd,
            'skipClothesChanges': self.skipClothesChanges,
        }
        scenesavestate_vnssext.exportToVNSS(self,params)
        if self.vnFastIsRunImmediately:
            self.runVNSS("cam")


    def runVNSS(self, starfrom = "begin"):
        self.game.gdata.wasvisible = self.game.visible
        self.game.visible = True

        self.game.gdata.vnbupskin = self.game.skin
        #self.game.skin_set_byname("skin_renpy")
        #from skin_renpy import SkinRenPy
        from skin_renpyminiadv import SkinRenPyMiniAdv
        rpySkin = SkinRenPyMiniAdv()
        rpySkin.isEndButton = True
        rpySkin.endButtonTxt = "End script"
        rpySkin.endButtonCall = self.endVNSSbtn
        self.game.skin_set(rpySkin)

        if starfrom == "cam":
            #print self.cur_index, self.cur_cam
            calcPos = (self.cur_index+1)*100 + self.cur_cam
        elif starfrom == "scene":
            calcPos = (self.cur_index+1)*100
        else:
            calcPos = 0
        print "Run VNSS from state %s" % str(calcPos)
        self.game.vnscenescript_run_current(self.onEndVNSS, calcPos)

    def endVNSSbtn(self, game = None):
        import vnscenescript
        vnscenescript.run_state(self.game,self.game.scenedata.scMaxState + 1,True) # move to end state

    def onEndVNSS(self, game = None):

        self.game.skin_set(self.game.gdata.vnbupskin)
        self.game.visible = self.game.gdata.wasvisible

    #def _exportAddBlock(self,fld_acode,):
    def get_next_speaker(self, curSpeakAlias, next):
        # next from unknown speaker
        all_actors = self.game.scenef_get_all_actors()
        if curSpeakAlias != 's' and (not curSpeakAlias in all_actors):
            return 's'

        # next from s or actor
        if curSpeakAlias == 's':
            if len(all_actors) > 0:
                if next:
                    return all_actors.Keys[0]
                else:
                    return all_actors.Keys[-1]
            else:
                return 's'
        else:
            nextIndex = all_actors.Keys.IndexOf(curSpeakAlias)
            if next:
                nextIndex += 1
            else:
                nextIndex -= 1
            if nextIndex in range(len(all_actors)):
                return all_actors.Keys[nextIndex]
            else:
                return 's'


class Scene():
    def __init__(self, actors=None, props=None, cams=None, thumbPngBA=None):
        self.cams = []
        self.actors = {}
        self.props = {}
        self.thumbTex = None

        if not actors == None:
            self.actors = actors
        if not cams == None:
            self.cams = cams
        if not props == None:
            self.props = props
        if not thumbPngBA == None:
            self.thumbTex = BytesPNG2Texture2D(thumbPngBA)

    def copy(self):
        stractors = json_encode(self.actors)
        strprops = json_encode(self.props)
        strcams = json_encode(self.cams)
        if self.thumbTex != None:
            pngba = Texture2D2BytesPNG(self.thumbTex)
        return Scene(json_decode(stractors),json_decode(strprops),json_decode(strcams),pngba)

    def isEqual(self,other):
        # if len(self.cams) != len(other.cams):
        #     return False
        # for i in range(len(self.cams)):
        #     diff =
        if not is_arr_equal(self.cams, other.cams):
            return False
        if not is_status_statuses_equal(self.actors,other.actors):
            return False
        if not is_status_statuses_equal(self.props, other.props):
            return False

        return True


    # ---- new ----
    def importCurScene(self,game,options = {}):
        """:type game: vngameengine.VNNeoController"""
        game.scenef_register_actorsprops()

        self.actors = {}
        self.props = {}

        actors = game.scenef_get_all_actors()
        props = game.scenef_get_all_props()

        for actid in actors:
            self.actors[actid] = actors[actid].export_full_status()

        for propid in props:
            self.props[propid] = props[propid].as_prop.export_full_status()

        if "sys" in options:
            self.actors["sys"] = export_sys_status(game)

        try:
            self.thumbTex = BytesPNG2Texture2D(game.makePngScreenshot(160,90))
        except Exception, e:
            game.logger_log_warning("Can't make PNG preview for Scene: "+str(e))
            pass
    # Set scene chars with state data from dictionary

    def setSceneState(self, game):
        """:type game: vngameengine.VNNeoController"""
        for actid in self.actors:
            if actid == "sys":
                #vnframe.act(game, {'sys': self.actors[actid]})
                import_sys_status_diff_optimized(game, self.actors[actid])
        for actid in self.actors:
            #vnframe.act(game, {actid: self.actors[actid]})
            #game.scenef_get_actor(actid).import_status(self.actors[actid])
            #diffstatus = game.scenef_get_actor(actid).export_diff_status(self.actors[actid])
            #game.scenef_get_actor(actid).import_status(diffstatus)
            #game.scenef_get_actor(actid).import_status_diff_optimized(self.actors[actid])

            if actid == "sys":
                continue

            #char_import_status_diff_optimized(game.scenef_get_actor(actid),self.actors[actid])
            char_status = self.actors[actid]
            try:
                global _sc
                if _sc:
                    if hasattr(_sc, "skipClothesChanges"):
                        if _sc.skipClothesChanges:
                            char_status = dict(char_status) # make a copy
                            del char_status["acc_all"]
                            del char_status["cloth_all"]
                            del char_status["cloth_type"]
            except Exception, e:
                pass

            try:
                char_import_status_diff_optimized(game.scenef_get_actor(actid), char_status)
            except Exception, e:
                game.logger_log_message("Error: can't set scene char id=%s"%actid)
                game.logger_log_message("If you removed it, try Tracking>Advanced functions>Cleanup unused char/props")

        for propid in self.props:
            #vnframe.act(game, {propid: self.props[propid]})
            #print propid
            #print game.scenef_get_all_props()

            #game.scenef_get_propf(propid).import_status(self.props[propid])
            # optimized version
            try:
                char_import_status_diff_optimized(game.scenef_get_propf(propid), self.props[propid])
            except Exception, e:
                game.logger_log_message("Error: can't set scene prop id=%s"%propid)
                game.logger_log_message("If you removed it, try Tracking>Advanced functions>Cleanup unused char/props")


    # Camera Manip
    def addCam(self, cam_data):
        global _sc
        if _sc.AddCamInsertsRightAfter:
            self.cams.insert(_sc.cur_cam + 1, cam_data)
            return _sc.cur_cam + 1

        self.cams.append(cam_data)
        return (len(self.cams) - 1)


    def updateCam(self, index, cam_data):
        self.cams[index] = cam_data

    def deleteCam(self, index):
        if len(self.cams) > 0:
            self.cams.pop(index)
            if index == 0 and len(self.cams) > 0:
                return index
            return (index - 1)


# ::::: Console init and window :::::


def toggle_scene_console(game):
    global _sc
    if _sc == None:
        _sc = SceneConsole(game)

    if _sc.guiOnShow:
        sceneConsoleGUIClose()
    else:
        sceneConsoleGUIStart(game)


def resetConsole(game):
    global _sc
    sceneConsoleGUIClose()

    # _sc = None
    # _sc = SceneConsole()
    sceneConsoleGUIStart(game)



def sceneConsoleGUIStart(game):
    global _sc

    #_sc.game_skin_saved = game.skin
    if hasattr(game.gdata, 'sss_game_skin_saved'):
        if game.gdata.sss_game_skin_saved:
            pass
        else:
            game.gdata.sss_game_skin_saved = game.skin
    else:
        game.gdata.sss_game_skin_saved = game.skin



    #game.skin_set(_sc.skin)
    global newWndId
    newWndId = game.new_extra_window_skin(_sc.skin)

    # _sc.originalWindowCallback = game.windowCallback
    # _sc.originalwindowwidth = game.wwidth
    # _sc.originalwindowheight = game.wheight

    _sc.guiOnShow = True



    #_sc.skin = skin

    # setWindowName(_sc.windowindex)
    # game.wwidth = _sc.windowwidth
    # game.wheight = _sc.windowheight
    #
    # game.windowRect = Rect(Screen.width / 2 - game.wwidth * 1.5, Screen.height - game.wheight - 500,
    #                        game.wwidth + 50, game.wheight + 400)
    loadConfig()
    game.event_unreg_listener("update", hook_update, "sssupdate")
    game.event_reg_listener("update", hook_update, "sssupdate")

    game.event_unreg_listener("scene_loaded_after", hook_loaded, "sssupdatel")
    game.event_reg_listener("scene_loaded_after", hook_loaded, "sssupdatel")
    # game.windowCallback = GUI.WindowFunction(sceneConsoleWindowFunc)

def sceneConsoleSkinSetup(game):
    global _sc

    setWindowName(_sc.windowindex)
    from UnityEngine import GUI, Screen, Rect
    game.wwidth = _sc.windowwidth
    game.wheight = _sc.windowheight
    # #game.windowRect = Rect (Screen.width / 2 - game.wwidth / 2, Screen.height - game.wheight - 10, game.wwidth, game.wheight)

    x = get_ini_value_def_int("WindowX", Screen.width / 2 - game.wwidth * 1.5)
    y = get_ini_value_def_int("WindowY", Screen.height - game.wheight - 500)
    w = get_ini_value_def_int("WindowWidth", game.wwidth + 50)
    h = get_ini_value_def_int("WindowHeight", game.wheight + 400)

    # game.windowRect = Rect(Screen.width / 2 - game.wwidth * 1.5, Screen.height - game.wheight - 500,
    #                        game.wwidth + 50, game.wheight + 400)

    game.windowRect = Rect(x,y,w,h)

    #game.windowCallback = GUI.WindowFunction(scriptHelperWindowGUI)
    game.windowStyle = game.windowStyleDefault

def sceneConsoleSkinWindowGUI(game,windowid):
    sceneConsoleWindowFunc(windowid)

def sceneConsoleSkinWindowGUIMin(game,windowid):
    minimizeWindowFunc(windowid)

def loadConfig():
    global _sc
    import ConfigParser

    # Shortcuts
    _sc.shortcuts_process = {
        "Load Next": [_sc.goto_next, None],
        "Load Prev": [_sc.goto_prev, None],
        "Load Next Scene": [_sc.goto_next_sc, None],
        "Load Prev Scene": [_sc.goto_prev_sc, None],
        "Load First Scene": [_sc.goto_first, None],
        "Add Scene (auto)": [_sc.addAuto, None],
        "Expand/collapse window": [minimizeWindow, None],
        "Save Scenedata": [_sc.saveSceneData, None],
        "Add Camera": [_sc.addCamWithMessage, None],
        #"Load Temp States": [loadTempStates, None],
        #"Load Temp Poses": [loadTempPoses, None]
    }
    _sc.shortcuts = {}

    config = ConfigParser.SafeConfigParser()
    config.read(os.path.splitext(__file__)[0] + '.ini')

    for command, key in config.items('Shortcuts'):
        """
        if command.lower() == "loadnext":
            comstr = "Load Next"
        elif command.lower() == "loadprev":
            comstr = "Load Prev"
        elif command.lower() == "loadnextscene":
            comstr = "Load Next Scene"
        elif command.lower() == "loadprevscene":
            comstr = "Load Prev Scene"
        elif command.lower() == "loadfirstscene":
            comstr = "Load First Scene"
        elif command.lower() == "addsceneauto":
            comstr = "Add Scene (Auto)"
        """
        for com in _sc.shortcuts_process.keys():
            if command == com.lower():
                _sc.shortcuts_process[com][1] = parseKeyCode(key)
                _sc.shortcuts[com] = key
                break


def saveConfig():
    global _sc

    cfpath = os.path.splitext(__file__)[0] + '.ini'
    content = "[Shortcuts]\n"
    for command, key in _sc.shortcuts.items():
        content += command + " = " + key + "\n"

    cfile = open(cfpath, "w")
    cfile.write(content)
    cfile.close()

    # reinit config
    _sc.game.event_unreg_listener("update", hook_update, "sssupdate")
    loadConfig()
    _sc.game.event_reg_listener("update", hook_update, "sssupdate")


def hook_loaded(game, evid, u_param):


    isProcess = get_ini_value_def_int("AutoLoadSSSOnSceneLoad", 1)
    if isProcess == 1:
        global _sc
        if len(_sc.block) == 0: # only if no data
            if HSNeoOCIFolder.find_single_startswith("-scenesavestate:") != None:
                _sc.loadSceneData()
                _sc.show_blocking_message_time_sc("Scene data was auto-loaded during scene load!")
            else:
                _sc.clear_scenes()




def hook_update(game, evid, u_param):
    try:
        global _sc
        if not _sc.hook_update_allowed:
            return

        import unity_util
        from UnityEngine import Input, KeyCode




        global _sc
        global _step

        dt = Time.deltaTime

        if _sc.skin.controller.visible: # count only time when SSS is visible
            _sc.backupTimeCur -= dt
            #print _sc.backupTimeCur
            if _sc.backupTimeCur <= 0:
                _sc.backupTimeCur = _sc.backupTimeDuration
                if len(_sc.block) > 0:
                    #print len(_sc.block)
                    print "VNGE SSS: try backup by timer (every %s seconds)... (%s scenes)" % (str(_sc.backupTimeDuration), str(len(_sc.block)))
                    try:
                        _sc.saveToFileDirect("_backuptimer")
                        print "VNGE SSS: made backup by timer!"
                    except:
                        print "VNGE SSS: timer backup FAILED!... "


        # param = _sc.game.gdata.sc_shortcuts["loadnext"]
        try:
            for commands, param in _sc.shortcuts_process.items():

                (_, icode, ictrl, ialt, ishift) = param[1]

                if Input.GetKeyDown(icode):
                    # unity sucks for checking meta keys
                    ctrl, alt, shift = unity_util.metakey_state()
                    # print "detected key down:"
                    # print "tgt:", game.gdata.startShortcut
                    # print "cur: ctrl=%s, alt=%s, shift=%s"%(str(ctrl), str(alt), str(shift))
                    if ctrl == ictrl and alt == ialt and shift == ishift:

                        # need to stop processing for about 0.5 seconds - avoid duplicate key proc
                        _sc.hook_update_allowed = False
                        game.set_timer(0.3, hook_upd_restore)

                        param[0]()  # _sc.goto_next()
                        break
        except Exception, e:
            print("Error in SSS hook_update shortcuts processing: ")
            print(param)
            import traceback
            traceback.print_exc()

    except Exception, e:
        print("Error in SSS hook_update")
        import traceback
        traceback.print_exc()

def hook_upd_restore(game):
    _sc.hook_update_allowed = True

def sceneConsoleGUIClose():
    global _sc

    # applying backup

    if not _sc.svname == "":
        _sc.saveToFile(backup=True)
    else:
        #if _sc.verify_load() != 0:
        #_sc.saveSceneData(backup=True)
        _sc.svname = "backup"
        _sc.saveToFile(backup=True)

    _sc.game.event_unreg_listener("update", hook_update, "sssupdate")
    _sc.guiOnShow = False
    _sc.game.windowName = ""
    #_sc.game.skin_set(_sc.game_skin_saved)
    _sc.game.skin_set(_sc.game.gdata.sss_game_skin_saved)
    _sc.game.gdata.sss_game_skin_saved = None
    # _sc.game.isShowDevConsole = False
    # _sc.game.wwidth = _sc.originalwindowwidth
    # _sc.game.wheight = _sc.originalwindowheight
    # _sc.game.windowRect = Rect(Screen.width / 2 - _sc.game.wwidth / 2, Screen.height - _sc.game.wheight - 10,
    #                            _sc.game.wwidth, _sc.game.wheight)
    # _sc.game.windowCallback = _sc.originalWindowCallback


def setWindowName(index):
    global _sc
    names = {
        0: "SceneSaveState",
        1: "Pose Library",
        2: "Scene Utils",
        3: "Clip Manager"
    }

    if index in names.Keys:
        if index == 3:
            _sc.windowindex = 0
            _sc.game.windowName = names[0]
            #_sc.skin.controller.windowName = names[0]
            _sc.game._sup_toggle_vnframe_console()
            if not _sc.game.visible:
                _sc.game.visible = True

        else:
            _sc.windowindex = index
            #_sc.game.windowName = names[index] # old one
            if _sc.skin.controller != None:
                _sc.skin.controller.windowName = names[index]
    else:
        print "Invalid index:", index


def sceneConsoleWindowFunc(windowid):
    global _sc

    #_sc.scene_str_array = Array[String](_sc.scene_strings)
    #_sc.fset = Array[String](_sc.nameset[0])
    #_sc.mset = Array[String](_sc.nameset[1])
    # prev_cam_index = _sc.cur_cam
    # prev_sc_index = _sc.cur_index
    # _sc.prev_index = _sc.cur_index

    try:
        if not _sc.warning_param == None:
            warningUI(*_sc.warning_param)
        elif _sc.isFuncLocked == True:
            GUILayout.BeginVertical()
            GUILayout.Space(10)
            GUILayout.BeginHorizontal()
            GUILayout.Space(10)
            GUILayout.Label("<size=20>"+_sc.funcLockedText+"</size>")
            # GUILayout.Label(_sc.funcLockedText)
            GUILayout.Space(10)
            GUILayout.EndHorizontal()
            GUILayout.Space(10)
            GUILayout.EndVertical()
        else:
            GUILayout.BeginHorizontal()
            if GUILayout.Button("-", GUILayout.Width(45)):
                minimizeWindow()
            _sc.windowindex = GUILayout.Toolbar(_sc.windowindex, _sc.consolenames)
            GUILayout.EndHorizontal()
            GUILayout.Space(10)

            setWindowName(_sc.windowindex)
            # Scene Console
            if _sc.windowindex == 0:
                GUILayout.BeginVertical()
                _sc.subwinindex = GUILayout.Toolbar(_sc.subwinindex, _sc.options)
                GUILayout.Space(10)

                # Edit window
                if _sc.subwinindex == 0:
                    sceneConsoleEditUI()

                # Trackable window
                elif _sc.subwinindex == 1:
                    sceneConsoleTrackable()

                # Load/Save window
                elif _sc.subwinindex == 2:
                    sceneConsoleLdSvUI()

                # --------- Advanced controls -------------
                elif _sc.subwinindex == 3:
                    sceneConsoleAdvUI()

                # Ministates window
                elif _sc.subwinindex == 4:
                    sceneConsoleMinistates()

                # Render for advanced cam properties
                elif _sc.subwinindex == 100:
                    scenesavestate_vnssext.render_wizard_ui(_sc)

                GUILayout.FlexibleSpace()
                GUILayout.BeginHorizontal()
                # GUILayout.Label("<b>Warning:</b> Closing console removes all console data")
                global mod_version
                if GUILayout.Button("About v"+mod_version, GUILayout.Width(100)):
                    #resetConsole(_sc.game)
                    _sc.show_blocking_message_time_sc(
                        "SceneSaveState "+mod_version+"\n"
                        "\n"
                        "From @keitaro\n"
                        "Lightweight and crossplatform version of SceneConsole mod by @chickenManX\n"                                                      
                        "Original code by @chickenManX\n"
                        "Some cool features by @countd360\n"
                        "\n"
                        "Also includes:\n"
                        "Pose Library (by @keitaro, original code by @chickenManX)\n"
                        "Scene Utils (by @keitaro)\n"
                        "(with Body and Face Sliders) (by @countd360)\n"
                    , 5.0)
                GUILayout.FlexibleSpace()
                # if GUILayout.Button("Reset console", GUILayout.Width(100)):
                #     resetConsole(_sc.game)
                if GUILayout.Button("Clear scenes", GUILayout.Width(100)):
                    col = _sc.sel_font_col
                    _sc.warning_param = (_sc.clear_scenes,
                                         "Do you really want to delete ALL current scenes? (<b><color=%s>Warning:</color> All current scenedata will be deleted</b>)" % col,
                                         None, False)
                # if GUILayout.Button("Close SSS", GUILayout.Width(100)):
                #     col = _sc.sel_font_col
                #     _sc.warning_param = (sceneConsoleGUIClose,
                #                          "Do you really want to close window? (<b><color=%s>Warning:</color> All current scenedata will be deleted</b>)" % col,
                #                          None, False)
                GUILayout.EndHorizontal()
                GUILayout.EndVertical()

            # Pose Console
            elif _sc.windowindex == 1:

                _pc = posesavestate.init_from_sc(_sc.game)
                posesavestate.poseConsoleUIFuncs()
                #GUILayout.Label("No poses console for now ))")
            elif _sc.windowindex == 2:
                sceneUtilsUI()
    except Exception as e:
        import traceback
        print "sceneSaveStateWindowGUI Exception:"
        traceback.print_exc()
        sceneConsoleGUIClose()
        _sc.game.show_blocking_message_time("sceneSaveState error: " + str(e))


def warningUI(func, msg, func_param=None, single_op=False):
    GUILayout.Space(125)
    # GUILayout.FlexibleSpace()

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.Label(msg)
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()

    GUILayout.Space(125)
    GUILayout.BeginHorizontal()
    if not single_op == True:
        if GUILayout.Button("Yes", GUILayout.Height(100)):
            if func_param == None:
                func()
            elif isinstance(func_param, tuple):
                func(*func_param)
            else:
                func(func_param)
            _sc.warning_param = None
        if GUILayout.Button("Hell No!", GUILayout.Height(100)):
            _sc.warning_param = None
    else:
        GUILayout.FlexibleSpace()
        if GUILayout.Button("OK!", GUILayout.Height(100)):
            _sc.warning_param = None
        GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    # GUILayout.FlexibleSpace()


def sceneConsoleAdvUI():
    global _sc
    _sc = _sc
    """:type _sc:SceneConsole"""

    _sc.adv_scroll = GUILayout.BeginScrollView(_sc.adv_scroll)
    GUILayout.Label("<b>Advanced controls</b>")
    GUILayout.Space(10)
    GUILayout.Label("Change character name:")
    GUILayout.BeginHorizontal()
    _sc.charname = GUILayout.TextField(_sc.charname)
    if GUILayout.Button("Change selected", GUILayout.Width(110)):
        _sc.changeCharName(_sc.charname)
    GUILayout.EndHorizontal()
    GUILayout.Label("Status operations:")
    GUILayout.BeginHorizontal()
    if GUILayout.Button("Copy selected status"):
        _sc.copySelectedStatus()
    if GUILayout.Button("Paste selected status"):
        _sc.pasteSelectedStatus()
    GUILayout.EndHorizontal()
    GUILayout.BeginHorizontal()
    if GUILayout.Button("Copy selected status 2"):
        _sc.copySelectedStatus2()
    if GUILayout.Button("Paste selected status 2"):
        _sc.pasteSelectedStatus2()
    GUILayout.EndHorizontal()
    GUILayout.BeginHorizontal()
    if GUILayout.Button("Copy selected status to tracking char with same name"):
        _sc.copySelectedStatusToTracking()



    # if GUILayout.Button("(without Pos)"):
    #     _sc.copySelectedStatusToTracking(["pos"])
    GUILayout.EndHorizontal()
    #GUILayout.Space(15)
    GUILayout.BeginHorizontal()
    if GUILayout.Button("VN: all cameras on"):
        _sc.camSetAll(True)
    if GUILayout.Button("VN: all cameras off"):
        _sc.camSetAll(False)
    GUILayout.EndHorizontal()
    """
    GUILayout.BeginHorizontal()
    if GUILayout.Button("VN: add Fake Lip Sync Ext, if no"):
        import vnscenescript
        header = vnscenescript.get_headerfolder(_sc.game)
        if header:
            # vnscenescript.addaction_to_headerfolder(_sc.game, ":useext:flipsync10")
            # vnscenescript.addaction_to_headerfolder(_sc.game, ":a:i:initflipsync:v10")
            add_folder_if_not_exists(":useext:flipsync10", ":useext:flipsync", header)
            add_folder_if_not_exists(":a:i:initflipsync:v10", ":a:i:initflipsync:", header)
            _sc.show_blocking_message_time_sc("Done!")
        else:
            _sc.show_blocking_message_time_sc("Please, export VN at least one time before add Fake Lip Sync")
    GUILayout.EndHorizontal()
    """
    GUILayout.BeginHorizontal()     # Fake Lip Sync with option
    import vngelipsync    
    if GUILayout.Button("VN: add Fake Lip Sync Ext: " + ("<color=#00ff00>ON</color>" if _sc.vnExportFakeLipSync else "<color=#ff0000>OFF</color>")):
        _sc.vnExportFakeLipSync = not _sc.vnExportFakeLipSync
    if _sc.vnExportFakeLipSync:
        GUILayout.Label("Ver:", GUILayout.Width(30))
        if GUILayout.Button(_sc.vnExportFakeLipSyncVer + ":" + vngelipsync.fls_version_description[_sc.vnExportFakeLipSyncVer], GUILayout.Width(120)):
            cidx = vngelipsync.fls_valid_version.index(_sc.vnExportFakeLipSyncVer)
            cidx = (cidx + 1) % len(vngelipsync.fls_valid_version)
            _sc.vnExportFakeLipSyncVer = vngelipsync.fls_valid_version[cidx]
        GUILayout.Label("Speed:", GUILayout.Width(45))
        _sc.vnExportFakeLipSyncSpd = GUILayout.TextField(_sc.vnExportFakeLipSyncSpd, GUILayout.Width(40))
        try:
            testf = float(_sc.vnExportFakeLipSyncSpd)
            if testf < 1:
                raise Exception()
        except:
            _sc.vnExportFakeLipSyncSpd = "12.0"
    GUILayout.EndHorizontal()

    GUILayout.Space(20)

    _sc.paramSceneListShowThumb = GUILayout.Toggle(_sc.paramSceneListShowThumb, "Scene list: show thumbnails")
    GUILayout.Space(10)

    _sc.paramSceneListShowLabel = GUILayout.Toggle(_sc.paramSceneListShowLabel, "Scene list: show labels")
    GUILayout.Space(10)

    _sc.autoLoad = GUILayout.Toggle(_sc.autoLoad, "Load scene on select")
    GUILayout.Space(10)

    _sc.autoAddCam = GUILayout.Toggle(_sc.autoAddCam, "Auto add cam for new scenes")
    GUILayout.Space(10)

    _sc.promptOnDelete = GUILayout.Toggle(_sc.promptOnDelete, "Prompt before delete (scene/cam/chars)")
    GUILayout.Space(10)

    _sc.skipClothesChanges = GUILayout.Toggle(_sc.skipClothesChanges, "Don't process clothes changes on scene change")
    GUILayout.Space(10)

    _sc.paramAnimCamIfPossible = GUILayout.Toggle(_sc.paramAnimCamIfPossible, "Animate cam if possible")
    GUILayout.Space(10)

    # CertainLSP: New config options in GUI
    GUILayout.Space(10)
    _sc.HideAddSelectedToTrackInPreviousScenes = GUILayout.Toggle(_sc.HideAddSelectedToTrackInPreviousScenes,
                                                                  "When tracking new chars/props, hide them in previous scenes")
    GUILayout.Space(10)

    _sc.AddCamInsertsRightAfter = GUILayout.Toggle(_sc.AddCamInsertsRightAfter,
                                                   "When adding new cameras, insert right after current camera")
    GUILayout.Space(10)

    GUILayout.BeginHorizontal()
    GUILayout.Label("Camera anim params: duration ")
    _sc.paramAnimCamDuration = GUILayout.TextField(_sc.paramAnimCamDuration, GUILayout.Width(40))
    GUILayout.Label(", zoom-out")
    _sc.paramAnimCamZoomOut = GUILayout.TextField(_sc.paramAnimCamZoomOut, GUILayout.Width(40))
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()



    # Debug purpose
    if GUILayout.Button("Print block data"):
        print "::::::::::::Debug::::::::::::"
        """
        for i in range(len(_sc.temp_states)):
            for j in range(len(_sc.temp_states[i])):
                print ("FK for char[%d][%d]:"%(i,j))
                for key in sorted(_sc.temp_states[i][j]["fk_set"].keys()):
                    print key,":",_sc.temp_states[i][j]["fk_set"][key]
        """
        # print "_sc.cur.index :",_sc.cur_index
        # print "_sc.nameset :",_sc.nameset
        # print "_sc.block[_sc.cur_index].mchars :",_sc.block[_sc.cur_index].mchars
        # print "_sc.block[_sc.cur_index].fchars :",_sc.block[_sc.cur_index].fchars
        # print "_sc.block[_sc.cur_index].props :", _sc.block[_sc.cur_index].props
    if GUILayout.Button("Print char data"):
        print "::::::::::::Debug::::::::::::"
        char = getSelectedChar(_sc.game, mult=False)
        if not char == None:
            state = char.export_full_status()
            fk_dic = state["fk_set"]
            print "fk_set = {"
            for k, v in fk_dic.items():
                print k, ":", v, ","
            print "}"

    if GUILayout.Button("Print Item FK"):
        print "::::::::::::Debug::::::::::::"
        obj = getSelectedItem(_sc.game, all=False)
        if not obj == None:
            obst = obj.export_full_status()
            if "fk_set" in obst.keys():
                for k, v in obst["fk_set"].items():
                    print k, ":", v
        # print "isAnime:",obj.isAnime
        # print "+++++++++++++"
        # print "_sc.block[last].props :", _sc.block[-1].props

    GUILayout.Space(25)

    GUILayout.Label("<b>Shortcut settings</b>")
    GUILayout.Space(10)
    GUILayout.BeginHorizontal()
    cnt = 0
    for command in sorted(_sc.shortcuts.keys()):
        GUILayout.Label("%s:" % command, GUILayout.Width(110))
        _sc.shortcuts[command] = GUILayout.TextField(_sc.shortcuts[command], GUILayout.Width(120))
        GUILayout.FlexibleSpace()
        cnt += 1
        if cnt % 2 == 0:
            GUILayout.EndHorizontal()
            GUILayout.BeginHorizontal()
    GUILayout.EndHorizontal()
    if GUILayout.Button("Save config", GUILayout.Height(50)):
        saveConfig()

    GUILayout.EndScrollView()


def sceneConsoleTrackable():
    global _sc

    #if _sc is SceneConsole:


    # _sc.svname = GUILayout.TextField(_sc.svname)
    # GUILayout.Space(35)
    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.Label(
        " ---------------------------------    Operations    ------------------------------------")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(15)

    GUILayout.BeginHorizontal()
    GUILayout.Space(40)
    if GUILayout.Button("Add selected", GUILayout.Height(50), GUILayout.Width(160)):
        _sc.addSelectedToTrack()

    GUILayout.Space(15)
    if GUILayout.Button("Del selected", GUILayout.Height(50), GUILayout.Width(160)):
        _sc.delSelectedFromTrack()

    GUILayout.Space(15)
    if GUILayout.Button("Refresh", GUILayout.Height(50), GUILayout.Width(80)):
        _sc.game.scenef_register_actorsprops()

    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()

    GUILayout.BeginHorizontal()
    GUILayout.Space(40)
    if not _sc.isSysTracking():
        if GUILayout.Button("Track scene environment\n<color=#ff0000>OFF</color>", GUILayout.Height(50), GUILayout.Width(160)):
            _sc.addSysTracking()
    else:
        if GUILayout.Button("Track scene environment\n<color=#00ff00>ON</color>", GUILayout.Height(50), GUILayout.Width(160)):
            _sc.delSysTracking()
    GUILayout.EndHorizontal()

    GUILayout.Space(15)

    GUILayout.BeginHorizontal()
    GUILayout.Space(40)
    _sc.uiTrackingShowAdvanced = GUILayout.Toggle(_sc.uiTrackingShowAdvanced, "Advanced functions", GUILayout.Height(20),
                                        GUILayout.Width(160))
    GUILayout.EndHorizontal()

    if _sc.uiTrackingShowAdvanced:

        GUILayout.BeginHorizontal()
        GUILayout.Space(40)
        GUILayout.Label("Pro: Change selected char ID to ", GUILayout.Width(210))
        #GUILayout.Label("  Who say:", GUILayout.Width(80))
        _sc.newid = GUILayout.TextField(_sc.newid, GUILayout.Width(120))
        if GUILayout.Button("Change",GUILayout.Width(60)):
            #_sc.cam_whosay = _sc.get_next_speaker(_sc.cam_whosay, False)
            _sc.changeSelTrackID(_sc.newid)
        GUILayout.EndHorizontal()

        GUILayout.BeginHorizontal() # change actor's color and title
        GUILayout.Space(40)
        GUILayout.Label("VN: Setup selected char's color and title in VN talking window:")
        GUILayout.EndHorizontal()
        GUILayout.BeginHorizontal()
        GUILayout.Space(65)
        GUILayout.Label("Color code:")
        _sc.newCharColor = GUILayout.TextField(_sc.newCharColor, GUILayout.Width(60))
        GUILayout.Label(" Title (empty for default):")
        _sc.newCharTitle = GUILayout.TextField(_sc.newCharTitle, GUILayout.Width(90))
        if GUILayout.Button("Change",GUILayout.Width(60)):
            _sc.changeSelColorTitle(_sc.newCharColor, _sc.newCharTitle)
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()

        GUILayout.Space(15)

        GUILayout.BeginHorizontal()
        GUILayout.Space(40)
        if GUILayout.Button("<color=#ff0000>Cleanup</color> scene data\nfrom unknown char/props", GUILayout.Height(50), GUILayout.Width(160)):
            res = _sc.delUnusedCharsProps()
            _sc.show_blocking_message_time_sc(res)
        GUILayout.EndHorizontal()



    GUILayout.Space(15)
    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.Label(
        " ----------------------------------------    Tracking chars/props     ----------------------------------------")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(15)

    #GUILayout.BeginHorizontal()
    _sc.tracking_scroll = GUILayout.BeginScrollView(_sc.tracking_scroll)
    GUILayout.Label("Actors:")
    actors = _sc.game.scenef_get_all_actors()
    txt = ""
    for actorid in actors:
        #GUILayout.Label("  "+actorid+": "+actors[actorid].text_name)
        #txt += "  "+actorid+": "+actors[actorid].text_name+"\n"
        #GUILayout.Label(txt)
        actor = actors[actorid]
        """:type actor:Actor"""
        render_ui_for_tracking(actorid,actor)

    GUILayout.Label("Props:")
    props = _sc.game.scenef_get_all_props()
    for propid in props:
        render_ui_for_tracking(propid,props[propid])

    GUILayout.EndScrollView()

    """
    GUILayout.Space(50)
    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.Label(
        " ----------------------------    Load from backup (scene/external file)   ---------------------------")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(15)

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    if GUILayout.Button("Load backup scene data", GUILayout.Height(80), GUILayout.Width(210)):
        fld = getFolder(_sc.game, "-scfile:", False)
        if len(_sc.block) > 0:
            if fld == None:
                _sc.warning_param = (
                _sc.loadSceneData, 'Do you wish to load backup scenedata from scene? (Will overwrite console data)',
                (False, True), False)
            else:
                _sc.warning_param = (
                _sc.loadSceneData, 'Do you wish to load backup scenedata from file? (Will overwrite console data)',
                (True, True), False)
        elif fld == None:
            _sc.loadSceneData(backup=True)
        else:
            _sc.loadSceneData(file=True, backup=True)
    # if GUILayout.Button("Save backup scene data",GUILayout.Height(100),GUILayout.Width(210)):
    # _sc.saveSceneData(backup = True)
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    """

def render_ui_for_tracking(id,elem):
    """:type elem:HSNeoOCI"""
    global _sc


    txt = id + ": " + elem.text_name
    GUILayout.BeginHorizontal()
    GUILayout.Space(20)
    btntext = ""
    if elem.visible_treenode:
        btntext = "v"
    if GUILayout.Button(btntext, GUILayout.Width(22)):
        elem.visible_treenode = not elem.visible_treenode

    isSelected = treenode_check_select(elem.treeNodeObject)
    if GUILayout.Button(btntext_get_if_selected(txt,isSelected)):
        _sc.game.studio.treeNodeCtrl.SelectSingle(elem.treeNodeObject)

    #GUILayout.Label(txt)
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()

def btntext_get_if_selected(btntext,isSelected):
    global _sc
    if isSelected:
        col = _sc.sel_font_col
    else:
        col = _sc.nor_font_col
    return "<color=%s>%s</color>" % (col, btntext)

def btntext_get_if_selected2(btntext,isSelected):
    global _sc
    if isSelected:
        col = "#f8e473"
    else:
        col = _sc.nor_font_col
    return "<color=%s>%s</color>" % (col, btntext)

def recalc_autostates():
    global _sc
    ar = HSNeoOCIFolder.find_all_startswith("-msauto:vis:")
    ar.sort(key=sort_by_textname)
    _sc.arAutoStatesItemsVis = ar
    ar2 = HSNeoOCIFolder.find_all_startswith("-msauto:choice:")
    ar2.sort(key=sort_by_textname)
    _sc.arAutoStatesItemsChoice = ar2

def sort_by_textname(el):
    return el.treeNodeObject.textName

def sceneConsoleMinistates():
    global _sc
    _sc = _sc
    """:type _sc:SceneConsole"""

    # updating autostates - every 200 step
    if _sc.updAutoStatesTimer == 0:
        recalc_autostates()
    _sc.updAutoStatesTimer = (_sc.updAutoStatesTimer + 1) % 200

    tableLabelW = 90
    tableBtnW = 125
    tablePadding = 10

    # _sc.svname = GUILayout.TextField(_sc.svname)
    # GUILayout.Space(35)
    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.Label(
        "Ministates - add states only for selected actors+props. No tracking. Auto-save into scene.\nYou can use prefixes, naming by \"prefix-name\"")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(15)

    GUILayout.BeginHorizontal()
    GUILayout.Space(tablePadding)
    if GUILayout.Button("Add state", GUILayout.Width(200)):
        _sc.addSelectedMini()
    GUILayout.FlexibleSpace()
    GUILayout.Label("(optional) custom name: ")
    # GUILayout.Label("  Who say:", GUILayout.Width(80))
    _sc.mininewid = GUILayout.TextField(_sc.mininewid, GUILayout.Width(120))
    GUILayout.Space(tablePadding)
    GUILayout.EndHorizontal()

    GUILayout.BeginHorizontal()
    GUILayout.Space(tablePadding)
    _sc.isUseMsAuto = GUILayout.Toggle(_sc.isUseMsAuto, "Use auto-states (operations with selected props)")
    GUILayout.Space(tablePadding)
    GUILayout.EndHorizontal()

    if _sc.isUseMsAuto:
        GUILayout.BeginHorizontal()
        GUILayout.Space(tablePadding)
        if GUILayout.Button("Add Show/Hide", GUILayout.Width(100)):
            _sc.addSelectedAutoShow("vis")
        if GUILayout.Button("Add Choice", GUILayout.Width(100)):
            _sc.addSelectedAutoShow("choice")
        if GUILayout.Button("Del selected", GUILayout.Width(100)):
            _sc.delSelectedAutoShow()

        GUILayout.FlexibleSpace()
        GUILayout.Label("(opt) name: ")
        # GUILayout.Label("  Who say:", GUILayout.Width(80))
        _sc.autoshownewid = GUILayout.TextField(_sc.autoshownewid, GUILayout.Width(100))
        GUILayout.Space(tablePadding)
        GUILayout.EndHorizontal()

        GUILayout.BeginHorizontal()
        GUILayout.Space(tablePadding)
        GUILayout.FlexibleSpace()
        GUILayout.Space(tablePadding)
        GUILayout.EndHorizontal()


    GUILayout.Space(20)

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.Label(
        " ----------------------------------------    Ministates     ----------------------------------------")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(15)

    GUILayout.BeginHorizontal()
    GUILayout.Space(tablePadding)

    _sc.miniset_scroll = GUILayout.BeginScrollView(_sc.miniset_scroll)
    #for i in range(500):
    #    GUILayout.Label("State %s" % (str(i)))
    mslist = ministates_get_list(_sc.game)

    # calculating prfixes
    arPrefixes = ['']
    for el in mslist:
        #mstate = HSNeoOCIFolder.create_from_treenode(fldMiniState)
        ar = ministates_calc_prefix(el[0])
        if ar[0] in arPrefixes:
            pass
        else:
            arPrefixes.append(ar[0])

    # rendering ministates
    for prefix in arPrefixes:
        GUILayout.Space(6)
        GUILayout.BeginHorizontal()

        prefixtxt = prefix
        if prefixtxt == "":
            prefixtxt = "(default)"

        GUILayout.Label(prefixtxt+":",GUILayout.Width(tableLabelW))
        GUILayout.BeginVertical()

        GUILayout.BeginHorizontal()
        i = 0
        for el in mslist:

            ar = ministates_calc_prefix(el[0])
            if ar[0] == prefix:
                i += 1
                if GUILayout.Button(ar[1], GUILayout.Width(tableBtnW)):
                    try:
                        ministates_run_elem(_sc.game, el[1])
                    except Exception, e:
                        _sc.show_blocking_message_time_sc("Error during set state: %s" % (str(e)))
                        #return

            #if i != 0 and (i % 3 == 0):

            if i % 3 == 0:
                GUILayout.FlexibleSpace()
                GUILayout.EndHorizontal()
                GUILayout.BeginHorizontal()


        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()

        GUILayout.EndVertical()
        GUILayout.EndHorizontal()


    try:
        # trying auto states - to avoid errors during making UI
        for el0 in _sc.arAutoStatesItemsVis:
            el = el0.treeNodeObject.parent
            if el.textName != "":
                pass

        for el0 in _sc.arAutoStatesItemsChoice:
            el = el0.treeNodeObject.parent
            if el.textName != "":
                pass
            for el2 in el.child:
                if el2.textName != "":
                    pass
                if el2.visible:
                    pass



        # rendering auto vis
        if len(_sc.arAutoStatesItemsVis) > 0:
            GUILayout.Space(6)
            GUILayout.BeginHorizontal()

            GUILayout.Label("A SHOW/HIDE:", GUILayout.Width(tableLabelW+5))
            GUILayout.BeginVertical()

            GUILayout.BeginHorizontal()
            i = 0
            for vis in _sc.arAutoStatesItemsVis:
                vis = vis
                """:type vis:HSNeoOCIFolder"""
                ar = vis.text_name.split(":")
                i += 1
                try:
                    if ar[1] == "vis":
                        if GUILayout.Button(btntext_get_if_selected2(ar[2],vis.treeNodeObject.parent.visible), GUILayout.Width(tableBtnW)):
                            vis.treeNodeObject.parent.visible = not vis.treeNodeObject.parent.visible
                            if vis.treeNodeObject.parent.visible:
                                if treenode_check_select(vis.treeNodeObject.parent):
                                    pass
                                else:
                                    _sc.game.studio.treeNodeCtrl.SelectSingle(vis.treeNodeObject.parent)
                            else:
                                if treenode_check_select(vis.treeNodeObject.parent):
                                    _sc.game.studio.treeNodeCtrl.SelectSingle(vis.treeNodeObject.parent)
                                else:
                                    pass
                except Exception, e:
                    _sc.show_blocking_message_time_sc("Error during set visible: %s" % (str(e)))
                        # return

                # if i != 0 and (i % 3 == 0):

                if i % 3 == 0:
                    GUILayout.FlexibleSpace()
                    GUILayout.EndHorizontal()
                    GUILayout.BeginHorizontal()

            GUILayout.FlexibleSpace()
            GUILayout.EndHorizontal()

            GUILayout.EndVertical()
            GUILayout.EndHorizontal()

        # rendering choices
        for itchoice in _sc.arAutoStatesItemsChoice:
            GUILayout.Space(6)
            GUILayout.BeginHorizontal()

            lbname = "--tmp--"


            itchoice = itchoice
            """:type itchoice:HSNeoOCIFolder"""
            try:
                ar = itchoice.text_name.split(":")
                lbname = ar[2]
            except Exception, e:
                print "Err during calc label name..."
                pass

            #GUILayout.Label("A "+lbname + ":", GUILayout.Width(tableLabelW))
            GUILayout.Label(lbname, GUILayout.Width(tableLabelW))
            GUILayout.BeginVertical()

            GUILayout.BeginHorizontal()
            i = 0
            for el in itchoice.treeNodeObject.parent.child:
                el = el
                """:type el:dummyneoclasses.TreeNodeObject"""


                if not el.textName.startswith("-msauto:"):
                    i += 1
                    try:
                        btntext = btntext_get_if_selected2(el.textName,el.visible)
                        if GUILayout.Button(btntext, GUILayout.Width(tableBtnW)):
                            if el.visible:
                                el.visible = False
                            else:
                                el.visible = True
                                for el2 in itchoice.treeNodeObject.parent.child:
                                    if el2 != el:
                                        el2.visible = False
                            _sc.game.studio.treeNodeCtrl.SelectSingle(el)
                    except Exception, e:
                        print "Err during render button choice..."


                    if i % 3 == 0:
                        GUILayout.FlexibleSpace()
                        GUILayout.EndHorizontal()
                        GUILayout.BeginHorizontal()

            GUILayout.FlexibleSpace()
            GUILayout.EndHorizontal()

            GUILayout.EndVertical()
            GUILayout.EndHorizontal()

    except Exception, e:
        #print "VNGE SSS: try to recalc autostates...."
        GUILayout.Label(color_text_red("Trying to get autostates folders...."))
        recalc_autostates()
        #return

    # end of all elements
    GUILayout.EndScrollView()
    GUILayout.Space(tablePadding)
    GUILayout.EndHorizontal()





def sceneConsoleLdSvUI():
    global _sc
    _sc = _sc
    """:type _sc:SceneConsole"""
    # _sc.svname = GUILayout.TextField(_sc.svname)
    # GUILayout.Space(35)
    btnBigHeight = 60
    btnSmallHeight = 50

    _sc.saveload_scroll = GUILayout.BeginScrollView(_sc.saveload_scroll)




    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    if _sc.game.isSceneDataSaveSupported:
        try:
            import utf8texts
            GUILayout.Label(
                "<color=#00ff00>SSS data will be autosaved in PNG file. Please, don't use manual Save.\n"+utf8texts.sssDataWillBeSavedInPng+"</color>")
        except Exception as e:
            GUILayout.Label(
                "<color=#00ff00>SSS data will be autosaved in PNG file. Please, don't use manual Save.</color>")
    else:
        GUILayout.Label(
            "<color=#ff0000>SSS data will NOT be autosaved in PNG file. Please manually Save/Load.</color>")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(10)

    GUILayout.BeginHorizontal()
    GUILayout.Space(40)
    _sc.uiShowLoadSave = GUILayout.Toggle(_sc.uiShowLoadSave, "Indeed, show old Save/Load interface")
    GUILayout.EndHorizontal()

    GUILayout.Space(20)

    if _sc.uiShowLoadSave:
        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        GUILayout.Label(
            " ------------------------------------------    Data in scene folders    ------------------------------------------")
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()
        GUILayout.Space(15)

        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        if GUILayout.Button("<color=#00ff00>Load</color> scene data\nfrom folders", GUILayout.Height(btnBigHeight), GUILayout.Width(210)):
            if len(_sc.block) > 0:
                _sc.warning_param = (
                _sc.loadSceneData, 'Do you wish to load scenedata from current scene? (Will overwrite console data)', None,
                False)
            else:
                _sc.loadSceneData()
        GUILayout.FlexibleSpace()
        if GUILayout.Button("<color=#ff0000>Save</color> scene data\nto folders", GUILayout.Height(btnBigHeight), GUILayout.Width(210)):
            # delete existing scenedata fld
            #fld = getFolder(_sc.game, "-scenesavestate", True)
            fld = HSNeoOCIFolder.find_single_startswith("-scenesavestate:")
            if not fld == None:
                _sc.warning_param = (_sc.saveSceneData, 'Scenedata exists. Overwrite?', fld, False)
            else:
                _sc.saveSceneData(fld=None, backup=False)
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()

        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        GUILayout.Space(210)
        GUILayout.FlexibleSpace()
        #_sc.isSaveCompact = GUILayout.Toggle(_sc.isSaveCompact, "Save compact (since 4.0)", GUILayout.Height(20), GUILayout.Width(210))
        #_sc.isSaveCompact = GUILayout.Toggle(_sc.isSaveCompact, "Save compact", GUILayout.Height(20),
        #                                     GUILayout.Width(100))
        _sc.isSaveVerify = GUILayout.Toggle(_sc.isSaveVerify, "Verify save", GUILayout.Height(20),
                                             GUILayout.Width(80))
        _sc.isSaveOld = GUILayout.Toggle(_sc.isSaveOld, "Old save 100%OK", GUILayout.Height(20),
                                            GUILayout.Width(125))
        # if GUILayout.Button("Save scene data", GUILayout.Height(80), GUILayout.Width(210)):
        #     # delete existing scenedata fld
        #     # fld = getFolder(_sc.game, "-scenesavestate", True)
        #     fld = HSNeoOCIFolder.find_single_startswith("-scenesavestate:")
        #     if not fld == None:
        #         _sc.warning_param = (_sc.saveSceneData, 'Scenedata exists. Overwrite?', fld, False)
        #     else:
        #         _sc.saveSceneData(fld=None, backup=False)
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()

        GUILayout.Space(20)

        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        GUILayout.Label(
            " ----------------------------------------    Data on external file    ----------------------------------------")
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()
        GUILayout.Space(15)

        GUILayout.BeginHorizontal()
        GUILayout.Space(40)
        GUILayout.Label("File name:")
        GUILayout.Space(20)
        _sc.svname = GUILayout.TextField(_sc.svname, GUILayout.Width(300))
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()
        GUILayout.Space(20)
        GUILayout.BeginHorizontal()
        GUILayout.FlexibleSpace()
        if GUILayout.Button("<color=#00ff00>Load</color> from file", GUILayout.Height(btnBigHeight), GUILayout.Width(210)):
            if len(_sc.block) > 0:
                _sc.warning_param = (
                _sc.loadSceneData, 'Do you wish to load scenedata from file? (Will overwrite console data)', (True, False),
                False)
            else:
                _sc.loadSceneData(file=True, backup=False)
        GUILayout.FlexibleSpace()
        if GUILayout.Button("<color=#ff0000>Save</color> to file", GUILayout.Height(btnBigHeight), GUILayout.Width(210)):
            # delete existing scenedata fld
            fld_str = "-scfile:" + _sc.svname
            fld = getFolder(_sc.game, _sc.svname, True)
            if not fld == None:
                _sc.warning_param = (_sc.saveToFile, 'Scenedata exists. Overwrite?', False, False)
            else:
                _sc.saveToFile(backup=False)
        GUILayout.FlexibleSpace()
        GUILayout.EndHorizontal()

        GUILayout.Space(30)

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.Label(
        " ----------------------------    Load from backup (scene/external file)   ---------------------------")

    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(15)

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    if GUILayout.Button("Load backup scene data\n(scene/external file)", GUILayout.Height(btnSmallHeight), GUILayout.Width(210)):
        fld = getFolder(_sc.game, "-scfile:", False)
        if len(_sc.block) > 0:
            if fld == None:
                _sc.warning_param = (
                    _sc.loadSceneData, 'Do you wish to load backup scenedata from scene? (Will overwrite console data)',
                    (False, True), False)
            else:
                _sc.warning_param = (
                    _sc.loadSceneData, 'Do you wish to load backup scenedata from file? (Will overwrite console data)',
                    (True, True), False)
        elif fld == None:
            _sc.loadSceneData(backup=True)
        else:
            _sc.loadSceneData(file=True, backup=True)
    GUILayout.FlexibleSpace()
    if GUILayout.Button("Load auto-timer backup file", GUILayout.Height(btnSmallHeight), GUILayout.Width(210)):
        #_sc.exportToVNSS()
        if len(_sc.block) > 0:
            _sc.warning_param = (
                _sc.loadSceneDataBackupTimer, 'Do you wish to load backup scenedata from file auto-saved by timer? (Will overwrite console data)',
                None, False)
        else:
            _sc.loadSceneDataBackupTimer()

    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.FlexibleSpace()
    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    # GUILayout.Label(
    #     " ----------------------------    Load from backup (scene/external file)   ---------------------------")
    GUILayout.Label(
        " -------------------------------    VN Export   ------------------------------")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()
    GUILayout.Space(15)

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()

    if GUILayout.Button("<color=#00ff00>Export</color> scenes and cams\nto VNSceneScript",GUILayout.Height(btnSmallHeight),GUILayout.Width(210)):
        _sc.exportToVNSS()
    #GUILayout.Space(210)

    GUILayout.FlexibleSpace()
    if GUILayout.Button("...or <color=#00ff00>run</color> VNSceneScript\nfrom beginning", GUILayout.Height(btnSmallHeight), GUILayout.Width(210)):
        _sc.runVNSS()
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    #GUILayout.Space(210)

    if _sc.game.isSceneDataSaveSupported:
        _sc.vnFastIsRunImmediately = GUILayout.Toggle(_sc.vnFastIsRunImmediately, "+ run from cur",
                                                       GUILayout.Height(20),
                                                       GUILayout.Width(105))
        _sc.vnExportToPNG = GUILayout.Toggle(_sc.vnExportToPNG, "script to PNG",
                                                      GUILayout.Height(20),
                                                      GUILayout.Width(105))
    else:
        _sc.vnFastIsRunImmediately = GUILayout.Toggle(_sc.vnFastIsRunImmediately, "+ run from cur",
                                                      GUILayout.Height(20),
                                                      GUILayout.Width(210))
    GUILayout.FlexibleSpace()
    if GUILayout.Button("from scene", GUILayout.Height(20), GUILayout.Width(105)):
        _sc.runVNSS("scene")
    if GUILayout.Button("from cam", GUILayout.Height(20), GUILayout.Width(105)):
        _sc.runVNSS("cam")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()

    GUILayout.FlexibleSpace()

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    # GUILayout.Label(
    #     " ----------------------------    Load from backup (scene/external file)   ---------------------------")
    GUILayout.Label(
        " -------------------------------    Cam VN texts export/import   ------------------------------")
    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()

    GUILayout.FlexibleSpace()
    GUILayout.Space(5)

    GUILayout.BeginHorizontal()
    GUILayout.FlexibleSpace()
    if GUILayout.Button("Export cam texts\nto sss_camtexts.txt", GUILayout.Height(btnSmallHeight), GUILayout.Width(210)):
        _sc.exportCamTexts()
    GUILayout.FlexibleSpace()
    if GUILayout.Button("Import cam texts\nfrom sss_camtexts.txt", GUILayout.Height(btnSmallHeight), GUILayout.Width(210)):
        _sc.importCamTexts()

    GUILayout.FlexibleSpace()
    GUILayout.EndHorizontal()

    GUILayout.EndScrollView()

def sceneConsoleEditUI():
    global _sc

    # fset = _sc.fset
    # mset = _sc.mset

    GUILayout.BeginHorizontal()

    GUILayout.BeginVertical()
    # Scene tab
    GUILayout.Label("Scene states ({0}/{1})".format(_sc.cur_index+1,len(_sc.block)))
    _sc.scene_scroll = GUILayout.BeginScrollView(_sc.scene_scroll, GUILayout.Width(_sc.viewwidth))
    if len(_sc.block) > 0:
        for i in range(len(_sc.block)):
            if i == _sc.cur_index:
                col = _sc.sel_font_col
            else:
                col = _sc.nor_font_col
            scn_name = "Scene %d"%(i+1) #_sc.scene_str_array[i]
            if len(_sc.block[i].cams) > 0 and _sc.block[i].cams[0][4].has_key("addparam") and _sc.block[i].cams[0][4].has_key("addprops") and _sc.block[i].cams[0][4]["addparam"]:
                addprops = _sc.block[i].cams[0][4]["addprops"]
                if addprops.has_key("a1") and addprops["a1"] and addprops.has_key("a1o") and addprops["a1o"].has_key("name"):
                    sname = addprops["a1o"]["name"]
                    if sname != None and len(sname.strip()) > 0:
                        scn_name = sname + " (%d)"%(i+1)

            if _sc.paramSceneListShowThumb:
                if _sc.block[i].thumbTex != None:
                    #if GUILayout.Button(_sc.block[i].thumbTex):
                    opts = (GUILayout.Width(180),GUILayout.Height(100))# will be applied as GUILayoutOption[], auto-converted
                    if GUILayout.Button(_sc.block[i].thumbTex,GUIStyle("label"),opts):
                        _sc.cur_index = i
                        _sc.loadCurrentScene()
                    #GUILayout.Space(-5)
            if _sc.paramSceneListShowLabel or _sc.block[i].thumbTex == None:
                if GUILayout.Button("<color=%s>%s</color>" % (col, scn_name),GUILayout.Width(160)):
                    _sc.cur_index = i
                    if _sc.autoLoad == True:
                        _sc.loadCurrentScene()
        # _sc.cur_index = GUILayout.SelectionGrid(_sc.cur_index,_sc.scene_str_array,1)
    GUILayout.EndScrollView()

    GUILayout.BeginHorizontal()
    if GUILayout.Button("Move up"):
        _sc.move_scene_up()
    if GUILayout.Button("Move down"):
        _sc.move_scene_down()
    GUILayout.EndHorizontal()
    GUILayout.EndVertical()

    GUILayout.BeginVertical() # cam / scene ops / VN stuff

    # Camera and scene ops
    GUILayout.BeginHorizontal()

    GUILayout.BeginVertical()
    GUILayout.Label("Cameras")

    if _sc.cur_index > -1 and len(_sc.block) > 0:
        _sc.cam_scroll = GUILayout.BeginScrollView(_sc.cam_scroll, GUILayout.Height(185),
                                                   GUILayout.Width(_sc.camviewwidth))

        for i in range(len(_sc.block[_sc.cur_index].cams)):
            if i == _sc.cur_cam:
                col = _sc.sel_font_col
            else:
                col = "#f9f9f9"

            cam = _sc.block[_sc.cur_index].cams[i]
            addparams = cam[4]


            GUILayout.BeginHorizontal()

            # show name if available
            camtxt = "Cam %s" % str(i)
            if addparams["addparam"]:
                if "addprops" in addparams:
                    addprops = addparams["addprops"]
                    if "a1" in addprops and addprops["a1"]:
                        if "name" in addprops["a1o"] and addprops["a1o"]["name"] != "":
                            camtxt = addprops["a1o"]["name"]

            if GUILayout.Button("<color=%s>%s</color>" % (col, camtxt)):
                _sc.cur_cam = i
                _sc.setCamera(False)
            if GUILayout.Button("<color=%s>a</color>" % (col), GUILayout.Width(22)):
                _sc.cur_cam = i
                _sc.setCamera(True)
            GUILayout.EndHorizontal()

        GUILayout.EndScrollView()
        # _sc.cur_cam = GUILayout.SelectionGrid(_sc.cur_cam,_sc.scene_cam_str,1,GUILayout.Height(200),GUILayout.Width(125))
        # if not _sc.cur_cam == prev_cam_index:
        # _sc.setCamera()
        GUILayout.Space(15)
        GUILayout.BeginHorizontal()
        if GUILayout.Button("Add", GUILayout.Width(_sc.camviewwidth * 0.7)):
            _sc.changeSceneCam("add")
        if GUILayout.Button("Del", GUILayout.Width(_sc.camviewwidth * 0.3)):
            if _sc.promptOnDelete:
                _sc.warning_param = (_sc.changeSceneCam, "Delete selected cam?", "del", False)
            else:
                _sc.changeSceneCam("del")
        GUILayout.EndHorizontal()
        if GUILayout.Button("Update", GUILayout.Width(_sc.camviewwidth + 5)):
            _sc.changeSceneCam("upd")
        GUILayout.Label("Move cam:")

        GUILayout.BeginHorizontal()
        up = u'\u2191'
        down = u'\u2193'
        if GUILayout.Button(up, GUILayout.Width(_sc.camviewwidth / 2)):
            _sc.move_cam_up()
        if GUILayout.Button(down, GUILayout.Width(_sc.camviewwidth / 2)):
            _sc.move_cam_down()
        GUILayout.EndHorizontal()


    GUILayout.EndVertical()

    #GUILayout.Space(10)

    GUILayout.BeginVertical()

    GUILayout.Label("Navigation")

    GUILayout.BeginHorizontal()
    GUILayout.BeginVertical()
    if GUILayout.Button("< Previous",GUILayout.Height(35)):
        _sc.goto_prev()
    if GUILayout.Button("< Prev scene", GUILayout.Height(35)):
        _sc.goto_prev_sc()
    GUILayout.EndVertical()

    GUILayout.BeginVertical()
    if GUILayout.Button("Next >",GUILayout.Height(35)):
        _sc.goto_next()
    if GUILayout.Button("Next scene >", GUILayout.Height(35)):
        _sc.goto_next_sc()
    GUILayout.EndVertical()
    GUILayout.EndHorizontal()

    GUILayout.Space(10)

    GUILayout.Label("Scene operations")

    if GUILayout.Button("Add scene", GUILayout.Height(55)):
        _sc.addAuto()

    GUILayout.BeginHorizontal()
    if GUILayout.Button("Update scene", GUILayout.Height(55)):
        _sc.addAuto(addsc=False)
    GUILayout.BeginVertical()
    if GUILayout.Button("Insert scene", GUILayout.Height(25)):
        _sc.addAuto(insert=True)
    if GUILayout.Button("Dup scene", GUILayout.Height(25)):
        _sc.dupScene()
    GUILayout.EndVertical()
    GUILayout.EndHorizontal()

    GUILayout.Space(10)
    if GUILayout.Button("Delete scene"):
        if _sc.promptOnDelete == True:
            _sc.warning_param = (_sc.removeScene, "Delete selected scene?", None, False)
        else:
            _sc.removeScene()

    GUILayout.Space(10)
    GUILayout.BeginHorizontal()
    if _sc.cur_index > -1 and _sc.cur_cam > -1:
        if GUILayout.Button("Copy cam set"):
            _sc.copyCamSet()

    if _sc.cur_index > -1 and not _sc.camset == []:
        if GUILayout.Button("Paste cam set"):
            _sc.pasteCamSet()
    else:
        GUILayout.Label("")
    GUILayout.EndHorizontal()

    if not _sc.autoLoad == True:
        GUILayout.Space(10)
        if GUILayout.Button("Load Scene", GUILayout.Height(35)):
            _sc.loadCurrentScene()


    # if get_ini_value_def_int("ShowButtonsNextPrevScene",1) == 1:
    #     GUILayout.Space(10)




    GUILayout.EndVertical() # end scene buttons

    GUILayout.EndHorizontal()

    # char texts
    GUILayout.Space(10)
    GUILayout.BeginHorizontal()
    _sc.cam_addparam = GUILayout.Toggle(_sc.cam_addparam, "  Use cam in Visual Novel")
    GUILayout.FlexibleSpace()
    if _sc.cam_addparam:
        txt = btntext_get_if_selected2("More", _sc.cam_addprops["a1"] or  _sc.cam_addprops["a2"])
        if GUILayout.Button(txt, GUILayout.Height(20)):
            if _sc.cur_index == -1 or _sc.cur_cam == -1:
                _sc.show_blocking_message_time_sc("Please, add at least one scene/cam")
            else:
                _sc.subwinindex = 100
    GUILayout.EndHorizontal()
    #GUILayout.Label("  Replics for VN for cam (not necessary):")

    # if GUILayout.Button("Add scene (selected only)"):
    #     _sc.addAuto(allbase=False)
    # if GUILayout.Button("Delete duplicate characters"):
    #     _sc.removeDuplicates()
    if _sc.cam_addparam:
        GUILayout.BeginHorizontal()
        GUILayout.Label("  Who say:", GUILayout.Width(90))

        _sc.cam_whosay = GUILayout.TextField(_sc.cam_whosay, GUILayout.Width(210))
        if GUILayout.Button("<", GUILayout.Width(20)):
            _sc.cam_whosay = _sc.get_next_speaker(_sc.cam_whosay, False)
        if GUILayout.Button(">", GUILayout.Width(20)):
            _sc.cam_whosay = _sc.get_next_speaker(_sc.cam_whosay, True)
        GUILayout.EndHorizontal()

        GUILayout.BeginHorizontal()
        GUILayout.Label("  What say:", GUILayout.Width(90))
        _sc.cam_whatsay = GUILayout.TextField(_sc.cam_whatsay, GUILayout.Width(210))
        if GUILayout.Button("X", GUILayout.Width(20)):
            _sc.cam_whatsay = ""
        if GUILayout.Button("...", GUILayout.Width(20)):
            _sc.cam_whatsay = "..."
        GUILayout.EndHorizontal()
        GUILayout.Space(5)
        GUILayout.BeginHorizontal()
        GUILayout.Label("  Adv VN cmds", GUILayout.Width(90))
        _sc.cam_addvncmds = GUILayout.TextArea(_sc.cam_addvncmds, GUILayout.Width(235), GUILayout.Height(55))
        if GUILayout.Button("X", GUILayout.Width(20)):
            _sc.cam_addvncmds = ""
        # if GUILayout.Button("X", GUILayout.Width(20)):
        #     _sc.cam_whatsay = ""
        # if GUILayout.Button("...", GUILayout.Width(20)):
        #     _sc.cam_whatsay = "..."
        GUILayout.EndHorizontal()



    GUILayout.EndVertical()
    GUILayout.EndHorizontal()

    # if not _sc.prev_index == _sc.cur_index and not _sc.cur_index < 0:
    # _sc.loadCurrentScene()


# Minimize
def minimizeWindow():
    if _sc.skin.controller.windowRect.width > 200:
        _sc.consoleWidth = _sc.skin.controller.windowRect.width
        _sc.consoleHeight = _sc.skin.controller.windowRect.height
        _sc.skin.controller.windowRect.width = 110
        _sc.skin.controller.windowRect.height = 130
        # Rect (Screen.width / 2 - _sc.game.wwidth * 1.5, Screen.height - _sc.game.wheight - 500,
        #               110, 75)
        #_sc.game.windowCallback = GUI.WindowFunction(minimizeWindowFunc)
        _sc.skin.funcWindowGUI = sceneConsoleSkinWindowGUIMin
    else:
        _sc.skin.controller.windowRect.width = _sc.consoleWidth
        _sc.skin.controller.windowRect.height = _sc.consoleHeight
        _sc.skin.funcWindowGUI = sceneConsoleSkinWindowGUI
        #_sc.game.windowCallback = GUI.WindowFunction(sceneConsoleWindowFunc)


def minimizeWindowFunc(windowid):
    global _sc

    try:
        GUILayout.BeginVertical()

        GUILayout.BeginHorizontal()
        if GUILayout.Button("+", GUILayout.Height(25),GUILayout.Width(27)):
            _sc.skin.controller.windowRect.width = _sc.consoleWidth
            _sc.skin.controller.windowRect.height = _sc.consoleHeight
            _sc.skin.funcWindowGUI = sceneConsoleSkinWindowGUI
        GUILayout.FlexibleSpace()
        if GUILayout.Button("<", GUILayout.Height(25),GUILayout.Width(27)):
            _sc.goto_prev()
        GUILayout.FlexibleSpace()
        if GUILayout.Button(">", GUILayout.Height(25),GUILayout.Width(27)):
            _sc.goto_next()
        GUILayout.EndHorizontal()

        lbl = "Sc {0}/{1}".format(_sc.cur_index+1,len(_sc.block))
        try:
            if len(_sc.block) > 0:
                lbl += ", c {0}/{1}".format(_sc.cur_cam+1,len(_sc.block[_sc.cur_index].cams))
        except Exception, e:
            pass

        #GUILayout.BeginHorizontal()
        GUILayout.Label(lbl,GUILayout.Width(90))
        #GUILayout.EndHorizontal()
        #if GUILayout.Button("Expand", GUILayout.Width(90), GUILayout.Height(35)):

        #GUILayout.Space(2)
        if GUILayout.Button("Add scene", GUILayout.Width(90), GUILayout.Height(20)):
            _sc.addAuto()
        if GUILayout.Button("Add cam", GUILayout.Width(90), GUILayout.Height(20)):
            _sc.addCam(True)


        GUILayout.EndVertical()
    except Exception as e:
        import traceback
        print "sceneSaveStateWindowGUI Exception:"
        traceback.print_exc()
        sceneConsoleGUIClose()
        _sc.game.show_blocking_message_time("sceneSaveState error: " + str(e))


# ::::: Essential functions :::::
def getFolder(game, name, exact=False):
    flds = game.scene_get_all_folders()
    for fld in flds:
        if exact == False:
            if name in fld.text_name: return fld
        else:
            if name == fld.text_name: return fld


def getSelectedChar(game, mult=False):
    mtreeman = game.studio.treeNodeCtrl
    ar = []
    for node in mtreeman.selectNodes:
        ochar = HSNeoOCI.create_from_treenode(node)
        if isinstance(ochar.objctrl, OCIChar):
            ar.append(ochar.as_actor)

    if len(ar) > 0:
        if mult == False:
            return ar[0]
        else:
            am = []
            af = []
            for char in ar:
                if char.sex == 0:
                    am.append(char)
                else:
                    af.append(char)
            return [af, am]


def getSelectedItem(game, all=False):
    mtreeman = game.studio.treeNodeCtrl
    ar = []
    for node in mtreeman.selectNodes:
        oitem = HSNeoOCI.create_from_treenode(node)
        if isinstance(oitem.objctrl, OCIItem):
            ar.append(oitem.as_prop)
    if len(ar) > 0:
        if all == False:
            return ar[0]
        else:
            return ar
    else:
        raise Exception("No items selected")


# def getSelectedFolder(game, all=False):
#     mtreeman = game.studio.treeNodeCtrl
#     ar = []
#     for node in mtreeman.selectNodes:
#         ofld = HSNeoOCI.create_from_treenode(node)
#         if isinstance(ofld.objctrl, OCIFolder):
#             ar.append(PropSC(ofld.objctrl))
#     if len(ar) > 0:
#         if all == False:
#             return ar[0]
#         else:
#             return ar
#     # else:
#     # raise Exception("No folders selected")




# chara functions
def char_import_status_diff_optimized(self, status):
    ofs = self.export_full_status()
    dfs = {}
    for key in status.Keys:
        if not key in ofs.Keys or ofs[key] != status[key]:
            dfs[key] = status[key]
    #return dfs
    #print "Optimized import status diff, ", dfs
    self.import_status(dfs)

def get_status_diff_optimized(oldstatus, status):
    ofs = oldstatus
    dfs = {}
    for key in status.Keys:
        if not key in ofs.Keys or ofs[key] != status[key]:
            dfs[key] = status[key]
    #return dfs
    #print "Optimized import status diff, ", dfs
    return dfs

def is_local_equal(el1,el2):
    if el1 == el2:
        return True
    # if isinstance(el1, Vector3) or isinstance(el1, Vector2) or isinstance(el1, Color) or isinstance(
    #         el1, tuple):
    if json_encode(el1) == json_encode(el2):
        return True
    return False

def is_status_equal(oldstatus, status):
    if len(oldstatus) != len(status):
        return False
    ofs = oldstatus
    dfs = {}
    for key in status.Keys:
        if not key in ofs.Keys or ofs[key] != status[key]:
            #dfs[key] = status[key]
            if is_local_equal(ofs[key],status[key]):
                pass
            else:
                print "non-eq: ", ofs[key], status[key], type(ofs[key])
                return False
    # return dfs
    # print "Optimized import status diff, ", dfs
    return True

def is_status_statuses_equal(oldstatus, status):
    if len(oldstatus) != len(status):
        return False
    ofs = oldstatus
    dfs = {}
    for key in status.Keys:
        if not key in ofs.Keys or not is_status_equal(ofs[key], status[key]):
            #dfs[key] = status[key]
            return False
    # return dfs
    # print "Optimized import status diff, ", dfs
    return True

def is_status_equal_json(oldstatus, status):
    if len(oldstatus) != len(status):
        return False

    str1 = json_encode(oldstatus)
    str2 = json_encode(status)

    if str1 != str2:
        #print "neq json: ", str1, str2
        return False

    return True

def is_arr_statuses_equal(ar1,ar2):
    if len(ar1) != len(ar2):
        return False
    for i in range(len(ar1)):
        if is_status_equal(ar1[i],ar2[i]):
            pass
        else:
            return False

    return True

def is_arr_equal(ar1,ar2):
    if len(ar1) != len(ar2):
        return False
    for i in range(len(ar1)):
        if is_local_equal(ar1[i],ar2[i]):
            pass
        else:
            return False

    return True

def folder_add_child(parent,childtext):
    fold = HSNeoOCIFolder.add(childtext)
    fold.set_parent(parent)
    return fold

# scene utils UI
def sceneUtilsUI():
    global _sc
    """:type SceneConsole"""



    self = _sc.game
    skin_def = _sc.skinDefault

    # run scene utils if needed
    if(hasattr(_sc.game.gdata, "sceneUtilsSideApp")):
        pass
    else:
        _sc.game.gdata.sceneUtilsSideApp = True
        import sceneutils
        sceneutils.start(_sc.game)

    if not self.isFuncLocked:
        if not self.isShowDevConsole:
            try:
                skin_def.render_main(self.curCharFull, self.vnText, self.vnButtons, self._vnButtonsActions,
                                      self.vnButtonsStyle)
            except Exception, e:
                print "Error in skin.render_main, ", str(e)

        else:  # show dev console
            try:
                skin_def.render_dev_console()
            except Exception, e:
                print "Error in skin.render_dev_console, ", str(e)
    else:  # render system message
        skin_def.render_system(self.funcLockedText)

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

# tree node
def treenode_check_select(treenode):
    global _sc
    game = _sc.game
    """:type game:vngameengine.VNNeoController"""
    if game.isCharaStudio:
        return game.studio.treeNodeCtrl.CheckSelect(treenode)
    else:
        return False

# util colors

def color_text(text,color):
    return '<color=#{1}ff>{0}</color>'.format(text,color)

def color_text_green(text):
    return color_text(text,"aaffaa")

def color_text_red(text):
    return color_text(text,"ffaaaa")

def color_text_yellowlight(text):
    return color_text(text, "f8e473")

def color_text_blue(text):
    return color_text(text,"aaaaff")

# config ini values
# ini file

_iniOptions = None

def get_ini_value(elem): # get ini value for cur engine
    global _iniOptions
    if _iniOptions != None:
        # already parsed
        pass
    else:
        # need to parse and cache
        _iniOptions = {}

        import ConfigParser, sys, os.path
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.splitext(__file__)[0] + '_config.ini')

        for k, v in config.items("Options"):
            _iniOptions[k.lower()] = v


    # main code
    #print _iniOptions
    elemlower = elem.lower()
    if elemlower in _iniOptions:
        return _iniOptions[elemlower]

    return None

def get_ini_value_def_int(elem,defint):
    val = get_ini_value(elem)
    if val == None:
        return defint
    else:
        val2 = int(val)
        if val2 == -1:
            return defint
        else:
            return val2

def is_ini_value_true(elem, default=False):
    val = get_ini_value(elem)
    if val != None:
        if val != 0 and val != "0":
            return True
        else:
            return False
    return default

# folders
def add_folder_if_not_exists(foldertxt, folderfind, parentifcreate, overwrite=False):
    vnext = HSNeoOCIFolder.find_single_startswith(folderfind)
    if vnext:
        if overwrite:
            vnext.name = foldertxt
        return vnext
    else:
        return folder_add_child(parentifcreate,foldertxt)

# ---- API -------

# Move to concrete Scene,Cam and isAnimated
# You can skip scene, cam, or isAnimated to move locally
def api_moveto(scene=None,cam=None,isAnimated=None): # isAnimated - None / True / False - None - SSS depends
    global _sc
    if len(_sc.block) > 0:
        if scene != None:
            if scene < len(_sc.block):
                _sc.cur_index = scene
                _sc.loadCurrentScene(False)
                _sc.prev_index = _sc.cur_index

        if cam != None:
            if len(_sc.block[_sc.cur_index].cams) > 0 and cam < (len(_sc.block[_sc.cur_index].cams)):
                _sc.cur_cam = cam
                _sc.setCamera(isAnimated)

# calculate Dictionary for cams with names
def api_getdictnames():
    global _sc
    from scenesavestate_vnssext import calcDictNames
    return calcDictNames(_sc)

# Resolve cam Name to tuple (scene(int), cam(int)), if there is such cam name
# otherwise return (-1,-1)
def api_name2scenecam(name,dict=None):
    if dict == None:
        dict = api_getdictnames()

    if name in dict.keys():
        a = int(dict[name])
        cam = a % 100
        scene = int((a - cam) / 100 - 1)
        return (scene,cam)

    return (-1,-1)