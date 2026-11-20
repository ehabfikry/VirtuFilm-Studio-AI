Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

appDir = "C:\Users\DELL\Desktop\Cindy-AI-Director"
objShell.CurrentDirectory = appDir

' Check if port 8765 is already responding; if not, start cindy_server.py silently
Function IsServerUp()
    On Error Resume Next
    Dim http
    Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    http.setTimeouts 400, 400, 400, 400
    http.Open "GET", "http://127.0.0.1:8765", False
    http.Send
    IsServerUp = (Err.Number = 0 And http.Status >= 200 And http.Status < 500)
    On Error GoTo 0
End Function

If Not IsServerUp() Then
    objShell.Run "python """ & appDir & "\cindy_server.py""", 0, False
    Dim i
    For i = 1 To 20
        WScript.Sleep 400
        If IsServerUp() Then Exit For
    Next
End If

' Open in Chrome App Mode (clean standalone window, no address bar) if Chrome exists
chrome1 = "C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome2 = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
edge1 = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

If objFSO.FileExists(chrome1) Then
    objShell.Run """" & chrome1 & """ --app=http://127.0.0.1:8765 --start-maximized", 1, False
ElseIf objFSO.FileExists(chrome2) Then
    objShell.Run """" & chrome2 & """ --app=http://127.0.0.1:8765 --start-maximized", 1, False
ElseIf objFSO.FileExists(edge1) Then
    objShell.Run """" & edge1 & """ --app=http://127.0.0.1:8765 --start-maximized", 1, False
Else
    objShell.Run "http://127.0.0.1:8765", 1, False
End If
