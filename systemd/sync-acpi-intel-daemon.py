#!/usr/bin/env python
# Created in 2013 by Daniel Kukula <daniel.kuku@gmail.com>
#used code from http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
#written by Sander Marechal

import pyinotify
import sys, os, time, atexit
from signal import SIGTERM 

class Daemon:
	"""
	A generic daemon class.
	
	Usage: subclass the Daemon class and override the run() method
	"""
	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
	
	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)
	
	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if pid:
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print str(err)
				sys.exit(1)

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()

	def run(self):
		"""
		You should override this method when you subclass Daemon. It will be called after the process has been
		daemonized by start() or restart().
		"""


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
  
class MyDaemon(Daemon):
	def run(self):
		while True:
			notifier.loop()
			time.sleep(1)

if __name__ == "__main__":
	daemon = MyDaemon('/var/run/sync-acpi-intel.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
