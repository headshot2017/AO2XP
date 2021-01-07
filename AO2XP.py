import sys, thread, time, os, platform
from os.path import exists
from PyQt4 import QtGui, QtCore
app = QtGui.QApplication(sys.argv)

osname = platform.system()
bassdll = "bass.dll"
if osname != "Windows":
    bassdll = "libbass.so"

debugmode = len(sys.argv) > 1 and sys.argv[1] == "debug"
if not debugmode:
    fakebass = len(sys.argv) > 1 and sys.argv[1] == "bass"
    if not exists(bassdll) or fakebass:
        QtGui.QMessageBox.critical(None, "Unable to launch game", "Couldn't find the file %s on the client folder.\nAO2XP needs this file in order to play sounds and music.\nThe file is included in the client's zip file, make sure it's in the same folder as the AO2XP exe." % bassdll)
        os._exit(-2)

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
    force_downloader = len(sys.argv) > 1 and sys.argv[1] == "download"
    if force_downloader or (not exists("base/background") and not exists("base/characters") and not exists("base/sounds") and not exists("base/evidence")):
        jm = QtGui.QMessageBox.information(None, "Warning", "You seem to be missing the included Attorney Online content.\nWould you like to download them automatically?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if jm == QtGui.QMessageBox.Yes:
            import basedownloader
            code = basedownloader.downloadVanilla()
            if code != 0: os._exit(code)
        else:
            os._exit(-3)

from pybass import *
import gameview, mainmenu, options, ini

BASS_Init(ini.read_ini_int("base/AO2XP.ini", "Audio", "device", -1), 44100, 0, 0, 0)
BASS_PluginLoad("bassopus", 0)
shit = gamewindow()
shit.show()
sys.exit(app.exec_())
