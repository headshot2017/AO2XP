# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
import socket, thread, time, random, traceback, hardware
from os.path import exists

AOpath = "base/"
AO2XPpath = "AO2XPbase/"
#AOpath = "I:/aovanilla1.7.5/client/base/"

def decode_ao_str(text):
	return text.replace("<percent>", "%").replace("<pound>", "#").replace("<num>", "#").replace("<and>", "&").replace("<dollar>", "$")
def encode_ao_str(text):
	return text.replace("%", "<percent>").replace("#", "<pound>").replace("&", "<and>").replace("$", "<dollar>")

class PicButton(QtGui.QAbstractButton):
	def __init__(self, pixmap, parent=None):
		super(PicButton, self).__init__(parent)
		self.pixmap = pixmap

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.drawPixmap(event.rect(), self.pixmap)

	def sizeHint(self):
		return self.pixmap.size()
	
	def setPixmap(self, pixmap):
		self.pixmap = pixmap

class lobby(QtGui.QWidget):
	gamewindow = None
	tab = 0

	def __init__(self, parent=None):
		super(lobby, self).__init__(parent)
		self.can_connect = False
		self.svclicked = None
		self.gamewindow = parent
		self.pix_lobby = QtGui.QPixmap(AO2XPpath+'themes/default/lobbybackground.png')
		self.pix_btn_public = QtGui.QPixmap(AO2XPpath+'themes/default/publicservers.png')
		self.pix_btn_favs = QtGui.QPixmap(AO2XPpath+'themes/default/favorites.png')
		self.pix_btn_refresh = QtGui.QPixmap(AO2XPpath+'themes/default/refresh.png')
		self.pix_btn_addfav = QtGui.QPixmap(AO2XPpath+'themes/default/addtofav.png')
		self.pix_btn_connect = QtGui.QPixmap(AO2XPpath+'themes/default/connect.png')
		self.pix_connecting = QtGui.QPixmap(AO2XPpath+'themes/default/loadingbackground.png')
		
		if exists(AOpath+'serverlist.txt'):
			with open(AOpath+'serverlist.txt') as file:
				self.favoriteslist = [line.rstrip().split(':') for line in file]
		else:
			self.favoriteslist = ['127.0.0.1:27017:your server (port 27017)'.split(':'), '127.0.0.1:27016:your server (port 27016)'.split(':'),]
			
		self.lobbyimg = QtGui.QLabel(self)
		self.lobbyimg.setPixmap(self.pix_lobby)
		self.lobbyimg.show()
		
		self.connectingimg = QtGui.QLabel(self)
		self.connectingimg.setPixmap(self.pix_connecting)
		self.connectingimg.hide()
		
		self.clientver = QtGui.QLabel(self)
		self.clientver.setText('AO2XP 1.5 by Headshot')
		self.clientver.resize(self.clientver.sizeHint())
		self.clientver.move(self.pix_lobby.size().width() - self.clientver.size().width(), 0)
	
		self.settingsbtn = QtGui.QPushButton(self)
		self.settingsbtn.setText("Settings")
		self.settingsbtn.resize(self.settingsbtn.sizeHint())
		self.settingsbtn.move(self.clientver.x() - self.settingsbtn.size().width() - 8, 0)
		self.settingsbtn.clicked.connect(self.onSettingsClicked)
		
		self.btn_public = PicButton(self.pix_btn_public, self)
		self.btn_public.resize(self.btn_public.sizeHint())
		self.btn_public.move(46, 88)
		self.btn_public.clicked.connect(self.onClicked_public)
		
		self.btn_favs = PicButton(self.pix_btn_favs, self)
		self.btn_favs.resize(self.btn_favs.sizeHint())
		self.btn_favs.move(164, 88)
		self.btn_favs.clicked.connect(self.onClicked_favs)
		
		self.btn_refresh = PicButton(self.pix_btn_refresh, self)
		self.btn_refresh.resize(self.btn_refresh.sizeHint())
		self.btn_refresh.move(56, 381)
		self.btn_refresh.clicked.connect(self.onClicked_refresh)
		
		self.btn_addfav = PicButton(self.pix_btn_addfav, self)
		self.btn_addfav.resize(self.btn_addfav.sizeHint())
		self.btn_addfav.move(194, 381)
		self.btn_addfav.clicked.connect(self.onClicked_addfav)
		
		self.btn_connect = PicButton(self.pix_btn_connect, self)
		self.btn_connect.resize(self.btn_connect.sizeHint())
		self.btn_connect.move(332, 381)
		self.btn_connect.clicked.connect(self.onClicked_connect)
		
		self.serverlist = QtGui.QListWidget(self)
		self.serverlist.resize(286, 240)
		self.serverlist.move(20, 125)
		p = self.serverlist.viewport().palette()
		p.setColor(self.serverlist.viewport().backgroundRole(), QtGui.QColor(114,114,114))
		self.serverlist.viewport().setPalette(p)
		self.serverlist.itemClicked.connect(self.onClicked_serverlist)
		
		self.onlineplayers = QtGui.QLabel(self)
		self.onlineplayers.setStyleSheet('color: white')
		self.onlineplayers.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
		self.onlineplayers.setText(random.choice(['hi', 'oh, welcome back', 'hello', 'click on a server to begin', 'yo, how you doing?']))
		self.onlineplayers.move(336, 91)
		self.onlineplayers.resize(173, 16)
		
		self.serverinfo = QtGui.QTextEdit(self)
		self.serverinfo.setReadOnly(True)
		p = self.serverinfo.viewport().palette()
		p.setColor(self.serverinfo.viewport().backgroundRole(), QtGui.QColor(0,0,0))
		self.serverinfo.viewport().setPalette(p)
		self.serverinfo.setTextColor(QtGui.QColor("white"))
		self.serverinfo.move(337, 109)
		self.serverinfo.resize(173, 245)
		
		self.connectcancel = QtGui.QPushButton(self)
		self.connectcancel.setText('Cancel')
		self.connectcancel.resize(80, 20)
		self.connectcancel.move(220, 220)
		self.connectcancel.clicked.connect(self.onClicked_cancelconnect)
		self.connectcancel.hide()
		
		self.actual_serverlist = []
		
		self.lobbychatlog = QtGui.QTextEdit(self)
		self.lobbychatlog.setReadOnly(True)
		self.lobbychatlog.setGeometry(2, 445, 513, 198)
		p = self.lobbychatlog.viewport().palette()
		p.setColor(self.lobbychatlog.viewport().backgroundRole(), QtGui.QColor(139,139,139))
		self.lobbychatlog.viewport().setPalette(p)
		self.lobbychatlog.textChanged.connect(self.lobbychatlog_update)
		
		self.whitecolor = QtGui.QColor(255, 255, 255)
		
		self.font = QtGui.QFont()
		self.font.setFamily(QtCore.QString.fromUtf8('Arial'))
		self.font.setBold(True)
		self.font.setPointSize(14)
		
		self.connectprogress = QtGui.QLabel(self)
		self.connectprogress.hide()
		self.connectprogress.setStyleSheet('color: rgb(255, 128, 0);')
		self.connectprogress.setFont(self.font)
		self.connectprogress.setText('Connecting...')
		self.connectprogress.resize(300, 95)
		self.connectprogress.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
		self.connectprogress.move(135-20, 92)
		
		self.oocname = 'Name'
		self.oocnameinput = QtGui.QLineEdit(self)
		self.oocnameinput.setText(self.oocname)
		self.oocnameinput.move(0, 646)
		self.oocnameinput.resize(91, 19)
		self.oocnameinput.setStyleSheet('background-color: rgb(87, 87, 87);')
		self.oocnameinput.textChanged.connect(self.setoocname)
		
		self.lobbychatinput = QtGui.QLineEdit(self)
		self.lobbychatinput.setPlaceholderText("Say something...")
		self.lobbychatinput.move(90, 646)
		self.lobbychatinput.resize(427, 19)
		self.lobbychatinput.setStyleSheet('background-color: rgb(87, 87, 87);')
		self.lobbychatinput.returnPressed.connect(self.lobby_sendchat)

		self.aoserverinfo = AOServerInfo()
		self.aoserverinfo.moveToGameSignal.connect(self.moveToGame)
		self.aoserverinfo.msgbox_signal.connect(self.showMessageBox)
		self.aoserverinfo.setOnlinePlayers.connect(self.onlineplayers.setText)
		self.aoserverinfo.returnToLobby.connect(self.onClicked_cancelconnect)
		self.aoserverinfo.setConnectProgress.connect(self.connectprogress.setText)
		self.aoserverinfo.readySoon.connect(self.connectcancel.hide)
		self.aoserverinfo.setWindowTitle.connect(self.gamewindow.setWindowTitle)
		self.aoserverinfo.canConnect.connect(self.canConnect)

		self.masterserver = MasterServer()
		self.masterserver.gotServers.connect(self.onGetServers)
		self.masterserver.gotOOCMsg.connect(self.newOOCMessage)
		self.masterserver.msgbox_signal.connect(self.showMessageBox)
		self.masterserver.start()

	def canConnect(self):
		self.can_connect = True

	def onGetServers(self, servers):
		if self.tab == 0: self.serverlist.clear()
		self.actual_serverlist = []
		del servers[0]
		del servers[-1]
		for svcontent in servers:
			server = svcontent.split('&')
			del server[-1]
			name = server[0].decode('utf-8')
			desc = server[1].decode('utf-8')
			if len(server) <= 2:
				ip = '0.0.0.0'
				port = 0
			elif len(server) == 3:
				ip = server[2]
				port = 27017
			elif len(server) == 4:
				ip = server[2]
				port = int(server[3])
			serveritem = QtGui.QListWidgetItem(name)
			if self.tab == 0: self.serverlist.addItem(serveritem)
			self.actual_serverlist.append((ip, port, name, desc))

	def moveToGame(self, stuff):
		tcp, charlist, musiclist, background, evidence, areas, features, joinooc, hplist = stuff
		self.move_to_game(tcp, charlist, musiclist, background, evidence, areas, features, joinooc, hplist)
    
	def onSettingsClicked(self):
		self.gamewindow.showSettings()
	
	def showMessageBox(self, type, title, message):
		if type == 0: #critical
			return QtGui.QMessageBox.critical(self, title, message)
		elif type == 1: #information
			return QtGui.QMessageBox.information(self, title, message)
		elif type == 2: #question
			return QtGui.QMessageBox.question(self, title, message)
		elif type == 3: #warning
			return QtGui.QMessageBox.warning(self, title, message)

	def onClicked_public(self):
		self.tab = 0
		self.serverlist.clear()
		for sv in self.actual_serverlist:
			self.serverlist.addItem(QtGui.QListWidgetItem(sv[2]))

	def onClicked_favs(self):
		self.tab = 1
		self.serverlist.clear()
		self.serverinfo.setText("")
		for sv in self.favoriteslist:
			self.serverlist.addItem(QtGui.QListWidgetItem(sv[2]))

	def onClicked_refresh(self):
		self.serverlist.clear()
		if self.tab == 0:
			try:
				self.ms_tcp.send('ALL#%')
			except:
				self.lobbychatlog.append('failed to refresh server list')

		elif self.tab == 1:
			if exists(AOpath+'serverlist.txt'):
				with open(AOpath+'serverlist.txt') as file:
					self.favoriteslist = [ line.rstrip().split(':') for line in file ]
			else:
				self.favoriteslist = ['127.0.0.1:27017:your server (port 27017)'.split(':'), '0.0.0.0:27017:serverlist.txt not found on base folder'.split(':')]

	def onClicked_addfav(self):
		if self.tab == 1 or not self.svclicked:
			if self.tab == 1:
				QtGui.QMessageBox.information(self, "???", "Wait. That's illegal.")
			return
		
		for i in range(self.serverlist.count()):
			if self.serverlist.item(i) == self.svclicked:
				ip = self.actual_serverlist[i][0]
				port = str(self.actual_serverlist[i][1])
				name = self.actual_serverlist[i][2]

		for sv in self.favoriteslist:
			if sv[0] == ip and sv[1] == port:
				return QtGui.QMessageBox.information(self, "Error", "This server already exists in your favorites list, named '%s'" % sv[2])
		
		self.favoriteslist.append([ip, port, name])
		with open(AOpath+'serverlist.txt', "a") as file:
			file.write("%s:%s:%s\n" % (ip, port, name))
			file.close()

	def onClicked_connect(self):
		if not self.can_connect:
			return
		self.connectprogress.setText('Connecting...')
		self.connectingimg.show()
		self.connectcancel.show()
		self.connectprogress.show()
		self.btn_public.hide()
		self.btn_favs.hide()
		self.btn_refresh.hide()
		self.btn_addfav.hide()
		self.btn_connect.hide()
		self.serverlist.hide()
		self.onlineplayers.hide()
		self.serverinfo.hide()
		self.clientver.hide()
		self.settingsbtn.hide()
		self.aoserverinfo.tcp.send('askchaa#%')

	def onClicked_cancelconnect(self):
		self.connectingimg.hide()
		self.connectcancel.hide()
		self.connectprogress.hide()
		self.btn_public.show()
		self.btn_favs.show()
		self.btn_refresh.show()
		self.btn_addfav.show()
		self.btn_connect.show()
		self.serverlist.show()
		self.onlineplayers.show()
		self.serverinfo.show()
		self.clientver.show()
		self.settingsbtn.show()

	def onClicked_serverlist(self, item):
		self.svclicked = item
		self.can_connect = False
		self.onlineplayers.setText('Retrieving...')

		text = item.text()
		print '[debug]', 'you clicked %s' % text
		for i in range(self.serverlist.count()):
			if self.serverlist.item(i) == item:
				if self.tab == 0:
					self.serverinfo.setText(self.actual_serverlist[i][3])
					self.aoserverinfo.setIP(text, *self.actual_serverlist[i][:2])
					print '[debug]', 'ind: ' + str(i) + ', ip: ' + self.actual_serverlist[i][0] + ', port: ' + str(self.actual_serverlist[i][1])
				elif self.tab == 1:
					self.aoserverinfo.setIP(text, *self.favoriteslist[i][:2])
					print '[debug]', 'ind: ' + str(i) + ', ip: ' + self.favoriteslist[i][0] + ', port: ' + str(self.favoriteslist[i][1])

				self.aoserverinfo.stop()
				self.aoserverinfo.start()

	def move_to_game(self, tcp, charlist, musiclist, background, evidence, areas, features=[], oocjoin=[], hplist=[]):
		self.gamewindow.showGame(tcp, charlist, musiclist, background, evidence, areas, features, oocjoin, hplist)

	def lobby_sendchat(self):
		text = self.lobbychatinput.text().toUtf8()
		self.ms_tcp.send('CT#' +self.oocname+ '#' + text + '#%')
		self.lobbychatinput.clear()

	def setoocname(self):
		self.oocname = self.oocnameinput.text().toUtf8()

	def lobbychatlog_update(self):
		if self.lobbychatlog.verticalScrollBar().value() == self.lobbychatlog.verticalScrollBar().maximum(): self.lobbychatlog.verticalScrollBar().setValue(self.lobbychatlog.verticalScrollBar().maximum())

	def newOOCMessage(self, name, text):
		self.lobbychatlog.append('%s: %s' % (name, text))


