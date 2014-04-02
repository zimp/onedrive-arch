#!/usr/bin/python

import os, sys, yaml, subprocess, platform

# Prepare global variables

APP_CLIENT_ID = "000000004010C916"
APP_SECRET = "PimIrUibJfsKsMcd0SqwPBwMTV7NDgYi"

HOME_PATH = os.path.expanduser("~")
OS_USER = os.getenv("SUDO_USER")
if OS_USER == None or OS_USER == "":
	# the user isn't running sudo
	OS_USER = os.getenv("USER")
else:
	# when in SUDO, fix the HOME_PATH
	# may not be necessary on most OSes
	HOME_PATH = os.path.split(HOME_PATH)[0] + "/" + OS_USER

OS_NAME = platform.system() + " " + platform.release()
OS_DIST =  platform.linux_distribution(supported_dists=('debian', 'ubuntu'), full_distribution_name=1)

APTITUDE_PKG_DEPENDENCIES = ["dpkg", "git", "python-pip", "libyaml-dev", "python-yaml", "python-dateutil", "inotify-tools"]
PIP_PKG_DEPENDENCIES = ["urllib3", "requests"]

def queryUser(question, answer = "y"):
	valid = {"y": True, "ye": True, "yes": True,
			 "n": False, "no": False}
	if answer == "y":
		prompt = " [Y/n] "
	elif answer == "n":
		prompt = " [y/N] "
	else:
		prompt = " [y/n] "
	
	sys.stdout.write(question + prompt)
	while True:
		response = raw_input().lower()
		if answer is not None and response == "":
			return answer
		elif response in valid.keys():
			return valid[response]
		else:
			sys.stdout.write("Please respond with 'y' (yes) or 'n' (no).\n")

def mkdirIfMissing(path):
	try:
		if not os.path.exists(path):
			os.mkdir(path, 0700)
			print "Created directory \"" + path + "\"."
		return True
	except OSError:
		print "OSError({0}): {1}".format(e.errno, e.strerror)
		return False

def setupDaemon():
	rootPath = ""
	
	print "Setting up OneDrive-d..."
	# write down app information
	f = open(HOME_PATH + "/.lcrc", "w")
	f.write("client:\n  id: " + APP_CLIENT_ID + "\n  secret: " + APP_SECRET + "\n")
	f.close()
	
	assert mkdirIfMissing(HOME_PATH + "/.onedrive"), "Failed to create the configuration path."
	
	if not os.path.exists(HOME_PATH + "/.onedrive/user.conf") or os.path.exists(HOME_PATH + "/.onedrive/user.conf") and queryUser("The configuration file already exists.\nOverwrite?", None):
		while True:
			sys.stdout.write("Please specify the directory to sync with OneDrive (default: " + HOME_PATH + "/OneDrive):\n")
			response = raw_input().strip()
			if mkdirIfMissing(response):
				f = open(HOME_PATH + "/.onedrive/user.conf", "w")
				rootPath = os.path.abspath(response)
				f.write("rootPath: " + rootPath + "\n")
				f.close()
				break
			else:
				sys.stdout.write("Failed to create the directory \"" + response + "\". Please specify another one.\n")
	else:
		sys.stdout.write("Keep current configuration.\n")
		f = open(HOME_PATH + "/.onedrive/user.conf", "r")
		currentConf = yaml.safe_load(f)
		f.close()
		rootPath = currentConf["rootPath"]
	
	print rootPath
	#open(HOME_PATH + "", "r")

def installPackages():
	if queryUser("Do you want to run apt-get update && apt-get upgrade?", "y"):
		subprocess.Popen(["sudo", "apt-get", "update"]).communicate()
		subprocess.Popen(["sudo", "apt-get", "upgrade"]).communicate()
		print "System package list has been updated successfully."
	
	print "Now install pre-requisite system packages..."
	subp = subprocess.Popen(["sudo", "apt-get", "-y", "install"] + APTITUDE_PKG_DEPENDENCIES)
	subp.communicate()
	assert subp.returncode == 0
	
	print "Now install the required PIP packages..."
	for p in PIP_PKG_DEPENDENCIES:
		subprocess.Popen(["sudo", "pip", "install", p, "--upgrade"]).communicate()
	
	print "Now install python-skydrive package..."
	subprocess.Popen(["sudo", "pip", "install", "git+https://github.com/mk-fg/python-skydrive.git#egg=python-skydrive[standalone]", "--upgrade"]).communicate()

def authDaemon():
	print "Authenticating..."

def parseArguments():
	if len(sys.argv) < 2:
		print "Usage: onedrive-util [pre|setup|auth|all]"
		sys.exit(1)
	argv = sys.argv
	if argv[1] == "setup":
		setupDaemon()
	elif argv[1] == "pre":
		installPackages()
	elif argv[1] == "auth":
		authDaemon()
	elif argv[1] == "all":
		installPackages()
		setupDaemon()
		authDaemon()
	
if __name__ == "__main__":
	parseArguments()
