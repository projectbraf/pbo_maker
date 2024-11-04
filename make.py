import sys
if sys.version_info[0] == 2:
    print("Python 3 is required.")
    sys.exit(1)
import os
import os.path
import pathlib
import shutil
import platform
import glob
import subprocess
import hashlib
import configparser
import json
import traceback
import time
import timeit
import re
from tempfile import mkstemp
if sys.platform == "win32":
    import winreg

###############################################################################
# http://akiscode.com/articles/sha-1directoryhash.shtml
# Copyright (c) 2009 Stephen Akiki
# MIT License (Means you can do whatever you want with this)
#  See http://www.opensource.org/licenses/mit-license.php
# Error Codes:
#   -1 -> Directory does not exist
#   -2 -> General error (see stack traceback)
def  get_directory_hash(directory):
    directory_hash = hashlib.sha1()
    if not os.path.exists (directory):
        return -1

    try:
        for root, dirs, files in os.walk(directory):
            for names in files:
                path = os.path.join(root, names)
                try:
                    f = open(path, 'rb')
                except:
                    # You can't open the file for some reason
                    f.close()
                    continue

                while 1:
                    # Read file in as little chunks
                    buf = f.read(4096)
                    if not buf: break
                    new = hashlib.sha1(buf)
                    directory_hash.update(new.digest())
                f.close()

    except:
        # Print the stack traceback
        traceback.print_exc()
        return -2

    retVal = directory_hash.hexdigest()
    #print_yellow("Hash Value for {} is {}".format(directory,retVal))
    return directory_hash.hexdigest()

def Fract_Sec(s):
    temp = float()
    temp = float(s) / (60*60*24)
    d = int(temp)
    temp = (temp - d) * 24
    h = int(temp)
    temp = (temp - h) * 60
    m = int(temp)
    temp = (temp - m) * 60
    sec = temp
    return d,h,m,sec
    #endef Fract_Sec

# Copyright (c) André Burgaud
# http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
if sys.platform == "win32":
    from ctypes import windll, Structure, c_short, c_ushort, byref

    SHORT = c_short
    WORD = c_ushort

    class COORD(Structure):
      """struct in wincon.h."""
      _fields_ = [
        ("X", SHORT),
        ("Y", SHORT)]

    class SMALL_RECT(Structure):
      """struct in wincon.h."""
      _fields_ = [
        ("Left", SHORT),
        ("Top", SHORT),
        ("Right", SHORT),
        ("Bottom", SHORT)]

    class CONSOLE_SCREEN_BUFFER_INFO(Structure):
      """struct in wincon.h."""
      _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", WORD),
        ("srWindow", SMALL_RECT),
        ("dwMaximumWindowSize", COORD)]

    # winbase.h
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    # wincon.h
    FOREGROUND_BLACK     = 0x0000
    FOREGROUND_BLUE      = 0x0001
    FOREGROUND_GREEN     = 0x0002
    FOREGROUND_CYAN      = 0x0003
    FOREGROUND_RED       = 0x0004
    FOREGROUND_MAGENTA   = 0x0005
    FOREGROUND_YELLOW    = 0x0006
    FOREGROUND_GREY      = 0x0007
    FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

    BACKGROUND_BLACK     = 0x0000
    BACKGROUND_BLUE      = 0x0010
    BACKGROUND_GREEN     = 0x0020
    BACKGROUND_CYAN      = 0x0030
    BACKGROUND_RED       = 0x0040
    BACKGROUND_MAGENTA   = 0x0050
    BACKGROUND_YELLOW    = 0x0060
    BACKGROUND_GREY      = 0x0070
    BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

    stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

    def get_text_attr():
      """Returns the character attributes (colors) of the console screen
      buffer."""
      csbi = CONSOLE_SCREEN_BUFFER_INFO()
      GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
      return csbi.wAttributes

    def set_text_attr(color):
      """Sets the character attributes (colors) of the console screen
      buffer. Color is a combination of foreground and background color,
      foreground and background intensity."""
      SetConsoleTextAttribute(stdout_handle, color)
###############################################################################

def find_bi_tools(work_drive):
    """Find BI tools."""

    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    try:
        k = winreg.OpenKey(reg, r"Software\bohemia interactive\arma 3 tools")
        arma3tools_path = winreg.QueryValueEx(k, "path")[0]
        winreg.CloseKey(k)
    except:
        raise Exception("BadTools","Arma 3 Tools are not installed correctly or the P: drive needs to be created.")

    addonbuilder_path = os.path.join(arma3tools_path, "AddonBuilder", "AddonBuilder.exe")
    dssignfile_path = os.path.join(arma3tools_path, "DSSignFile", "DSSignFile.exe")
    dscreatekey_path = os.path.join(arma3tools_path, "DSSignFile", "DSCreateKey.exe")
    cfgconvert_path = os.path.join(arma3tools_path, "CfgConvert", "CfgConvert.exe")

    if os.path.isfile(addonbuilder_path) and os.path.isfile(dssignfile_path) and os.path.isfile(dscreatekey_path) and os.path.isfile(cfgconvert_path):
        return [addonbuilder_path, dssignfile_path, dscreatekey_path, cfgconvert_path]
    else:
        raise Exception("BadTools","Arma 3 Tools are not installed correctly or the P: drive needs to be created.")