class MasterServer(QtCore.QThread):
	gotServers = QtCore.pyqtSignal(list)
	gotOOCMsg = QtCore.pyqtSignal(str, str)
	msgbox_signal = QtCore.pyqtSignal(int, str, str)

	def __init__(self):
		super(MasterServer, self).__init__()

	def run(self):
		tempdata = ""
		self.ms_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.ms_tcp.connect(('master.aceattorneyonline.com', 27016))
		except:
			return

		while True:
			contents = self.ms_tcp.recv(16384)
			if len(contents) == 0:
				print 'masterserver failure'
				return
			
			if not contents.endswith("%"):
				tempdata += contents
				continue
			else:
				if tempdata:
					contents = tempdata + contents
					tempdata = ""
			
			temp = contents.split('%')
			for msg in temp:
				network = msg.split('#')
				header = network[0]
				
				if header == "servercheok":
					self.ms_tcp.send("HI#AO2XP %s#%%ID#AO2XP by Headshot#1.4.1#%%" % hardware.get_hdid())
					self.ms_tcp.send("ALL#%")
				
				elif header == 'DOOM':
					print 'banned from masterserver'
					self.msgbox_signal.emit(0, "WHEEZE", "You are exiled from AO")
					self.ms_tcp.close()
					return
					
				elif header == 'ALL':
					self.gotServers.emit(network)

				elif header == 'CT':
					name = network[1].decode("utf-8").replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#').replace('<pound>', '#')
					chatmsg = network[2].decode("utf-8").replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#').replace('<pound>', '#')
					self.gotOOCMsg.emit(name, chatmsg)

