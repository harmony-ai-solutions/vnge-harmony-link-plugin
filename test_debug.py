# Small helper file to test bunch of things using the runtime and Debugger

import sys
sys.path.append(r"E:\Koikatsu Party After Party\BepInEx\plugins\Console")
sys.path.append(r"E:\Koikatsu Party After Party\CharaStudio_Data\Managed")

#print sys.path

import clr
clr.AddReference('StdLib')
clr.AddReference('UnityEngine')
clr.AddReference('UnityEngine.UI')
clr.AddReference('Unity.Python.Modules')
clr.AddReference('Assembly-CSharp')
clr.AddReference('Assembly-CSharp-firstpass')
clr.AddReference('InputSimulator')
clr.AddReference('NLayer')

## ALSO SEE UNITY SCRIPTING REFERENCE (!):
# https://docs.unity3d.com/560/Documentation/ScriptReference/Application.html

import UnityEngine

from pprint import pprint


def recursiveDocumentation(object):
    data = {}
    if hasattr(object, "__dict__"):
        d = vars(object)
        for k, v in d.items():
            data[k] = recursiveDocumentation(v)
    return data


# See last answer here also: https://stackoverflow.com/questions/28947581/how-to-convert-a-dictproxy-object-into-json-serializable-dict
# -> Python vars() returns a dict, yielding proxy objects (to other dicts or whatever type), which need to be instantiated

#doc = recursiveDocumentation(UnityEngine)
pprint(vars(UnityEngine), indent=2)

apps = vars(UnityEngine.Application)
apps = dict(apps)
pprint(apps, indent=2)

exit(0)