def mikero_windows_registry(path, access=winreg.KEY_READ):
    try:
        return winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Mikero\{}".format(path), access=access)
    except FileNotFoundError:
        try:
            return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Mikero\{}".format(path), access=access)
        except FileNotFoundError:
            try:
                return winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Wow6432Node\Mikero\{}".format(path), access=access)
            except FileNotFoundError:
                return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Mikero\{}".format(path), access=access)

def find_depbo_tools():
    """Use registry entries to find DePBO-based tools."""
    # try running pboProject once if it's not in registry
    try:
        pboProject = mikero_windows_registry("pboProject")
        print(f"pboProject found normally via registry")
    except:
        print(f"pboProject not in registry")
        pboProject = shutil.which('pboProject')
        if (pboProject is None):
            print("pboProject not in sys path")
        else:
            print(f"pboProject startup")
            ret = subprocess.call([pboProject, "-P"])

    requiredToolPaths = {"pboProject": None, "rapify": None, "MakePbo": None}
    failed = False

    for tool in requiredToolPaths:
        try:
            k = mikero_windows_registry(tool)
            path = winreg.QueryValueEx(k, "exe")[0]
        except FileNotFoundError:
            print_error("Could not find {}".format(tool))
            failed = True
        else:
            #Strip any quotations from the path due to a MikeRo tool bug which leaves a trailing space in some of its registry paths.
            requiredToolPaths[tool] = path.strip('"')
            print_green("Found {}.".format(tool))
        finally:
            winreg.CloseKey(k)

    if failed:
        raise Exception("BadDePBO", "DePBO tools not installed correctly")

    return requiredToolPaths


def pboproject_settings():
    """Use registry entries to configure needed pboproject settings."""
    value_exclude = "thumbs.db,*.txt,*.h,*.dep,*.cpp,*.bak,*.png,*.log,*.pew,source,*.tga"

    try:
        pbok = mikero_windows_registry(r"pboProject")
        try:
            k = winreg.OpenKey(pbok, "Settings", access=winreg.KEY_SET_VALUE)
        except:
            print_yellow("WARNING: creating pboProject/Settings reg manually")
            print_yellow("This should have happened before running make.py")
            k = winreg.CreateKeyEx(pbok, "Settings", access=winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "m_exclude", 0, winreg.REG_SZ, value_exclude)
        winreg.SetValueEx(k, "m_exclude2", 0, winreg.REG_SZ, value_exclude)
        winreg.SetValueEx(k, "wildcard_exclude_from_pbo_normal", 0, winreg.REG_SZ, value_exclude)
        winreg.SetValueEx(k, "wildcard_exclude_from_pbo_unbinarised_missions", 0, winreg.REG_SZ, value_exclude)
    except:
        raise Exception("BadDePBO", "pboProject not installed correctly, make sure to run it at least once")
    finally:
        winreg.CloseKey(k)
        winreg.CloseKey(pbok)

def color(color):
    """Set the color. Works on Win32 and normal terminals."""
    if sys.platform == "win32":
        if color == "green":
            set_text_attr(FOREGROUND_GREEN | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
        elif color == "yellow":
            set_text_attr(FOREGROUND_YELLOW | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
        elif color == "red":
            set_text_attr(FOREGROUND_RED | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
        elif color == "blue":
            set_text_attr(FOREGROUND_BLUE | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
        elif color == "reset":
            set_text_attr(FOREGROUND_GREY | get_text_attr() & 0x0070)
        elif color == "grey":
            set_text_attr(FOREGROUND_GREY | get_text_attr() & 0x0070)
    else :
        if color == "green":
            sys.stdout.write('\033[92m')
        elif color == "red":
            sys.stdout.write('\033[91m')
        elif color == "blue":
            sys.stdout.write('\033[94m')
        elif color == "reset":
            sys.stdout.write('\033[0m')

def print_error(msg):
    color("red")
    print("ERROR: {}".format(msg))
    color("reset")
    global printedErrors
    printedErrors += 1

def print_green(msg):
    color("green")
    print(msg)
    color("reset")

def print_blue(msg):
    color("blue")
    print(msg)
    color("reset")

def print_yellow(msg):
    color("yellow")
    print(msg)
    color("reset")

## CHECK IF THE PROVIDED PRIVATE KEY PATH EXISTS ##
def check_private_key(private_key_path):
    if not os.path.exists(private_key_path):
        print_error("Private key not found at {}".format(private_key_path))

## get private_jkey variable
private_key = sys.argv[3]
private_key_path = os.path.expanduser("~") + "/" + private_key
print ("Private key: {}".format(private_key))
print ("Private key path: {}".format(private_key_path))