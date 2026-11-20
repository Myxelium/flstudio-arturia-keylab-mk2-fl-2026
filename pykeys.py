"""Keyboard shortcut helper for FL Studio MIDI scripts.

FL Studio 2025/2026 runs scripts in a Python subinterpreter where ctypes cannot
load DLLs (SendInput/keybd_event). Shortcut macros are therefore disabled;
transport/mixer still work via the FL API when the KeyLab speaks MCU.
"""
import sys

_ENABLED = False
_INIT_ERROR = 'disabled in FL subinterpreter (no ctypes DLL loading)'


def platform():
    if sys.platform.startswith('win'):
        return 'win'
    if sys.platform == 'darwin':
        return 'mac'
    return sys.platform


def send(key, shift=0, win=0, ctrl=0, alt=0):
    """No-op: Win32 key injection is unavailable inside FL's script host."""
    return False
