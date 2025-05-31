from ctypes import *
from ctypes.wintypes import LPSTR, HWND, UINT, INT, LPCSTR, LPDWORD, DWORD, HANDLE, BOOL, LPRECT 

'''
MessageBoxA is part of user32 DLL/Library
MessageBoxA expect 4 parameters
1- the owner of the window of the message  (HWND)
2- the message to be displayed (LPCSTR)
3- the title of the message (LPCSTR)
4- the type of the dialog box like (warning, info, etc) (UINT) 
'''
messageBoxA = windll.user32.MessageBoxA
messageBoxA.argtypes = (HWND, LPCSTR, LPCSTR, UINT)
messageBoxA.restype = INT

header = b"From Hacker!!"
message = b"Hello you have been hacked.\nEven if you press ok now just know that I can see you,\nif you want to communicate please call me +96551590222"
status = 0x00000040

# messageBoxA(None,message,header,status)


'''
GetUserNameA is part of Advapi32 DLL/Library
GetUserNameA expects 2 parameters:
1- A buffer to store the username (LPSTR)
2- A pointer to a DWORD representing the buffer size

- Windows API expects the size parameter to be a DWORD (32-bit unsigned integer)
- After the call, this DWORD contains the actual length of the username
'''

getUsernameA = windll.Advapi32.GetUserNameA
getUsernameA.argtypes = LPSTR, LPDWORD 
getUsernameA.restype = int

bfsize = DWORD(10)
buffer =  create_string_buffer(bfsize.value)
getUsernameA(buffer, byref(bfsize))

error = GetLastError()
if error:
    print(WinError(error))


'''
getWindowRect require 2 Parameters
1- A handle to the window which is a function in User32 DLL/Library
2- A pointer to a RECT. RECT is a structure defines
a rectangle by the coordinates of its upper-left and lower-right corners.

so before calling the getWindowRect API we need to define the attributes first 
'''

handler = windll.User32.GetForegroundWindow()

class RECT(Structure):
    _fields_ = [("left", c_long),("right", c_long),("top", c_long),("bottom", c_long)]

screenCords = RECT()

getWindowRect = windll.User32.GetWindowRect
getWindowRect.argtypes = HANDLE, POINTER(RECT) 
getWindowRect.restype = BOOL


getWindowRect(handler, byref(screenCords))

print(screenCords.top)
print(screenCords.right)
print(screenCords.left)
print(screenCords.bottom)