class AOServerInfo(QtCore.QThread):
	moveToGameSignal = QtCore.pyqtSignal(list)
	msgbox_signal = QtCore.pyqtSignal(int, str, str)
	setOnlinePlayers = QtCore.pyqtSignal(str)
	setConnectProgress = QtCore.pyqtSignal(str)
	returnToLobby = QtCore.pyqtSignal()
	readySoon = QtCore.pyqtSignal()
	setWindowTitle = QtCore.pyqtSignal(str)
	canConnect = QtCore.pyqtSignal()

	def __init__(self):
		super(AOServerInfo, self).__init__()
		self.ip = ""
		self.port = 0
		self.name = "jm"
		self.disconnect = False

	def setIP(self, name, ip, port):
		self.ip = ip
		self.port = int(port)
		self.name = name

	def stop(self):
		self.disconnect = True
		if self.isRunning():
			self.terminate()
			self.wait()

	def run(self):
		self.disconnect = False
		self.tcp = socket.socket()
		try:
			self.tcp.connect((self.ip, self.port))
		except:
			self.setOnlinePlayers.emit("couldn't retrieve players")
			return
		self.tcp.settimeout(0.2)

		tempdata = ""
		gotChars = False
		hplist = []
		joinooc = []
		areas = [[], [], [], []]
		features = []
		evidence = []
		pingtimer = 150
		readytick = -1

		while True:
			if self.disconnect:
				try: self.tcp.close()
				except: pass
				return

			pingtimer -= 1
			if pingtimer == 0:
				pingtimer = 150
				self.tcp.send('CH#%')
			
			if readytick > -1:
				readytick -= 1
				if readytick == 0:
					readytick = -1
					try:
						self.moveToGameSignal.emit([self.tcp, charlist, musiclist, background, evidence, areas, features, joinooc, hplist])
					except Exception as err:
						self.msgbox_signal.emit(0, "Error caught while loading", traceback.format_exc(err))
						self.returnToLobby.emit()
						return
					
					self.setWindowTitle.emit(self.name)
					return
					
			try:
				contents = self.tcp.recv(16384)
			except (socket.timeout, socket.error) as err:
				error = err.args[0]
				if error == "timed out" or error == 10035:
					continue
				else:
					self.setOnlinePlayers.emit("Something wrong happened" if not got_stuff else "Connection lost")
					return

			if not contents.endswith("%"):
				tempdata += contents
				continue
			else:
				if tempdata:
					contents = tempdata + contents
					tempdata = ""

			totals = contents.split('%')
			for g in totals:
				network = g.split('#')
				header = network[0]
				
				if header == 'PN':
					players = int(network[1])
					maxplayers = int(network[2])
					self.canConnect.emit()
					self.setOnlinePlayers.emit('%d/%d players online' % (players, maxplayers))
					got_stuff = True
				
				elif header == "decryptor":
					self.tcp.send("HI#AO2XP %s#%%" % hardware.get_hdid())
				
				elif header == "ID":
					self.tcp.send("ID#AO2#69.1337.420#%") # need to send this to tsuserver3 servers in order to get feature list (FL)
					
				elif header == "FL":
					features = network[1:]
					print features
				
				elif header == 'BD':
					reason = network[1].decode("utf-8") if len(network) > 1 else "Failed to receive ban reason (old server version?)" # new in AO2 2.6
					self.setOnlinePlayers.emit('Banned')
					self.msgbox_signal.emit(0, "Banned", "Reason:\n"+reason)
					self.tcp.close()
					return
					
				elif header == 'SI':
					if self.disconnect:
						continue
					maxchars = int(network[1])
					maxevidence = int(network[2])
					maxmusic = int(network[3])
					self.setConnectProgress.emit('Requesting character list (%d)...' % maxchars)
					self.tcp.send('RC#%')
					print '[client]', '%d characters, %d pieces of evidence and %d songs' % (maxchars, maxevidence, maxmusic)
					
				elif header == 'SC':
					if self.disconnect:
						continue
					del network[0]
					del network[len(network)-1]
					gotChars = True
					charlist = [ [char.split('&')[0], -1, "male"] for char in network ]
					self.setConnectProgress.emit('Requesting music list (%d)...' % maxmusic)
					self.tcp.send('RM#%')
					print '[client]', 'received characters (%d)' % len(charlist)
					
				elif header == 'SM':
					if self.disconnect:
						continue
					del network[0]
					del network[len(network)-1]
					
					musiclist = [music for music in network]
					
					self.setConnectProgress.emit('Finishing...')
					self.tcp.send('RD#%')
					print '[client]', 'received songs (%d)' % len(musiclist)
					
				elif header == 'CharsCheck':
					if self.disconnect or not gotChars:
						continue
					network.pop(0)
					network.pop(len(network)-1)
					for i in range(len(network)):
						charlist[i][1] = int(network[i])

				elif header == 'BN':
					if self.disconnect:
						continue
					background = network[1]
					print '[client]', 'courtroom background: %s' % background
					
				elif header == 'LE':
					if self.disconnect:
						continue
					del network[0]
					del network[len(network)-1]
					if len(network) > 0:
						evidence = [evi.split("&") for evi in network]
					else:
						evidence = []
					
					for evi in evidence:
						while len(evi) < 3: # new AO 2.9 bug where they never correctly escaped evidence name/desc/image on FantaProtocol
							evi += [""]
						evi[0] = decode_ao_str(evi[0].decode("utf-8"))
						evi[1] = decode_ao_str(evi[1].decode("utf-8"))
						evi[2] = decode_ao_str(evi[2].decode("utf-8"))
					print '[client]', 'received evidence'
				
				elif header == 'HP':
					if self.disconnect:
						continue
					del network[0]
					del network[len(network)-1]
					type = int(network[0])
					health = int(network[1])
					hplist.append([type, health])
				
				elif header == "ARUP": #AO2 2.6 new feature: area update
					del network[0]
					del network[len(network)-1]
					type = int(network[0])
					if type == 0: #player count
						areas[type] = [network[i] for i in range(1, len(network))]
					else: #area status, casemakers or locked area
						areas[type] = [network[i] for i in range(1, len(network))]
					
				elif header == 'DONE':
					if self.disconnect:
						continue
					self.setConnectProgress.emit('Done, loading...')
					self.readySoon.emit()
					print '[client]', 'finished requesting data, loading game...'
					readytick = 4
					
				elif header == 'CT':
					if self.disconnect:
						continue
					del network[0]
					del network[len(network)-1]
					name = network[0].decode("utf-8").replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#').replace('<pound>', '#')
					chatmsg = network[1].decode("utf-8").replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#').replace('<pound>', '#')
					joinooc.append("%s: %s" % (name, chatmsg))