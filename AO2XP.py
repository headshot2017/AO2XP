from PyQt4 import QtGui, QtCore
from pybass import *
import sys, thread, time
from os.path import exists
import ctypes

import gameview, mainmenu, options

class gamewindow(QtGui.QMainWindow):
	def __init__(self):
		super(gamewindow, self).__init__()
		self.stackwidget = QtGui.QStackedWidget(self)
		self.widget = mainmenu.lobby(self)
		self.gamewidget = gameview.gui(self)
		self.stackwidget.addWidget(self.widget)
		self.stackwidget.addWidget(self.gamewidget)
		self.setCentralWidget(self.stackwidget)
		self.stackwidget.setCurrentWidget(self.widget)
		self.setFixedSize(self.widget.lobbyimg.size().width(), self.widget.lobbyimg.size().height())
		self.center()
		self.setWindowTitle("AO2XP")
		self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
		
		self.settingsgui = options.Settings()
	
	def center(self):
		frameGm = self.frameGeometry()
		centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())
	
	def showGame(self, tcp, charlist, musiclist, background, evidence, areas, features=[], oocjoin=[], hplist=[]):
		self.gamewidget.disconnectnow = False
		self.gamewidget.startGame(tcp, charlist, musiclist, background, evidence, areas, features, oocjoin, hplist)
		self.setFixedSize(714, 668)
		self.stackwidget.setCurrentWidget(self.gamewidget)
	
	def returnToMenu(self):
		self.gamewidget.disconnectnow = True
		self.setFixedSize(self.widget.lobbyimg.size().width(), self.widget.lobbyimg.size().height())
		self.widget.onClicked_cancelconnect()
		self.stackwidget.setCurrentWidget(self.widget)
		self.setWindowTitle("AO2XP")
	
	def showSettings(self):
		self.settingsgui.showSettings()

debugmode = False
if len(sys.argv) > 1:
	if sys.argv[1] == "debug":
		debugmode = True

if not debugmode:
	if not exists("base"):
		ctypes.windll.user32.MessageBoxA(0, "i couldn't find the holy mother of all important folders that goes by the name of 'base'.\nto fix this, you can try:\n1. downloading a full vanilla copy of Attorney Online 2, and copy the 'base' folder over to this client's location\n2. making sure you extracted the client in the right location", "unable to launch game", 0)
		sys.exit(1)
	elif not exists("bass.dll"):
		ctypes.windll.user32.MessageBoxA(0, "i couldn't find the file 'bass.dll'\nthis program needs this file in order to play sounds and music\nthe file is included in this client's zip file, make sure it's in the same folder as this EXE", "unable to launch game", 0)
		sys.exit(1)

BASS_Init(-1, 44100, 0, 0, 0)
app = QtGui.QApplication(sys.argv)
shit = gamewindow()
shit.show()
sys.exit(app.exec_())