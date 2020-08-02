from PyQt4 import QtGui, QtCore
from pybass import *
from ConfigParser import ConfigParser
from os.path import exists
from os import listdir
import ini

AOpath = "base/"
#AOpath = "I:\\aovanilla1.7.5\\client\\base\\"

class Settings(QtGui.QDialog):
	def __init__(self):
		super(Settings, self).__init__()
		self.setModal(True)
		
		self.inifile = ConfigParser()
		self.setWindowTitle("Settings")
		self.setFixedSize(400, 400)
		self.hide()
		
		main_layout = QtGui.QVBoxLayout(self)
		save_layout = QtGui.QHBoxLayout()
		
		self.tabs = QtGui.QTabWidget()
		self.tabs.resize(320-16, 480-40)
		self.tabs.move(8, 8)
		
		general_tab = QtGui.QWidget()
		audio_tab = QtGui.QWidget()
		callwords_tab = QtGui.QWidget()
		general_layout = QtGui.QVBoxLayout(general_tab)
		general_layout.setAlignment(QtCore.Qt.AlignTop)
		audio_layout = QtGui.QFormLayout(audio_tab)
		audio_layout.setLabelAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
		audio_layout.setFormAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		callwords_layout = QtGui.QVBoxLayout(callwords_tab)
		callwords_layout.setAlignment(QtCore.Qt.AlignTop)
		
		savebtn = QtGui.QPushButton()
		savebtn.setText("Save")
		savebtn.clicked.connect(self.onSaveClicked)
		cancelbtn = QtGui.QPushButton()
		cancelbtn.setText("Cancel")
		cancelbtn.clicked.connect(self.onCancelClicked)
		
		separators = []
		for i in range(4):
			separator = QtGui.QFrame()
			separator.setFixedSize(separator.size().width(), 16)
			separators.append(separator)
		
		###### General tab ######
		self.savetolog = QtGui.QCheckBox()
		self.savetolog.setText("Save chat logs to a file*")
		self.savetolog.setChecked(False)
		self.savetolog_combine = QtGui.QCheckBox()
		self.savetolog_combine.setText("Combine OOC and IC chat logs in the same file*")
		self.savetolog_combine.setChecked(False)
		
		defaultoocname_layout = QtGui.QHBoxLayout()
		defaultoocname_label = QtGui.QLabel("Default OOC name")
		self.defaultoocname = QtGui.QLineEdit()
		defaultoocname_layout.addWidget(defaultoocname_label)
		defaultoocname_layout.addWidget(self.defaultoocname)
		
		allowdownload = QtGui.QLabel()
		allowdownload.setText("Automatically download or stream online from WebAO:")
		allowdownload_layout = QtGui.QHBoxLayout()
		self.allowdownload_chars = QtGui.QCheckBox("Characters")
		self.allowdownload_sounds = QtGui.QCheckBox("Sounds")
		self.allowdownload_music = QtGui.QCheckBox("Music")
		self.allowdownload_evidence = QtGui.QCheckBox("Evidence")
		allowdownload_layout.addWidget(self.allowdownload_chars)
		allowdownload_layout.addWidget(self.allowdownload_sounds)
		allowdownload_layout.addWidget(self.allowdownload_music)
		allowdownload_layout.addWidget(self.allowdownload_evidence)

		currtheme_layout = QtGui.QHBoxLayout()
		currtheme_label = QtGui.QLabel("Current theme")
		self.currtheme = QtGui.QComboBox()
		self.themes = listdir(AOpath+"ao2xp_themes")
		for theme in self.themes:
                        if exists(AOpath+"ao2xp_themes/"+theme+"/theme.py"):
                                self.currtheme.addItem(theme)
                currtheme_layout.addWidget(currtheme_label)
                currtheme_layout.addWidget(self.currtheme)
		
		savechangeswarn = QtGui.QLabel()
		savechangeswarn.setText("* Change takes effect upon restarting the client")
		
		general_layout.addWidget(self.savetolog)
		general_layout.addWidget(self.savetolog_combine, 0, QtCore.Qt.AlignRight)
		general_layout.addWidget(separators[0])
		general_layout.addLayout(defaultoocname_layout)
		general_layout.addWidget(separators[1])
		general_layout.addWidget(allowdownload)
		general_layout.addLayout(allowdownload_layout)
		general_layout.addWidget(separators[2])
		general_layout.addLayout(currtheme_layout)
		general_layout.addWidget(savechangeswarn, 50, QtCore.Qt.AlignBottom)

		###### Audio tab ######
		device_label = QtGui.QLabel("Audio device")
		self.device_list = QtGui.QComboBox()
		audio_layout.setWidget(0, QtGui.QFormLayout.LabelRole, device_label)
		audio_layout.setWidget(0, QtGui.QFormLayout.FieldRole, self.device_list)
		audio_layout.setWidget(1, QtGui.QFormLayout.FieldRole, separators[3])

		info = BASS_DEVICEINFO()
		ind = 0
		while BASS_GetDeviceInfo(ind, info):
			self.device_list.addItem(info.name)
			ind += 1

		###### Callwords tab ######
		self.callwords_edit = QtGui.QTextEdit()
		
		callwords_wordwrap = QtGui.QCheckBox("Word Wrap")
		callwords_wordwrap.setChecked(True)
		callwords_wordwrap.stateChanged.connect(self.callwordsWordWrapCheckbox)
		
		callwords_instructions = QtGui.QLabel()
		callwords_instructions.setText("Separate callwords with newlines (ENTER key).")
		
		callwords_layout.addWidget(self.callwords_edit)
		callwords_layout.addWidget(callwords_wordwrap, 0, QtCore.Qt.AlignRight)
		callwords_layout.addWidget(callwords_instructions)
		
		self.tabs.addTab(general_tab, "General")
		self.tabs.addTab(audio_tab, "Audio")
		self.tabs.addTab(callwords_tab, "Callwords")
		
		save_layout.addWidget(savebtn, 100, QtCore.Qt.AlignRight)
		save_layout.addWidget(cancelbtn, 0, QtCore.Qt.AlignRight)
		main_layout.addWidget(self.tabs)
		main_layout.addLayout(save_layout)
	
	def showSettings(self):
		if exists(AOpath+"AO2XP.ini"):
			self.inifile.read(AOpath+"AO2XP.ini")
			self.savetolog.setChecked(ini.read_ini_bool(self.inifile, "General", "save logs"))
			self.savetolog_combine.setChecked(ini.read_ini_bool(self.inifile, "General", "combined logs"))
			try:
				self.defaultoocname.setText(ini.read_ini(self.inifile, "General", "OOC name").decode("utf-8"))
			except:
				self.defaultoocname.setText(ini.read_ini(self.inifile, "General", "OOC name"))
			self.allowdownload_chars.setChecked(ini.read_ini_bool(self.inifile, "General", "download characters"))
			self.allowdownload_sounds.setChecked(ini.read_ini_bool(self.inifile, "General", "download sounds"))
			self.allowdownload_music.setChecked(ini.read_ini_bool(self.inifile, "General", "download music"))
			self.allowdownload_evidence.setChecked(ini.read_ini_bool(self.inifile, "General", "download evidence"))
			self.currtheme.setCurrentIndex(self.themes.index(ini.read_ini(self.inifile, "General", "theme", "default")))
			self.device_list.setCurrentIndex(ini.read_ini_int(self.inifile, "Audio", "device", BASS_GetDevice()))
		else:
			self.savetolog.setChecked(False)
			self.savetolog_combine.setChecked(False)
			self.defaultoocname.setText("")
			self.allowdownload_sounds.setChecked(True)
			self.allowdownload_music.setChecked(True)
			self.allowdownload_evidence.setChecked(True)
			self.currtheme.setCurrentIndex(self.themes.index("default"))
			self.device_list.setCurrentIndex(BASS_GetDevice())
		
		self.callwords_edit.clear()
		if exists(AOpath+"callwords.ini"):
			with open(AOpath+"callwords.ini") as f:
				for line in f:
					self.callwords_edit.append(line.rstrip().decode("utf-8"))
		
		self.tabs.setCurrentIndex(0)
		self.show()
	
	def callwordsWordWrapCheckbox(self, newstate):
		if newstate:
			self.callwords_edit.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
		else:
			self.callwords_edit.setWordWrapMode(0)
	
	def onSaveClicked(self):
		if not self.inifile.has_section("General"): self.inifile.add_section("General")
		if not self.inifile.has_section("Audio"): self.inifile.add_section("Audio")
		self.inifile.set("General", "save logs", self.savetolog.isChecked())
		self.inifile.set("General", "combined logs", self.savetolog_combine.isChecked())
		self.inifile.set("General", "OOC name", self.defaultoocname.text().toUtf8())
		self.inifile.set("General", "download characters", self.allowdownload_chars.isChecked())
		self.inifile.set("General", "download sounds", self.allowdownload_sounds.isChecked())
		self.inifile.set("General", "download music", self.allowdownload_music.isChecked())
		self.inifile.set("General", "download evidence", self.allowdownload_evidence.isChecked())
		self.inifile.set("General", "theme", self.currtheme.currentText())
		self.inifile.set("Audio", "device", self.device_list.currentIndex())
		self.inifile.write(open(AOpath+"AO2XP.ini", "w"))
		
		with open(AOpath+"callwords.ini", "w") as f:
			f.write(self.callwords_edit.toPlainText().toUtf8())
		
		self.hide()
	
	def onCancelClicked(self):
		self.hide()
