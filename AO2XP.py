import sys, thread, time, ctypes
from os.path import exists

debugmode = len(sys.argv) > 1 and sys.argv[1] == "debug"
if not debugmode:
	if not exists("bass.dll"):
		ctypes.windll.user32.MessageBoxA(0, "couldn't find the file 'bass.dll' on the client folder.\nthis program needs this file in order to play sounds and music.\nthe file is included in this client's zip file, make sure it's in the same folder as the AO2XP.exe", "unable to launch game", 0)
		sys.exit(1)

from PyQt4 import QtGui, QtCore
from pybass import *
import gameview, mainmenu, options, ini

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
		self.stackwidget.setCurrentWidget(self.gamewidget)
	
	def returnToMenu(self):
		self.gamewidget.disconnectnow = True
		self.setFixedSize(self.widget.lobbyimg.size().width(), self.widget.lobbyimg.size().height())
		self.widget.onClicked_cancelconnect()
		self.stackwidget.setCurrentWidget(self.widget)
		self.setWindowTitle("AO2XP")
	
	def showSettings(self):
		self.settingsgui.showSettings()

if not debugmode:
	if not exists("base"):
		ctypes.windll.user32.MessageBoxA(0, "The 'base' folder appears to be missing.\nDownload the original Attorney Online client below,\nthen extract the 'base' folder from the zip to the AO2XP folder.\n\nhttp://aceattorneyonline.com", "unable to launch game", 0)
		sys.exit(1)

BASS_Init(ini.read_ini_int("base/AO2XP.ini", "Audio", "device", -1), 44100, 0, 0, 0)
BASS_PluginLoad("bassopus", 0)
app = QtGui.QApplication(sys.argv)
shit = gamewindow()
shit.show()
sys.exit(app.exec_())
