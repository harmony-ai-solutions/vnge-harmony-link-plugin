# Small helper file to test bunch of things using the runtime and Debugger

import sys
sys.path.append(r"E:\Koikatsu Party After Party\BepInEx\plugins\Console")
sys.path.append(r"E:\Koikatsu Party After Party\CharaStudio_Data\Managed")

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



# Simple Web / API Requests:
# https://discourse.pyrevitlabs.io/t/using-requests-module-with-ironpython/541/7
# https://learn.microsoft.com/de-de/dotnet/api/system.net.webclient?view=net-5.0
#
# from System.Net import WebClient
# client = WebClient()
# client.Headers.Add("Accept", "application/json")
# client.Headers.Add("Content-Type", "application/json")
#
# response = client.UploadString("simple", "POST", "data")
#
# resp = client.ResponseHeaders
#
# pprint(response)
# pprint(resp)
#
# exit(0)

# On GraphQL:
# (Not too helpful) https://community.tibco.com/s/question/0D54z00007mxYpvCAE/connecting-to-graphql-with-ironpython-using-mutation-and-post-request
# https://github.com/the-orb/orb.net

# On WebSockets:
# https://github.com/gtalarico/ironpython-stubs/blob/master/release/stubs/System/Net/WebSockets.py
# https://learn.microsoft.com/de-de/dotnet/api/system.net.websockets?view=net-5.0


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