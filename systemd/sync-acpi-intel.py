#!/usr/bin/env python
# Created in 2013 by Daniel Kukula <daniel.kuku@gmail.com>

import pyinotify 
def filerw(file, type="r", str="0"):
#reads and writes to file
#type is r or w
#str is optional only when writing
    if type == "r":
        f = open(file, "r")
        bl = f.read()
        f.close()
        return bl
    elif type == "w":
        f = open(file, "w")
        bl = f.write(str)
        f.close()
    else:
        print "error reading or writing file"
BACKLIGHT_DIR = "/sys/class/backlight"
ACPI = BACKLIGHT_DIR + "/acpi_video0"
INTEL = BACKLIGHT_DIR + "/intel_backlight"
ACPI_MAX_FILE = ACPI + "/max_brightness"
INTEL_MAX_FILE = INTEL + "/max_brightness"
ACPI_MAX = int(filerw(ACPI_MAX_FILE))
INTEL_MAX = int(filerw(INTEL_MAX_FILE))
ACPI_BR_FILE = ACPI + "/brightness"
INTEL_BR_FILE = INTEL + "/brightness"
def set_backlight(bl, file):
#INT -> FILE
#bl is the preffered brightness in numerical form  
# file of the file who controls brightness
    filerw(file, "w", str(bl))

def logarithmic_bl(bl):
#INT -> INT
#function gets linear brightness and returns logarithmic
    if bl == ACPI_MAX:
        return INTEL_MAX
    else:
        return 2 ** (bl + 1)
        
def get_acpi_level(file):
#FILE -> INT
#return current acpi brightness level
    return int(filerw(file))
        
        
wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_MODIFY  # watched events

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        bl = get_acpi_level(ACPI_BR_FILE)
        set_backlight(logarithmic_bl(bl), INTEL_BR_FILE)

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(ACPI_BR_FILE, mask, rec=True)

notifier.loop()
