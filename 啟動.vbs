' launch the server launcher with no console flash
Set sh = CreateObject("WScript.Shell")
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.Run "pythonw """ & scriptDir & "\server_launcher.py""", 1, False
