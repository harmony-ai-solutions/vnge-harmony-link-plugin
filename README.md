# Koikatsu-Kaji-Plugin

This project aims at integrating Kajis from Kajiwoto into Koikatsu, by interfacing between actions in the game
and the actual conversation between an user and their Kaji.

This is a prototyping project which is intended to perform as a tech demonstrator for a larger scale project, which aims
towards realizing realtime interaction and conversation between AI entities and other AI or Human controlled entities in a virtual
environment.   

Success of the prototype and the overall outcome will decide whether this prototype will be developed further and
expanded with additional features.

##### Random notes on this Project for development:

- Severe issues have been obseved when using IronPython 2.7.7 or 2.7.7rc2 under Win 10 for development. 
For best compatibility and debugging capabilities, we use IronPython 2.7.8 for now.
- PyCharm using a version > 2020.1 is not capable to use pydevd (Debugger) on IronPython anymore. 
Fallback to 2019.3. See YouTrack: https://youtrack.jetbrains.com/issue/PY-45714
- Not necessarily needed, `ironpython-stubs` can be used to allow for better insight into linked modules.
https://github.com/gtalarico/ironpython-stubs
- Unity Scripting Reference (For Version 5.6.x): https://docs.unity3d.com/560/Documentation/ScriptReference/Application.html
- WebClient Module in DotNet (And other Modules there, too): https://learn.microsoft.com/de-de/dotnet/api/system.net.webclient?view=net-5.0

##### Trivia

- Countd360 - When You Report A Bug... (Patreon): https://kemono.party/patreon/user/43806151/post/59540118 