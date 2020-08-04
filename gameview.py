import socket, thread, time, os, buttons, urllib, charselect, ini, random
from PyQt4 import QtGui, QtCore
from pybass import *
from os.path import exists
from functools import partial
from ConfigParser import ConfigParser

import images

AOpath = "base/"
#AOpath = 'I:/aovanilla1.7.5/client/base/'

PREANIM = 2
CHARNAME = 3
ANIM = 4
CHATMSG = 5
SIDE = 6
SFX = 7
EMOTE_MOD = 8
CHAR_ID = 9
SFX_DELAY = 10
SHOUT_MOD = 11
EVIDENCE = 12
FLIP = 13
REALIZATION = 14
TEXT_COLOR = 15
SHOWNAME = 16
OTHER_CHARID = 17
OTHER_NAME = 18
OTHER_EMOTE = 19
SELF_OFFSET = 20
OTHER_OFFSET = 21
OTHER_FLIP = 22
NO_INTERRUPT = 23

INLINE_BLUE = 0
INLINE_GREEN = 1
INLINE_ORANGE = 2
INLINE_GRAY = 3

C_WHITE = 0
C_GREEN = 1
C_RED = 2
C_ORANGE = 3
C_BLUE = 4
C_YELLOW = 5
C_RAINBOW = 6
C_PINK = 7
C_CYAN = 8

DOWNLOAD_BLACKLIST = []

def delay(msec):
	dieTime = QtCore.QTime.currentTime().addMSecs(msec)
	
	while QtCore.QTime.currentTime() < dieTime:
		QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 100)

def decode_ao_str(text):
	return text.replace("<percent>", "%").replace("<pound>", "#").replace("<num>", "#").replace("<and>", "&").replace("<dollar>", "$")
	
def get_char_ini(char, section, value, default=""):
	tempini = ConfigParser()
	tempini.read(AOpath + 'characters/' + char + '/char.ini')
	return ini.read_ini(tempini, section, value, default)

def get_option(section, value, default=""):
        tempini = ConfigParser()
	tempini.read("base/ao2xp.ini")
	return ini.read_ini(tempini, section, value, default)

def get_text_color(textcolor):
	if textcolor == 0 or textcolor == 6:
		return QtGui.QColor(255, 255, 255)
	elif textcolor == 1:
		return QtGui.QColor(0, 255, 0)
	elif textcolor == 2: # OH FUCK MOD
		return QtGui.QColor(255, 0, 0)
	elif textcolor == 3:
		return QtGui.QColor(255, 165, 0)
	elif textcolor == 4:
		return QtGui.QColor(45, 150, 255)
	elif textcolor == 5:
		return QtGui.QColor(255, 255, 0)
	elif textcolor == 7:
		return QtGui.QColor(255, 192, 203)
	elif textcolor == 8:
		return QtGui.QColor(0, 255, 255)
	elif textcolor == "_inline_grey":
		return QtGui.QColor(187, 187, 187)
	
	return QtGui.QColor(0, 0, 0)

def download_thread(link, savepath):
	global DOWNLOAD_BLACKLIST
	if link in DOWNLOAD_BLACKLIST:
		return
	
	print link, savepath
	fp = urllib.urlopen(link)
	if fp.getcode() != 200:
		DOWNLOAD_BLACKLIST.append(link)
		print "HTTP error %d while downloading %s" % (fp.getcode(), link)
	else:
		with open(savepath, "wb") as f:
			f.write(fp.read())

def mockStr(text):
	upper = random.choice([True, False])
	l = list(text)
	for i in range(len(text)):
		if text[i] == " ":
			continue
		
		l[i] = l[i].upper() if upper else l[i].lower()
		upper = not upper
	return "".join(l)

class ChatLogs(QtGui.QTextEdit):
	def __init__(self, parent, logtype, logfile=None):
		QtGui.QTextEdit.__init__(self, parent)
		self.type = logtype
		self.savelog = ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "save logs")
		self.combinelog = ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "combined logs")
		if not exists("chatlogs"):
			os.mkdir("chatlogs")
		
		if self.savelog:
			currtime = time.localtime()
			if self.combinelog:
				if self.type == 0:
					self.logfile = logfile
				else:
					self.logfile = open("chatlogs/%d%.2d%.2d_on_%.2d.%.2d.%.2d.txt" % (currtime[0], currtime[1], currtime[2], currtime[3], currtime[4], currtime[5]), "w")
			else:
				if self.type == 0:
					self.logfile = open("chatlogs/IC_%d%.2d%.2d_on_%.2d.%.2d.%.2d.txt" % (currtime[0], currtime[1], currtime[2], currtime[3], currtime[4], currtime[5]), "w")
				else:
					self.logfile = open("chatlogs/OOC_%d%.2d%.2d_on_%.2d.%.2d.%.2d.txt" % (currtime[0], currtime[1], currtime[2], currtime[3], currtime[4], currtime[5]), "w")
		else:
                        self.logfile = None
	
	def __del__(self):
		if self.savelog:
			self.logfile.close()
	
	def append(self, text):
		super(ChatLogs, self).append(text)
		if self.savelog:
			if isinstance(text, str) or isinstance(text, unicode):
				if self.combinelog and not "Log started" in text:
					if self.type == 0:
						self.logfile.write("[IC] "+text.encode("utf-8")+"\n")
					else:
						self.logfile.write("[OOC] "+text.encode("utf-8")+"\n")
				else:
					self.logfile.write(text.encode("utf-8")+"\n")
			else:
				if self.combinelog and not "Log started" in text:
					if self.type == 0:
						self.logfile.write("[IC] "+text.toUtf8()+"\n")
					else:
						self.logfile.write("[OOC] "+text.toUtf8()+"\n")
				else:
					self.logfile.write(text.toUtf8()+"\n")

class AOCharMovie(QtGui.QLabel):
	done = QtCore.pyqtSignal()
	use_pillow = 0
	pillow_frames = []
	pillow_frame = 0
	pillow_speed = 0

	def __init__(self, parent):
		QtGui.QLabel.__init__(self, parent)
		
		self.resize(256, 192)
		self.time_mod = 62
		self.play_once = True
		self.m_flipped = False
		
		self.m_movie = QtGui.QMovie()
		
		self.preanim_timer = QtCore.QTimer(self)
		self.preanim_timer.setSingleShot(True)
		self.pillow_timer = QtCore.QTimer(self)
		self.pillow_timer.setSingleShot(True)

		self.preanim_timer.timeout.connect(self.timer_done)
		self.pillow_timer.timeout.connect(self.pillow_frame_change)
		self.m_movie.frameChanged.connect(self.frame_change)
	
	def set_flipped(self, flip):
		self.m_flipped = flip
	
	def play(self, p_char, p_emote, emote_prefix):
		if p_emote[0] == "/" or p_emote[0] == "/":
			p_emote = p_emote[1:]
		elif "../../characters" in p_emote:
			print p_emote
			a = p_emote.split("/")
			p_char = a[3]
			emote = a[4]
			emote_prefix = ""
			p_emote = emote
        
		self.pillow_frames = []
		self.pillow_frame = 0
		
		original_path = AOpath+"characters/"+p_char+"/"+emote_prefix+p_emote+".gif"
		alt_path = AOpath+"characters/"+p_char+"/"+p_emote+".png"
		apng_path = AOpath+"characters/"+p_char+"/"+emote_prefix+p_emote+".apng"
		webp_path = AOpath+"characters/"+p_char+"/"+emote_prefix+p_emote+".webp"
		placeholder_path = AOpath+"themes/default/placeholder.gif"
		gif_path = ""
		
		if exists(apng_path):
			gif_path = apng_path
			self.use_pillow = 1
		else:
			if ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "download characters"):
				url = "http://s3.wasabisys.com/webao/base/characters/"+p_char.lower()+"/"+emote_prefix+p_emote.lower()+".apng"
				url = url.replace(" ", "%20")
				if not exists(AOpath+"characters/"+p_char): # gotta make sure the character folder exists, better safe than sorry
					os.mkdir(AOpath+"characters/"+p_char)
				thread.start_new_thread(download_thread, (url, apng_path))

			if exists(webp_path):
				gif_path = webp_path
				self.use_pillow = 2
			else:
				if ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "download characters"):
					url = "http://s3.wasabisys.com/webao/base/characters/"+p_char.lower()+"/"+p_emote.lower()+".webp"
					url = url.replace(" ", "%20")
					if not exists(AOpath+"characters/"+p_char): # gotta make sure the character folder exists, better safe than sorry
						os.mkdir(AOpath+"characters/"+p_char)
					thread.start_new_thread(download_thread, (url, webp_path))

				if exists(original_path):
					gif_path = original_path
					self.use_pillow = 0
				else:
					if ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "download characters"):
						url = "http://s3.wasabisys.com/webao/base/characters/"+p_char.lower()+"/"+emote_prefix+p_emote.lower()+".gif"
						url = url.replace(" ", "%20")
						if not exists(AOpath+"characters/"+p_char): # gotta make sure the character folder exists, better safe than sorry
							os.mkdir(AOpath+"characters/"+p_char)
						thread.start_new_thread(download_thread, (url, original_path))

					if exists(alt_path):
						gif_path = alt_path
						self.use_pillow = 0
					else:
						if ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "download characters"):
							url = "http://s3.wasabisys.com/webao/base/characters/"+p_char.lower()+"/"+emote_prefix+p_emote.lower()+".png"
							url = url.replace(" ", "%20")
							if not exists(AOpath+"characters/"+p_char): # gotta make sure the character folder exists, better safe than sorry
								os.mkdir(AOpath+"characters/"+p_char)
							thread.start_new_thread(download_thread, (url, alt_path))

						if exists(placeholder_path):
							gif_path = placeholder_path
						else:
							gif_path = ""
						self.use_pillow = 0

		if not self.use_pillow:
			self.m_movie.stop()
			self.m_movie.setFileName(gif_path)
			self.m_movie.start()

		elif self.use_pillow == 1: # apng
			self.pillow_frames = images.load_apng(apng_path)
			#print apng_path, self.pillow_frames[0], int(self.pillow_frames[0][1] * self.pillow_speed) if len(self.pillow_frames[0]) > 1 else 0
			if len(self.pillow_frames) > 1: self.pillow_timer.start(int(self.pillow_frames[0][1] * self.pillow_speed))
			self.set_pillow_frame()

		elif self.use_pillow == 2: # webp
			self.pillow_frames = images.load_webp(webp_path)
			if len(self.pillow_frames) > 1: self.pillow_timer.start(int(self.pillow_frames[0][1] * self.pillow_speed))
			self.set_pillow_frame()

		self.show()
	
	def play_pre(self, p_char, p_emote, duration):
		gif_path = AOpath+"characters/"+p_char+"/"+p_emote+".gif"
		apng_path = AOpath+"characters/"+p_char+"/"+p_emote+".apng"
		webp_path = AOpath+"characters/"+p_char+"/"+p_emote+".webp"

		full_duration = duration * self.time_mod
		real_duration = 0

		self.play_once = False
		self.m_movie.stop()
		self.clear()

		if exists(apng_path):
			real_duration = images.get_apng_duration(apng_path)

		elif exists(webp_path):
			real_duration = images.get_webp_duration(webp_path)

		elif exists(gif_path):
			self.m_movie.setFileName(gif_path)
			self.m_movie.jumpToFrame(0)
			for n_frame in range(self.m_movie.frameCount()):
				real_duration += self.m_movie.nextFrameDelay()
				self.m_movie.jumpToFrame(n_frame + 1)
		
		percentage_modifier = 100.0
		
		if real_duration != 0 and duration != 0:
			modifier = full_duration / float(real_duration)
			percentage_modifier = 100 / modifier
			
			if percentage_modifier > 100.0 or percentage_modifier < 0.0:
				percentage_modifier = 100.0
		
		self.pillow_fullduration = full_duration
		if full_duration == 0 or full_duration >= real_duration:
			self.play_once = True
		else:
			self.play_once = False
			if full_duration >= 0:
				self.preanim_timer.start(full_duration)
		
		self.m_movie.setSpeed(int(percentage_modifier))
		self.pillow_speed = percentage_modifier / 100.
		self.play(p_char, p_emote, "")
	
	def play_talking(self, p_char, p_emote):
		gif_path = AOpath + 'characters/' + p_char + '/(b)' + p_emote + '.gif'
		
		self.m_movie.stop()
		self.clear()
		self.m_movie.setFileName(gif_path)
		self.m_movie.jumpToFrame(0)
		
		self.play_once = False
		self.m_movie.setSpeed(100)
		self.pillow_speed = 1
		self.play(p_char, p_emote, '(b)')

	def play_idle(self, p_char, p_emote):
		gif_path = AOpath + 'characters/' + p_char + '/(a)' + p_emote + '.gif'
		
		self.m_movie.stop()
		self.clear()
		self.m_movie.setFileName(gif_path)
		self.m_movie.jumpToFrame(0)
		
		self.play_once = False
		self.m_movie.setSpeed(100)
		self.pillow_speed = 1
		self.play(p_char, p_emote, '(a)')

	def stop(self):
		self.m_movie.stop()
		self.preanim_timer.stop()
		self.hide()

	@QtCore.pyqtSlot(int)
	def frame_change(self, n_frame):
		f_img = self.m_movie.currentImage().mirrored(self.m_flipped, False)
		if f_img.size().width() != 256 or f_img.size().height() != 192:
			f_img = f_img.scaled(256, 192, transformMode=QtCore.Qt.SmoothTransformation)

		f_pixmap = QtGui.QPixmap.fromImage(f_img)
		self.setPixmap(f_pixmap)
		
		if self.m_movie.frameCount() - 1 == n_frame and self.play_once:
			self.preanim_timer.start(self.m_movie.nextFrameDelay())

	@QtCore.pyqtSlot()
	def pillow_frame_change(self):
		if len(self.pillow_frames)-1 == self.pillow_frame:
			if self.play_once:
				self.preanim_timer.start(int(self.pillow_frames[self.pillow_frame][1] * self.pillow_speed))
			elif len(self.pillow_frames) > 1:
				self.pillow_frame = 0
				self.pillow_timer.start(int(self.pillow_frames[self.pillow_frame][1] * self.pillow_speed))
		else:
			self.pillow_frame += 1
			self.pillow_timer.start(int(self.pillow_frames[self.pillow_frame][1] * self.pillow_speed))

		self.set_pillow_frame()

	def set_pillow_frame(self):
		f_img = self.pillow_frames[self.pillow_frame][0].mirrored(self.m_flipped, False)
		if f_img.size().width() != 256 or f_img.size().height() != 192:
			f_img = f_img.scaled(256, 192, transformMode=QtCore.Qt.SmoothTransformation)

		f_pixmap = QtGui.QPixmap.fromImage(f_img)
		self.setPixmap(f_pixmap)

	@QtCore.pyqtSlot()
	def timer_done(self):
		self.done.emit()

class AOMovie(QtGui.QLabel):
	play_once = True
	done = QtCore.pyqtSignal()
	
	def __init__(self, parent):
		QtGui.QLabel.__init__(self, parent)
		self.m_movie = QtGui.QMovie()
		self.setMovie(self.m_movie)
		self.m_movie.frameChanged.connect(self.frame_change)
	
	def set_play_once(self, once):
		self.play_once = once
	
	def play(self, p_gif, p_char):
		self.m_movie.stop()
		
		gif_path = ""
		
		custom_path = ""
		if p_gif == "custom":
			custom_path = AOpath+"characters/"+p_char+"/"+p_gif+".gif"
		else:
			custom_path = AOpath+"characters/"+p_char+"/"+p_gif+"_bubble.gif"
		
		theme_path = AOpath+"themes/default/"+p_gif+".gif"
		placeholder_path = AOpath+"themes/default/placeholder.gif"
		
		if exists(custom_path):
			gif_path = custom_path
		elif exists(theme_path):
			gif_path = theme_path
		else:
			gif_path = placeholder_path
		
		self.m_movie.setFileName(gif_path)
		
		self.show()
		self.m_movie.start()
	
	def stop(self):
		self.m_movie.stop()
		self.hide()
	
	@QtCore.pyqtSlot(int)
	def frame_change(self, n_frame):
		if n_frame == self.m_movie.frameCount() - 1 and self.play_once:
			delay(self.m_movie.nextFrameDelay())
			self.stop()
			self.done.emit()

class ZoomLines(QtGui.QLabel):

	def __init__(self, parent):
		super(ZoomLines, self).__init__(parent)
		self.resize(256, 192)
		self.movie = QtGui.QMovie()
		self.movie.frameChanged.connect(self.frame_change)

	def frame_change(self):
		img = self.movie.currentImage()
		self.setPixmap(QtGui.QPixmap.fromImage(img))

	def setZoom(self, on, dir=0):
		self.movie.stop()
		if not on:
			self.hide()
			return
		self.show()
		if dir == 0:
			self.movie.setFileName(AOpath + 'themes/default/defense_speedlines.gif')
		else:
			self.movie.setFileName(AOpath + 'themes/default/prosecution_speedlines.gif')
		self.movie.start()


class WTCE_View(QtGui.QLabel):

	def __init__(self, parent):
		super(WTCE_View, self).__init__(parent)
		self.movie = QtGui.QMovie()
		self.movie.frameChanged.connect(self.frame_change)
		self.finalframe_timer = QtCore.QTimer()
		self.finalframe_timer.setSingleShot(False)
		self.finalframe_timer.timeout.connect(self.finished)
		self.resize(256, 192)

	def frame_change(self, frame):
		if self.movie.state() != QtGui.QMovie.Running:
			return
		img = self.movie.currentImage()
		self.setPixmap(QtGui.QPixmap.fromImage(img))
		if self.movie.currentFrameNumber() == self.movie.frameCount() - 1:
			self.finalframe_timer.start(self.movie.nextFrameDelay())

	def finished(self):
		self.finalframe_timer.stop()
		self.movie.stop()
		self.hide()

	def showWTCE(self, wtce, variant=0):
		self.finished()
		if wtce == 'testimony1':
			self.movie.setFileName(AOpath + 'themes/default/witnesstestimony.gif')
		elif wtce == 'testimony2':
			self.movie.setFileName(AOpath + 'themes/default/crossexamination.gif')
		elif wtce == "judgeruling":
			if variant == 0:
				self.movie.setFileName(AOpath + 'themes/default/notguilty.gif')
			elif variant == 1:
				self.movie.setFileName(AOpath + 'themes/default/guilty.gif')
		else:
			return
		self.show()
		self.movie.start()

class gui(QtGui.QWidget):
	gamewindow = None
	sound = None
	music = None
	next_character_is_not_special = False
	message_is_centered = False
	current_display_speed = 3
	message_display_speed = (30, 40, 50, 60, 75, 100, 120)
	entire_message_is_blue = False
	inline_color_stack = [] #"colour" is for EU nobos
	inline_blue_depth = 0
	other_charid = -1
	offset_with_pair = 0
	tick_pos = 0
	blip_pos = 0
	blip_rate = 1
	time_mod = 40
	blip = "male"
	blipsnd = None
	chatmessage_size = 24
	m_chatmessage = []
	blank_blip = False
	chatmessage_is_empty = False
	anim_state = 3
	text_state = 2
	objection_state = 0
	text_color = 0
	
	charini = ConfigParser()
	chatmsg = ''
	charid = -1
	#ICchat = QtCore.pyqtSignal(str, str, str, str, str, str, int, int, int, int, int, int, int, int)
	#ICchat = QtCore.pyqtSignal(list)
	WTCEsignal = QtCore.pyqtSignal(str, int)
	healthbars = QtCore.pyqtSignal(int, int)
	gotPing = QtCore.pyqtSignal(int)

	def __init__(self, parent=None):
		super(gui, self).__init__(parent)
		self.gamewindow = parent
		
		self.gotPing.connect(self.setPing)
		
		for i in range(self.chatmessage_size):
			self.m_chatmessage.append("")
			
		self.chat_tick_timer = QtCore.QTimer(self)
		self.chat_tick_timer.timeout.connect(self.chat_tick)
		
		self.sfx_delay_timer = QtCore.QTimer(self)
		self.sfx_delay_timer.setSingleShot(True)
		self.sfx_delay_timer.timeout.connect(self.play_sfx)
		
		if exists('mod_call.wav'):
			self.modcall = BASS_StreamCreateFile(False, 'mod_call.wav', 0, 0, 0)
		else:
			self.modcall = None
			
		self.wtcesfx = BASS_StreamCreateFile(False, AOpath + 'sounds/general/sfx-testimony2.wav', 0, 0, 0)
		self.guiltysfx = BASS_StreamCreateFile(False, AOpath+"sounds/general/sfx-guilty.wav", 0, 0, 0)
		self.notguiltysfx = BASS_StreamCreateFile(False, AOpath+"sounds/general/sfx-notguilty.wav", 0, 0, 0)
		
		self.healthbars.connect(self.netmsg_hp)
		self.disconnectnow = False
		self.swapping = False
		self.iniswapindex = 0
		self.background = 'default'
		
		self.viewport = QtGui.QWidget(self)
		self.viewport.resize(256, 192)
		
		self.court = QtGui.QLabel(self.viewport)
		self.zoom = ZoomLines(self.viewport)
		
		self.char = AOCharMovie(self.viewport)
		self.char.done.connect(self.preanim_done)
		self.sidechar = AOCharMovie(self.viewport)
		self.sidechar.hide()
		
		self.bench = QtGui.QLabel(self.viewport)
		bench = QtGui.QPixmap(AOpath + 'background/default/defensedesk.png')
		self.court.setPixmap(QtGui.QPixmap(AOpath + 'background/default/defenseempty.png'))
		self.bench.setPixmap(bench)
		self.chatbox = QtGui.QLabel(self)
		chatbox = QtGui.QPixmap(AOpath + 'themes/default/chatmed.png')
		chatboxheight = chatbox.size().height()
		self.chatbox.setPixmap(chatbox)
		self.chatbox.move(0, 192 - chatboxheight)
		
		self.text = QtGui.QLabel(self)
		self.text.setWordWrap(True)
		self.text.resize(250, 96)
		self.text.move(6, 192 - chatboxheight + 20)
		self.text.setStyleSheet('color: white')
		self.text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		
		self.ao2text = QtGui.QTextEdit(self)
		self.ao2text.setFrameStyle(QtGui.QFrame.NoFrame)
		self.ao2text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.ao2text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.ao2text.setReadOnly(True)
		self.ao2text.setGeometry(2, 192-chatboxheight+16, 240+10, 96)
		self.ao2text.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
		self.ao2text.setStyleSheet("background-color: rgba(0, 0, 0, 0);"
													"color: white")
		
		self.name = QtGui.QLabel(self.chatbox)
		self.name.setStyleSheet('color: white')
		self.name.move(5, 0)
		self.name.resize(248, self.name.sizeHint().height())
		self.wtceview = WTCE_View(self)
		self.WTCEsignal.connect(self.wtceview.showWTCE)
		
		self.objectionview = AOMovie(self)
		self.objectionview.done.connect(self.objection_done)
		
		self.whiteflashlab = QtGui.QLabel(self)
		self.whiteflashlab.setPixmap(QtGui.QPixmap(AOpath + 'themes/default/realizationflash.png'))
		self.whiteflashlab.setGeometry(0, 0, 256, 192)
		self.whiteflashlab.hide()
		self.whiteflash = QtCore.QTimer()
		self.whiteflash.setSingleShot(False)
		self.whiteflash.timeout.connect(partial(self.setWhiteFlash, False))
		
		self.ooclog = ChatLogs(self, 1)
		self.ooclog.setReadOnly(True)
		self.ooclog.setStyleSheet('background-color: rgb(139, 139, 139);')
		self.ooclog.textChanged.connect(self.ooclog_update)
		
		self.oocnameinput = QtGui.QLineEdit(self)
		self.oocnameinput.setPlaceholderText('Enter a name...')
		self.oocnameinput.setStyleSheet('background-color: rgb(139, 139, 139);')
		
		self.oocinput = QtGui.QLineEdit(self)
		self.oocinput.setPlaceholderText('Server chat/OOC chat...')
		self.oocinput.setStyleSheet('background-color: rgb(139, 139, 139);')
		self.oocinput.returnPressed.connect(self.onOOCreturn)
		
		self.ooclogin = QtGui.QPushButton("Login", self)
		self.ooclogin.clicked.connect(self.onOOCLoginBtn)
		
		self.musicitems = QtGui.QListWidget(self)
		self.musicitems.itemDoubleClicked.connect(self.onMusicClick)
		
		self.gametabs = QtGui.QTabWidget(self)
		self.gametab_log = QtGui.QWidget() # the IC chat log
		self.gametab_evidence = QtGui.QWidget() # court record
		self.gametab_msgqueue = QtGui.QWidget() # IC messages pending to be sent
		self.gametab_iniswap = QtGui.QWidget() # self explanatory
		self.gametab_mute = QtGui.QWidget() # mute a player
		self.gametab_pair = QtGui.QWidget() # AO2 pair
		self.gametab_misc = QtGui.QWidget() # ao2xp misc/fun stuff
		
		self.icLog = ChatLogs(self.gametab_log, 0, self.ooclog.logfile)
		self.icLog.setReadOnly(True)
		self.icLog.textChanged.connect(self.icLogChanged)
		
		self.evidencedropdown = QtGui.QComboBox(self.gametab_evidence)
		self.evidencedropdown.currentIndexChanged.connect(self.changeEvidence)
		self.evidencedesc = QtGui.QTextEdit(self.gametab_evidence)
		self.evidencedesc.setReadOnly(True)
		self.evidenceimage = QtGui.QLabel(self.gametab_evidence)
		self.evidenceimage.setPixmap(QtGui.QPixmap(AOpath + 'evidence/empty.png'))
		self.evidenceimage.show()
		self.evidenceadd = QtGui.QPushButton(self.gametab_evidence)
		self.evidenceadd.setText('Add')
		self.evidenceadd.clicked.connect(self.onAddEvidence)
		self.evidenceedit = QtGui.QPushButton(self.gametab_evidence)
		self.evidenceedit.setText('Edit')
		self.evidenceedit.clicked.connect(self.onEditEvidence)
		self.evidencedelete = QtGui.QPushButton(self.gametab_evidence)
		self.evidencedelete.setText('Delete')
		self.evidencedelete.clicked.connect(self.onDeleteEvidence)
		self.evidencepresent = PresentButton(self, self.gametab_evidence)
		
		self.msgqueueList = QtGui.QListWidget(self.gametab_msgqueue)
		self.msgqueueList.itemClicked.connect(self.onClicked_msgqueue)
		self.removeQueue = QtGui.QPushButton(self.gametab_msgqueue)
		self.removeQueue.setText('Delete')
		self.removeQueue.clicked.connect(self.onClicked_removeQueue)
		
		self.unmutedlist = QtGui.QListWidget(self.gametab_mute)
		self.mutedlist = QtGui.QListWidget(self.gametab_mute)
		self.mutebtn = QtGui.QPushButton(self.gametab_mute)
		self.unmutebtn = QtGui.QPushButton(self.gametab_mute)
		self.notmutedlabel = QtGui.QLabel(self.gametab_mute)
		self.mutedlabel = QtGui.QLabel(self.gametab_mute)
		self.notmutedlabel.setText('Not muted')
		self.mutedlabel.setText('Muted')
		self.mutebtn.setText('>>')
		self.unmutebtn.setText('<<')
		self.mutebtn.clicked.connect(self.onMuteClick)
		self.unmutebtn.clicked.connect(self.onUnmuteClick)
		self.mutedlist.itemClicked.connect(self.changeMuteIndex)
		self.unmutedlist.itemClicked.connect(self.changeUnmuteIndex)
		
		self.iniswaplist = QtGui.QComboBox(self.gametab_iniswap)
		self.iniswaplist.currentIndexChanged.connect(self.iniswap_index_change)
		self.iniswapconfirm = QtGui.QPushButton(self.gametab_iniswap)
		self.iniswapconfirm.setText('Swap')
		self.iniswapconfirm.clicked.connect(self.iniswap_confirm)
		self.iniswapreset = QtGui.QPushButton(self.gametab_iniswap)
		self.iniswapreset.setText('Reset')
		self.iniswapreset.clicked.connect(self.resetIniSwap)
		self.iniswapinfo = QtGui.QLabel(self.gametab_iniswap)
		self.iniswapinfo.setText('Not swapped')
		self.iniswaprefresh = QtGui.QPushButton(self.gametab_iniswap)
		self.iniswaprefresh.setText('Refresh characters')
		self.iniswaprefresh.clicked.connect(self.loadSwapCharacters)
		
		self.paircheckbox = QtGui.QCheckBox(self.gametab_pair)
		self.paircheckbox.setChecked(False)
		self.pairdropdown = QtGui.QComboBox(self.gametab_pair)
		self.pairdropdown_l = QtGui.QLabel("Pair with...", self.gametab_pair)
		self.pairdropdown_l.move(self.pairdropdown.x() - 64, self.pairdropdown.y()+2)
		self.pairoffset = QtGui.QSlider(QtCore.Qt.Horizontal, self.gametab_pair)
		self.pairoffset.setRange(-100, 100)
		self.pairoffset.setValue(0)
		self.pairoffset_l = QtGui.QLabel("Position offset", self.gametab_pair)
		self.pairoffsetreset = QtGui.QPushButton("Reset", self.gametab_pair)
		self.pairoffsetreset.clicked.connect(partial(self.pairoffset.setValue, 0))
		
		self.misc_layout = QtGui.QVBoxLayout(self.gametab_misc)
		self.misc_layout.setAlignment(QtCore.Qt.AlignTop)
		self.mocktext = QtGui.QCheckBox()
		self.mocktext.setChecked(False)
		self.mocktext.setText(mockStr("mock text"))
		self.spacebartext = QtGui.QCheckBox()
		self.spacebartext.setChecked(False)
		self.spacebartext.setText("S p a c i n g")
		self.autocaps = QtGui.QCheckBox()
		self.autocaps.setChecked(False)
		self.autocaps.setText("Automatic caps and period")
		self.misc_layout.addWidget(self.mocktext)
		self.misc_layout.addWidget(self.spacebartext)
		self.misc_layout.addWidget(self.autocaps)
		
		self.gametabs.addTab(self.gametab_log, 'Game log')
		self.gametabs.addTab(self.gametab_evidence, 'Evidence')
		self.gametabs.addTab(self.gametab_msgqueue, 'Message queue')
		self.gametabs.addTab(self.gametab_mute, 'Mute')
		self.gametabs.addTab(self.gametab_iniswap, 'Easy IniSwap')
		self.gametabs.addTab(self.gametab_pair, 'Pair')
		self.gametabs.addTab(self.gametab_misc, 'Misc')
		
		self.icchatinput = QtGui.QLineEdit(self)
		self.icchatinput.setGeometry(0, 192, 256, 23)
		self.icchatinput.returnPressed.connect(self.onICreturn)
		self.icchatinput.setPlaceholderText('Game chat')
		
		self.emotedropdown = QtGui.QComboBox(self)
		self.emotedropdown.setGeometry(192, 344, 128, 20)
		self.emotedropdown.currentIndexChanged.connect(partial(self.changeEmote, True))
		
		self.colordropdown = QtGui.QComboBox(self)
		self.colordropdown.setGeometry(192, 376, 72, 20)
		self.colordropdown.currentIndexChanged.connect(self.setChatColor)
		
		self.posdropdown = QtGui.QComboBox(self)
		self.posdropdown.addItems(["def", "pro", "wit", "hld", "hlp", "jud"])
		self.posdropdown.setGeometry(self.emotedropdown.x() + self.emotedropdown.size().width() + 8, 344, 64, 20)
		self.posdropdown.currentIndexChanged.connect(self.setPosition)
		
		self.flipbutton = QtGui.QCheckBox(self)
		self.flipbutton.stateChanged.connect(self.changeFlipCheck)
		self.flipbutton.setText('Mirror emote')
		self.flipbutton.resize(self.flipbutton.sizeHint())
		self.flipbutton.move(272, 240)
		
		self.sfxbutton = QtGui.QCheckBox(self)
		self.sfxbutton.setChecked(True)
		self.sfxbutton.stateChanged.connect(self.changeSfxCheck)
		self.sfxbutton.setText('Play pre-animation')
		self.sfxbutton.resize(self.sfxbutton.sizeHint())
		self.sfxbutton.move(272, 272-12)
		
		self.nointerruptbtn = QtGui.QCheckBox(self)
		self.nointerruptbtn.setChecked(False)
		self.nointerruptbtn.setText('No Interrupt')
		self.nointerruptbtn.resize(self.sfxbutton.sizeHint())
		self.nointerruptbtn.move(272, 272+8)
		
		self.changechar = QtGui.QPushButton(self)
		self.changechar.setText('Switch character')
		self.changechar.setGeometry(10, 344, 121, 23)
		self.changechar.clicked.connect(self.onClick_changeChar)
		self.callmodbtn = QtGui.QPushButton(self)
		self.callmodbtn.setText('Call mod')
		self.callmodbtn.setGeometry(10, 376, 71, 23)
		self.callmodbtn.clicked.connect(self.onClick_callMod)
		
		self.settingsbtn = QtGui.QPushButton("Settings", self)
		self.settingsbtn.setGeometry(self.callmodbtn.x()+self.callmodbtn.size().width()+8, 376, self.settingsbtn.sizeHint().width(), 23)
		self.settingsbtn.clicked.connect(self.gamewindow.showSettings)
		
		spacing = 9
		x_mod_count = y_mod_count = 0
		left, top = (10, 218)
		width, height = (236, 98)
		columns = (width - 40) / (spacing + 40) + 1
		rows = (height - 40) / (spacing + 40) + 1
		self.max_emotes_on_page = columns * rows
		self.emotebuttons = []
		for i in range(self.max_emotes_on_page):
			x_pos = (40 + spacing) * x_mod_count
			y_pos = (40 + spacing) * y_mod_count
			self.emotebuttons.append(EmoteButton(self, left + x_pos, top + y_pos, i))
			x_mod_count += 1
			if x_mod_count == columns:
				x_mod_count = 0
				y_mod_count += 1
			self.emotebuttons[i].show()

		self.current_emote_page = 0
		self.prevemotepage = BackEmoteButton(self, 0, 253)
		self.prevemotepage.hide()
		self.nextemotepage = NextEmoteButton(self, 236, 253)
		self.nextemotepage.show()
		self.realizationbtn = buttons.RealizationButton(self, 265, 192)
		self.realizationsnd = BASS_StreamCreateFile(False, AOpath + 'sounds/general/sfx-realization.wav', 0, 0, 0)
		self.customobject = buttons.CustomObjection(self, 250, 312)
		self.holditbtn = buttons.Objections(self, 10, 312, 1)
		self.objectbtn = buttons.Objections(self, 90, 312, 2)
		self.takethatbtn = buttons.Objections(self, 170, 312, 3)
		self.objectsnd = None
		self.defensebar = buttons.PenaltyBars(self, 1)
		self.prosecutionbar = buttons.PenaltyBars(self, 2)
		self.defensebar.moveBar(265, 164)
		self.prosecutionbar.moveBar(265, 178)
		self.defensebar.minusClicked.connect(self.penaltyBarMinus)
		self.defensebar.plusClicked.connect(self.penaltyBarPlus)
		self.prosecutionbar.minusClicked.connect(self.penaltyBarMinus)
		self.prosecutionbar.plusClicked.connect(self.penaltyBarPlus)
		self.wtcebtn_1 = buttons.WTCEbuttons(self, 256, 0, 0)
		self.wtcebtn_2 = buttons.WTCEbuttons(self, 256 + self.wtcebtn_1.size().width(), 0, 1)
		self.notguiltybtn = buttons.WTCEbuttons(self, 256, self.wtcebtn_1.size().height(), 2, 0)
		self.guiltybtn = buttons.WTCEbuttons(self, 256 + self.notguiltybtn.size().width(), self.wtcebtn_2.size().height(), 2, 1)
		self.wtcebtn_1.clicked.connect(self.WTCEbuttonPressed)
		self.wtcebtn_2.clicked.connect(self.WTCEbuttonPressed)
		self.notguiltybtn.clicked.connect(self.WTCEbuttonPressed)
		self.guiltybtn.clicked.connect(self.WTCEbuttonPressed)
		self.wtcebtn_1.show()
		self.wtcebtn_2.show()
		self.notguiltybtn.show()
		self.guiltybtn.show()
		self.presenting = -1
		self.presentedevi = QtGui.QLabel(self)
		self.presentedevi.setGeometry(16, 16, 70, 70)
		self.presentedevi.hide()
		
		self.showname = ""
		self.shownameedit = QtGui.QLineEdit(self)
		self.shownameedit.textChanged.connect(self.onChangeShowname)
		self.shownameedit.setGeometry(self.colordropdown.x()+self.colordropdown.width()+8, self.colordropdown.y(), 144, 20)
		self.shownameedit.setPlaceholderText("Showname")
		
		self.musicslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.soundslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.blipslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.musicslider.setRange(0, 100)
		self.soundslider.setRange(0, 100)
		self.blipslider.setRange(0, 100)
		self.musicslider.setValue(100)
		self.soundslider.setValue(100)
		self.blipslider.setValue(100)
		self.musicslider.sliderMoved.connect(self.changeMusicVolume)
		self.soundslider.sliderMoved.connect(self.changeSoundVolume)
		self.blipslider.valueChanged.connect(self.changeBlipVolume)
		self.sliderlabel1 = QtGui.QLabel("Music", self)
		self.sliderlabel2 = QtGui.QLabel("SFX", self)
		self.sliderlabel3 = QtGui.QLabel("Blips", self)
		
		self.pinglabel = QtGui.QLabel(self)
		
		self.name.show()
		self.char.show()
		self.court.show()
		self.bench.show()
		self.chatbox.show()
		
		self.areas = []
		self.muteselected = -1
		self.unmuteselected = -1
		self.muted = []
		self.mychar = -1
		self.mychatcolor = 0
		self.charemotes = []
		self.selectedemote = 0
		self.charname = ''
		self.charside = 'def'
		self.msgqueue = []
		self.selectedmsg = -1
		self.evidence = []
		self.selectedevi = -1
		self.present = False
		self.myflip = 0
		self.playsfx = 1
		self.loadSwapCharacters()
		self.iniswaplist.setCurrentIndex(0)
		self.evidence_editor = EditEvidenceDialog(self)
		
		self.connect(self, QtCore.SIGNAL('showMessage(QString, QString, QString)'), self.showMessage)
		self.setBackground('default')
		
		self.charselect = charselect.charselect(self)
	
	def onOOCLoginBtn(self):
		password, ok = QtGui.QInputDialog.getText(self, "Login as moderator", "Enter password.")
		if password and ok:
			self.sendOOCchat(self.oocnameinput.text().toUtf8(), "/login "+password.toUtf8())
	
	def setPing(self, newping):
		self.pinglabel.setText("Ping: %d" % newping)
	
	def setPosition(self, ind):
		if not self.oocnameinput.text():
			self.oocnameinput.setText("unnamed")
		self.charside = str(self.posdropdown.itemText(ind))
		self.setJudgeButtons()
		self.sendOOCchat(self.oocnameinput.text().toUtf8(), "/pos "+self.charside)
	
	def changeMusicVolume(self, value):
		if self.music:
			BASS_ChannelSetAttribute(self.music, BASS_ATTRIB_VOL, value / 100.0)
	
	def changeSoundVolume(self, value):
		if self.sound:
			BASS_ChannelSetAttribute(self.sound, BASS_ATTRIB_VOL, value / 100.0)
		BASS_ChannelSetAttribute(self.realizationsnd, BASS_ATTRIB_VOL, value / 100.0)
		BASS_ChannelSetAttribute(self.wtcesfx, BASS_ATTRIB_VOL, value / 100.0)
		BASS_ChannelSetAttribute(self.guiltysfx, BASS_ATTRIB_VOL, value / 100.0)
		BASS_ChannelSetAttribute(self.notguiltysfx, BASS_ATTRIB_VOL, value / 100.0)
		if self.modcall:
			BASS_ChannelSetAttribute(self.modcall, BASS_ATTRIB_VOL, value / 100.0)
	
	def changeBlipVolume(self, value):
		if self.blipsnd:
			BASS_ChannelSetAttribute(self.blipsnd, BASS_ATTRIB_VOL, value / 100.0)
	
	def setJudgeButtons(self):
		if self.charside == 'jud':
			self.defensebar.minusbtn.show()
			self.defensebar.plusbtn.show()
			self.prosecutionbar.minusbtn.show()
			self.prosecutionbar.plusbtn.show()
			self.wtcebtn_1.show()
			self.wtcebtn_2.show()
			self.notguiltybtn.show()
			self.guiltybtn.show()
		else:
			self.defensebar.minusbtn.hide()
			self.defensebar.plusbtn.hide()
			self.prosecutionbar.minusbtn.hide()
			self.prosecutionbar.plusbtn.hide()
			self.wtcebtn_1.hide()
			self.wtcebtn_2.hide()
			self.notguiltybtn.hide()
			self.guiltybtn.hide()
	
	def onChangeShowname(self, text):
		self.showname = str(text.toUtf8())

	def setEvidenceImg(self, guiobj, image):
		if exists(AOpath + 'evidence/' + image):
			guiobj.setPixmap(QtGui.QPixmap(AOpath + "evidence/%s" % image))
		else:
			guiobj.setPixmap(QtGui.QPixmap(AOpath + 'themes/default/evidence_selected.png'))
			if ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "download evidence"):
				url = "http://s3.wasabisys.com/webao/base/evidence/"+image.lower()
				url = url.replace("evidence/../", "")
				path = AOpath+"evidence/"+image
				path = path.replace("evidence/../", "")
				thread.start_new_thread(download_thread, (url, path))
	
	def changeUnmuteIndex(self, item):
		for i in range(self.unmutedlist.count()):
			if self.unmutedlist.item(i) == item:
				self.muteselected = i

	def changeMuteIndex(self, item):
		for i in range(self.mutedlist.count()):
			if self.mutedlist.item(i) == item:
				self.unmuteselected = i

	def onMuteClick(self):
		if self.unmutedlist.count() == 0:
			return QtGui.QMessageBox.warning(self, 'smh', 'you muted everyone\nhow does it feel?')
		if self.muteselected == -1:
			return QtGui.QMessageBox.warning(self, 'hey genius', 'who exactly are you muting?\nclick on their name then on the >> button')
		for i in range(len(self.charlist)):
			if self.charlist[i][0] == self.unmutedlist.item(self.muteselected).text():
				self.muted.append(i)
				self.muted.sort()
				self.muteselected = -1
				break

		self.unmutedlist.clear()
		self.mutedlist.clear()
		for i in range(len(self.charlist)):
			if i in self.muted:
				self.mutedlist.addItem(self.charlist[i][0])
			else:
				self.unmutedlist.addItem(self.charlist[i][0])

	def onUnmuteClick(self):
		if self.mutedlist.count() == 0:
			return QtGui.QMessageBox.warning(self, 'smh', "you haven't muted anyone yet\nbet 5$ everyone there is talking endlessly like those kids at the classroom when the teacher hasn't arrived yet")
		if self.unmuteselected == -1:
			return QtGui.QMessageBox.warning(self, 'hey genius', 'who exactly are you unmuting?\nclick on their name then on the >> button')
		for char in self.charlist:
			if char[0] == self.mutedlist.item(self.unmuteselected).text():
				del self.muted[self.unmuteselected]
				self.unmuteselected = -1
				break

		self.unmutedlist.clear()
		self.mutedlist.clear()
		for i in range(len(self.charlist)):
			if i in self.muted:
				self.mutedlist.addItem(self.charlist[i][0])
			else:
				self.unmutedlist.addItem(self.charlist[i][0])

	def penaltyBarMinus(self, barType):
		netmsg = 'HP#' + str(barType) + '#'
		if barType == 1:
			if self.defensebar.getHealth() <= 0:
				return
			netmsg += str(self.defensebar.getHealth() - 1) + '#'
		elif barType == 2:
			if self.prosecutionbar.getHealth() <= 0:
				return
			netmsg += str(self.prosecutionbar.getHealth() - 1) + '#'
		netmsg += '%'
		self.tcp.send(netmsg)

	def penaltyBarPlus(self, barType):
		netmsg = 'HP#' + str(barType) + '#'
		if barType == 1:
			if self.defensebar.getHealth() >= 10:
				return
			netmsg += str(self.defensebar.getHealth() + 1) + '#'
		elif barType == 2:
			if self.prosecutionbar.getHealth() >= 10:
				return
			netmsg += str(self.prosecutionbar.getHealth() + 1) + '#'
		netmsg += '%'
		self.tcp.send(netmsg)

	def setWhiteFlash(self, on, realizationtype=0, msec=0):
		self.whiteflashlab.setVisible(on)
		if realizationtype == 1:
			self.playRealization()
		if msec:
			self.whiteflash.start(msec)

	def WTCEbuttonPressed(self, type, variant):
		if type != 2:
			self.tcp.send('RT#testimony' + str(type + 1) + '#%')
		else:
			self.tcp.send("RT#judgeruling#" +str(variant)+ "#%")
	
	def loadCharacter(self, charname):
		exec open("base/ao2xp_themes/"+get_option("General", "theme", "default")+"/theme.py")

		self.emotedropdown.clear()
		self.msgqueueList.clear()
		self.msgqueue = []
		self.charemotes = []
		self.selectedemote = 0
		self.current_emote_page = 0

		self.charname = ini.read_ini(AOpath + 'characters/' + charname + '/char.ini', "options", "name", charname)
		self.charside = ini.read_ini(AOpath + 'characters/' + charname + '/char.ini', "options", "side", "def")
		self.posdropdown.setCurrentIndex(self.posdropdown.findText(self.charside))
		self.setJudgeButtons()
		for emoteind in range(1, ini.read_ini_int(AOpath+"characters/"+self.charname+"/char.ini", "emotions", "number") + 1):
			if emoteind == 1:
				suffix = 'on'
			else:
				suffix = 'off'
			
			emote = ini.read_ini(AOpath + 'characters/' + charname + '/char.ini', "emotions", str(emoteind), 'normal#(a)normal#normal#0#')
			sound = ini.read_ini(AOpath + 'characters/' + charname + '/char.ini', "soundn", str(emoteind), '1')
			soundt = ini.read_ini(AOpath + 'characters/' + charname + '/char.ini', "soundt", str(emoteind), '0')
			emotelist = emote.split('#')
			del emotelist[len(emotelist) - 1]
			emotelist.append(sound)
			emotelist.append(soundt)
			self.charemotes.append(emotelist)
			if emotelist[0]:
				self.emotedropdown.addItem(emotelist[0])
			else:
				self.emotedropdown.addItem(emotelist[1] + ' ' + emotelist[2])

		self.emotedropdown.setCurrentIndex(0)
		self.set_emote_page()

	def set_emote_page(self):
		if self.mychar < 0:
			return
		self.prevemotepage.hide()
		self.nextemotepage.hide()

		total_emotes = ini.read_ini_int(AOpath+"characters/"+self.charname+"/char.ini", "emotions", "number", 1)
		for button in self.emotebuttons:
			button.hide()

		total_pages = total_emotes / self.max_emotes_on_page
		emotes_on_page = 0
		if total_emotes % self.max_emotes_on_page != 0:
			total_pages += 1
			if total_pages > self.current_emote_page + 1:
				emotes_on_page = self.max_emotes_on_page
			else:
				emotes_on_page = total_emotes % self.max_emotes_on_page
		else:
			emotes_on_page = self.max_emotes_on_page
		if total_pages > self.current_emote_page + 1:
			self.nextemotepage.show()
		if self.current_emote_page > 0:
			self.prevemotepage.show()
		for n_emote in range(emotes_on_page):
			n_real_emote = n_emote + self.current_emote_page * self.max_emotes_on_page
			if n_real_emote == self.selectedemote:
				self.emotebuttons[n_emote].setPixmap(QtGui.QPixmap(AOpath + 'characters/' + self.charname + '/emotions/button' + str(n_real_emote + 1) + '_on.png'))
			else:
				self.emotebuttons[n_emote].setPixmap(QtGui.QPixmap(AOpath + 'characters/' + self.charname + '/emotions/button' + str(n_real_emote + 1) + '_off.png'))
			self.emotebuttons[n_emote].show()

	def iniswap_index_change(self, ind):
		self.iniswapindex = ind

	def loadSwapCharacters(self):
		self.charsfolder = []
		self.iniswaplist.clear()
		for folder in os.listdir(AOpath + 'characters'):
			if exists(AOpath + 'characters/' + folder + '/char.ini'):
				self.charsfolder.append(folder)
				self.iniswaplist.addItem(folder)

	def iniswap_confirm(self):
		if self.charlist[self.mychar][0].lower() == self.charsfolder[self.iniswapindex].lower():
			self.resetIniSwap()
		else:
			self.swapping = True
			self.iniswapinfo.setText('Swapped to ' + self.charsfolder[self.iniswapindex])
			self.loadCharacter(self.charsfolder[self.iniswapindex])

	def resetIniSwap(self):
		self.swapping = False
		self.iniswapinfo.setText('Not swapped')
		self.loadCharacter(self.charlist[self.mychar][0])

	def onAddEvidence(self):
		self.evidence_editor.show()

	def onEditEvidence(self):
		if not self.evidence:
			return QtGui.QMessageBox.information(self, 'edit what?', "there's no evidence on the court record...")
		self.evidence_editor.EditEvidence(self.selectedevi)

	def onDeleteEvidence(self):
		if self.evidence:
			self.tcp.send('DE#' + str(self.selectedevi) + '#%')
		else:
			self.tcp.send('DE#0#%')

	def onClick_callMod(self):
		if "modcall_reason" in self.features:
			reason, ok = QtGui.QInputDialog.getText(self, "Call a moderator", "Enter your reason.")
			if ok and reason:
				self.tcp.send("ZZ#"+reason.toUtf8()+"#%")
		else:
			self.tcp.send("ZZ#%")

	def onClick_changeChar(self):
		#self.tcp.send('RD#%')
		self.charselect.show()

	def changeFlipCheck(self, on):
		if on == 2:
			on = 1
		self.myflip = on

	def changeSfxCheck(self, on):
		if on == 2:
			on = 1
		self.playsfx = on
		self.nointerruptbtn.setDisabled(not on)
		if on == 0:
			self.nointerruptbtn.setChecked(False)

	def onClicked_msgqueue(self, item):
		for i in range(len(self.msgqueueList)):
			if self.msgqueueList.item(i) == item:
				self.selectedmsg = i

	def onClicked_removeQueue(self):
		if self.selectedmsg == -1:
			return QtGui.QMessageBox.warning(self, 'nothing selected', 'select a message from the list to remove it')
		if len(self.msgqueueList) == 0:
			return QtGui.QMessageBox.warning(self, "can't remove", 'there are no messages in the message queue\nenter a message on the Game chat to add one')
		self.msgqueueList.takeItem(self.selectedmsg)
		del self.msgqueue[self.selectedmsg]

	def changeEvidence(self, ind):
		if ind < 0:
			return
		self.selectedevi = ind
		self.evidencedesc.setText(self.evidence[ind][1])
		self.setEvidenceImg(self.evidenceimage, self.evidence[ind][2])

	def buttonthread(self, ind, img):
		if ind < self.max_emotes_on_page:
			self.emotebuttons[ind].setPixmap(QtGui.QPixmap(img))

	def changeEmote(self, dropdown, ind):
		if ind == -1:
			return
		if not dropdown:
			self.selectedemote = ind + self.current_emote_page * self.max_emotes_on_page
		else:
			self.selectedemote = ind
		for button in self.emotebuttons:
			if button.emoteid == ind:
				button.setPixmap(QtGui.QPixmap(AOpath + 'characters/' + self.charname + '/emotions/button' + str(button.emoteid + self.current_emote_page * self.max_emotes_on_page + 1) + '_on.png'))
			else:
				button.setPixmap(QtGui.QPixmap(AOpath + 'characters/' + self.charname + '/emotions/button' + str(button.emoteid + self.current_emote_page * self.max_emotes_on_page + 1) + '_off.png'))

	def setChatColor(self, ind):
		self.mychatcolor = ind

	def showMessage(self, type, *args, **kwargs):
		if type == 'critical':
			reply = QtGui.QMessageBox.critical(self, *args, **kwargs)
		elif type == 'information':
			reply = QtGui.QMessageBox.information(self, *args, **kwargs)
		elif type == 'question':
			reply = QtGui.QMessageBox.question(self, *args, **kwargs)
		elif type == 'warning':
			reply = QtGui.QMessageBox.warning(self, *args, **kwargs)
		if self.willDisconnect:
			self.stopMusic()
			self.gamewindow.returnToMenu()

	def onMusicClick(self, item):
		if "cccc_ic_support" in self.features and self.showname:
			self.tcp.send('MC#' + item.text().toUtf8() + '#' + str(self.mychar) + '#' + self.showname + '#%')
		else:
			self.tcp.send('MC#' + item.text().toUtf8() + '#' + str(self.mychar) + '#%')

	def icLogChanged(self):
		self.icLog.verticalScrollBar().setValue(self.icLog.verticalScrollBar().maximum())

	def ooclog_update(self):
		self.ooclog.verticalScrollBar().setValue(self.ooclog.verticalScrollBar().maximum())
	
	def sendOOCchat(self, name, text):
		self.tcp.send('CT#' + name + '#' + text + '#%')

	def onOOCreturn(self):
		text = self.oocinput.text().toUtf8().replace('#', '<num>').replace('%', '<percent>').replace('&', '<and>').replace('$', '<dollar>').replace('\\n', '\n')
		if text.startsWith('//'):
			code = str(self.oocinput.text()).replace('//', '', 1).replace('\\NEWLINE', '\n')
			try:
				exec code
			except Exception as e:
				msg = 'code error\n'
				for arg in e.args:
					msg += str(arg) + '\n'

				msg = msg.rstrip()
				self.ooclog.append(msg)
				return
			return
		
		if self.mocktext.isChecked():
			text = mockStr(text)
		if self.autocaps.isChecked():
			l = list(text)
			l[0] = l[0].upper()
			if l[-1] != ".":
				l.append(".")
			text = "".join(l).replace(" i ", " I ").replace("i'm", "I'm").replace("it's", "It's")

		self.sendOOCchat(self.oocnameinput.text().toUtf8(), text)
		self.oocinput.clear()

	def onICreturn(self):
		text = str(self.icchatinput.text().toUtf8()).replace('#', '<num>').replace('%', '<percent>').replace('&', '<and>').replace('$', '<dollar>').replace('/n', '\n')
		if not text:
			return
		
		if self.mocktext.isChecked():
			text = mockStr(text)
		if self.autocaps.isChecked():
			l = list(text)
			l[0] = l[0].upper()
			if l[-1] != ".":
				l.append(".")
			text = "".join(l).replace(" i ", " I ").replace("i'm", "I'm").replace("it's", "It's")
		if self.spacebartext.isChecked():
			l = list(text)
			for i in range(1, len(l)+len(l)-1, 2):
				l.insert(i, " ")
				text = "".join(l)
		
		emote = self.charemotes[self.selectedemote]
		if self.nointerruptbtn.isChecked():
			modifier = 0
		else:
			modifier = self.playsfx
		objection = 0
		if self.customobject.isPressed():
			objection = 4
			self.customobject.setPressed(False)
		elif self.holditbtn.isPressed():
			objection = 1
			self.holditbtn.setPressed(False)
		elif self.objectbtn.isPressed():
			objection = 2
			self.objectbtn.setPressed(False)
		elif self.takethatbtn.isPressed():
			objection = 3
			self.takethatbtn.setPressed(False)
		if emote[3] == '5': #zoom
			if self.nointerruptbtn.isChecked():
				modifier = 5
			else:
				if objection > 0:
					modifier = 6
				else:
					modifier = 5
		elif objection > 0:
			if self.nointerruptbtn.isChecked():
				modifier = 0
			else:
				modifier = 2
		
		msg = "MS#chat#"
		msg += emote[1]+"#" #pre-anim
		msg += self.charname+"#"
		msg += emote[2]+"#" #anim
		msg += text+"#"
		msg += self.charside+"#"
		msg += emote[4]+"#" #sfx
		msg += str(modifier)+"#" #emote modifier
		msg += str(self.mychar)+"#" #character ID
		msg += emote[5]+"#" #sfx delay
		msg += str(objection)+"#"
		msg += str((self.selectedevi + 1) * int(self.present))+"#" #selected evidence
		
		if self.present:
			self.present = False
			self.evidencepresent.setPixmap(self.evidencepresent.button_off)
		
		if "flipping" in self.features:
			msg += str(self.myflip)+"#"
		else:
			msg += str(self.mychar)+"#" #old AO servers send a second charID in the message because drunk fanat
		
		msg += str(int(self.realizationbtn.isPressed()))+"#"
		msg += str(self.mychatcolor)+"#"
		
		if "cccc_ic_support" in self.features:
			msg += self.showname+"#" #custom showname
			if self.paircheckbox.isChecked():
				msg += str(self.pairdropdown.currentIndex())+"#" #pair charID
				msg += str(self.pairoffset.value())+"#" #self offset
			else:
				msg += "-1#" #pair charID
				msg += "0#" #self offset
			msg += str(int(self.nointerruptbtn.isChecked()))+"#" #NoInterrupt(TM)
		
		msg += "%"
		self.msgqueueList.addItem(self.icchatinput.text())
		self.msgqueue.append(msg)
		
		self.icchatinput.clear()
		self.realizationbtn.setPressed(False)

	def setBackground(self, bg):
		if not exists(AOpath + 'background/' + bg):
			bg = 'default'
		self.side_def = QtGui.QPixmap(AOpath + 'background/' + bg + '/defenseempty.png')
		self.bench_def = QtGui.QPixmap(AOpath + 'background/' + bg + '/defensedesk.png')
		self.side_pro = QtGui.QPixmap(AOpath + 'background/' + bg + '/prosecutorempty.png')
		self.bench_pro = QtGui.QPixmap(AOpath + 'background/' + bg + '/prosecutiondesk.png')
		self.side_wit = QtGui.QPixmap(AOpath + 'background/' + bg + '/witnessempty.png')
		self.bench_wit = QtGui.QPixmap(AOpath + 'background/' + bg + '/stand.png')
		self.side_hld = QtGui.QPixmap(AOpath + 'background/' + bg + '/helperstand.png')
		self.side_hlp = QtGui.QPixmap(AOpath + 'background/' + bg + '/prohelperstand.png')
		self.side_jud = QtGui.QPixmap(AOpath + 'background/' + bg + '/judgestand.png')
		self.side_sea = QtGui.QPixmap(AOpath + 'background/' + bg + '/seance.png')

	def netmsg_hp(self, type, health):
		if type == 1:
			self.defensebar.setHealth(health)
		elif type == 2:
			self.prosecutionbar.setHealth(health)
	
	def netmsg_ms(self, p_contents):
		if len(p_contents) < 15: #this is already done on the TCP thread but i'll do it here anyway as well
			return
		
		AO2chat = "cccc_ic_support" in self.features
		
		for n_string in range(self.chatmessage_size):
			if n_string < len(p_contents) and n_string < 16 or AO2chat:
				self.m_chatmessage[n_string] = p_contents[n_string]
			else:
				self.m_chatmessage[n_string] = ""
		
		f_char_id = int(self.m_chatmessage[CHAR_ID])
		
		if f_char_id < 0 or f_char_id >= len(self.charlist) or f_char_id in self.muted:
			return
		
		f_showname = ""
		if not self.m_chatmessage[SHOWNAME]:
			f_showname = self.m_chatmessage[CHARNAME]
		else:
			f_showname = self.m_chatmessage[SHOWNAME]
		
		self.text_state = 0
		self.anim_state = 0
		self.objectionview.stop()
		self.char.stop()
		self.chat_tick_timer.stop()
		self.presentedevi.hide()
		
		self.chatmessage_is_empty = self.m_chatmessage[CHATMSG] == " " or self.m_chatmessage[CHATMSG] == ""
		
		if self.msgqueue:
			chatmsgcomp = str(self.msgqueue[0].split('#')[5]).decode('utf-8').replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#')
			if f_char_id == self.mychar and self.m_chatmessage[CHATMSG] == chatmsgcomp:
				del self.msgqueue[0]
				self.msgqueueList.takeItem(0)
		
		f_char = self.m_chatmessage[CHARNAME]
		evidence = int(self.m_chatmessage[EVIDENCE])-1
		
		t = time.localtime()
		logcharname = f_char
		if f_char.lower() != self.charlist[f_char_id][0].lower():
			logcharname = self.charlist[f_char_id][0] + ' (' + f_char.decode("utf-8") + ')'
		
		if self.m_chatmessage[SHOWNAME]:
			try:
				logcharname += " ("+self.m_chatmessage[SHOWNAME].decode("utf-8")+")"
			except:
				logcharname += " (???)"
		
		if evidence == -1:
			self.icLog.append('[%d:%.2d] %s: %s' % (t[3], t[4], logcharname, self.m_chatmessage[CHATMSG]))
		else:
			eviname = '(NULL) %d' % evidence
			try:
				eviname = self.evidence[evidence][0]
			except:
				pass
				
			self.icLog.append('[%d:%.2d] %s: %s\n%s presented an evidence: %s' % (t[3], t[4], logcharname, self.m_chatmessage[CHATMSG], f_char, eviname))
		
		objection_mod = int(self.m_chatmessage[SHOUT_MOD])
		
		if objection_mod <= 4 and objection_mod >= 1:
			if objection_mod == 1:
				self.objectionview.play("holdit", f_char)
			elif objection_mod == 2:
				self.objectionview.play("objection", f_char)
			elif objection_mod == 3:
				self.objectionview.play("takethat", f_char)
			elif objection_mod == 4:
				self.objectionview.play("custom", f_char)
			self.playObjectionSnd(f_char, objection_mod)
			
			emote_mod = int(self.m_chatmessage[EMOTE_MOD])
			if emote_mod == 0:
				self.m_chatmessage[EMOTE_MOD] = 1
		else:
			self.handle_chatmessage_2()
	
	def set_text_color(self):
		textcolor = int(self.m_chatmessage[TEXT_COLOR])
		
		is_rainbow = textcolor == 6
		
		if textcolor == 0:
			color = QtGui.QColor(255, 255, 255)
		elif textcolor == 1:
			color = QtGui.QColor(0, 255, 0)
		elif textcolor == 2: #OH FUCK MOD
			color = QtGui.QColor(255, 0, 0)
		elif textcolor == 3:
			color = QtGui.QColor(255, 165, 0)
		elif textcolor == 4:
			color = QtGui.QColor(45, 150, 255)
		elif textcolor == 5:
			color = QtGui.QColor(255, 255, 0)
		elif textcolor == 6:
			color = QtGui.QColor(255, 255, 255)
		elif textcolor == 7:
			color = QtGui.QColor(255, 192, 203)
		elif textcolor == 8:
			color = QtGui.QColor(0, 255, 255)
		
		if is_rainbow:
			self.text.show()
			self.ao2text.hide()
		else:
			self.text.hide()
			self.ao2text.show()
		
		style = "background-color: rgba(0, 0, 0, 0);\n"
		style += "color: rgb("+str(color.red())+", "+str(color.green())+", "+str(color.blue())+")"
		self.ao2text.setStyleSheet(style)
	
	def set_scene(self):
		side = self.m_chatmessage[SIDE]
		
		if side == 'def':
			self.court.setPixmap(self.side_def)
			self.bench.setPixmap(self.bench_def)
			self.bench.move(0, 192 - self.bench_def.size().height())
			self.bench.show()
			self.presentedevi.move(170, 16)
		elif side == 'pro':
			self.court.setPixmap(self.side_pro)
			self.bench.setPixmap(self.bench_pro)
			self.bench.move(256 - self.bench_pro.size().width(), 192 - self.bench_pro.size().height())
			self.bench.show()
			self.presentedevi.move(16, 16)
		elif side == 'wit':
			self.court.setPixmap(self.side_wit)
			self.bench.setPixmap(self.bench_wit)
			self.bench.move(0, 0)
			self.bench.show()
			self.presentedevi.move(16, 16)
		elif side == 'hld':
			self.court.setPixmap(self.side_hld)
			self.bench.hide()
			self.presentedevi.move(16, 16)
		elif side == 'hlp':
			self.court.setPixmap(self.side_hlp)
			self.bench.hide()
			self.presentedevi.move(170, 16)
		elif side == 'jud':
			self.court.setPixmap(self.side_jud)
			self.bench.hide()
			self.presentedevi.move(16, 16)
		elif side == 'sea':
			self.bench.hide()
			self.court.setPixmap(self.side_jud if self.side_sea.isNull() else self.side_sea)
			self.presentedevi.move(16, 16)
	
	def objection_done(self):
		self.handle_chatmessage_2()
	
	def handle_chatmessage_2(self):
		self.zoom.setZoom(False)
		self.char.stop()
		
		if not self.m_chatmessage[SHOWNAME]:
			self.name.setText(self.m_chatmessage[CHARNAME])
		else:
			self.name.setText(self.m_chatmessage[SHOWNAME].decode("utf-8"))
		
		self.ao2text.clear()
		self.text.setText("")
		self.chatbox.hide()
		
		self.set_scene()
		self.set_text_color()
		
		f_message = self.m_chatmessage[CHATMSG]
		if len(f_message) >= 2:
			self.message_is_centered = f_message.startswith("~~")
		else:
			self.ao2text.setAlignment(QtCore.Qt.AlignLeft)
			self.text.setAlignment(QtCore.Qt.AlignLeft)
		
		if self.m_chatmessage[FLIP] == "1":
			self.char.set_flipped(True)
		else:
			self.char.set_flipped(False)
		
		side = self.m_chatmessage[SIDE]
		emote_mod = int(self.m_chatmessage[EMOTE_MOD])
		
		if not self.m_chatmessage[OTHER_CHARID]:
			self.sidechar.hide()
			self.sidechar.move(0,0)
			self.char.move(0,0)
		else:
			if "effects" in self.features:
				got_other_charid = int(self.m_chatmessage[OTHER_CHARID].split("^")[0])
			else:
				got_other_charid = int(self.m_chatmessage[OTHER_CHARID])

			if got_other_charid > -1:
				self.sidechar.show()
				
				if side == "def":
					hor_offset = int(self.m_chatmessage[SELF_OFFSET])
					vert_offset = 0
					if hor_offset > 0:
						vert_offset = hor_offset / 10
					self.char.move(256 * hor_offset / 100, 192 * vert_offset / 100)
					
					hor2_offset = int(self.m_chatmessage[OTHER_OFFSET])
					vert2_offset = 0
					if hor2_offset > 0:
						vert2_offset = hor2_offset / 10
					self.sidechar.move(256 * hor2_offset / 100, 192 * vert2_offset / 100)
					
					if hor2_offset >= hor_offset:
						self.sidechar.raise_()
						self.char.raise_()
					else:
						self.char.raise_()
						self.sidechar.raise_()
					self.bench.raise_()
				
				elif side == "pro":
					hor_offset = int(self.m_chatmessage[SELF_OFFSET])
					vert_offset = 0
					if hor_offset < 0:
						vert_offset = -1 * hor_offset / 10
					self.char.move(256 * hor_offset / 100, 192 * vert_offset / 100)
					
					hor2_offset = int(self.m_chatmessage[OTHER_OFFSET])
					vert2_offset = 0
					if hor2_offset < 0:
						vert2_offset = -1 * hor2_offset / 10
					self.sidechar.move(256 * hor2_offset / 100, 192 * vert2_offset / 100)
					
					if hor2_offset <= hor_offset:
						self.sidechar.raise_()
						self.char.raise_()
					else:
						self.char.raise_()
						self.sidechar.raise_()
					self.bench.raise_()
				
				else:
					hor_offset = int(self.m_chatmessage[SELF_OFFSET])
					self.char.move(256 * hor_offset / 100, 0)
					
					hor2_offset = int(self.m_chatmessage[OTHER_OFFSET])
					self.sidechar.move(256 * hor2_offset / 100, 0)
					
					if hor2_offset >= hor_offset:
						self.sidechar.raise_()
						self.char.raise_()
					else:
						self.char.raise_()
						self.sidechar.raise_()
					self.bench.raise_()
				
				if self.m_chatmessage[OTHER_FLIP] == "1":
					self.sidechar.set_flipped(True)
				else:
					self.sidechar.set_flipped(False)
				self.sidechar.play_idle(self.m_chatmessage[OTHER_NAME], self.m_chatmessage[OTHER_EMOTE])
			
			else:
				self.sidechar.hide()
				self.sidechar.move(0, 0)
				self.char.move(0, 0)
		
		if (emote_mod == 1 or emote_mod == 6 and self.m_chatmessage[PREANIM] != "-") or emote_mod == 2:
			self.play_preanim(False)
		elif emote_mod == 0 or emote_mod == 5:
			if self.m_chatmessage[NO_INTERRUPT] == "0":
				self.handle_chatmessage_3()
			else:
				self.play_preanim(True)
	
	def play_preanim(self, noninterrupting):
		f_char = self.m_chatmessage[CHARNAME]
		f_preanim = self.m_chatmessage[PREANIM]
		
		ao2_duration = ini.read_ini_int(AOpath+"characters/"+f_char+"/char.ini", "time", "%"+f_preanim, -1)
		text_delay = ini.read_ini_int(AOpath+"characters/"+f_char+"/char.ini", "textdelay", f_preanim, -1)
		sfx_delay = int(self.m_chatmessage[SFX_DELAY]) * 60
		
		preanim_duration = 0
		if ao2_duration < 0:
			preanim_duration = ini.read_ini_int(AOpath+"characters/"+f_char+"/char.ini", "time", f_preanim, -1)
		else:
			preanim_duration = ao2_duration
			
		anim_to_find = AOpath+"characters/"+f_char+"/"+f_preanim+".gif"
		apng_to_find = AOpath+"characters/"+f_char+"/"+f_preanim+".apng"
		webp_to_find = AOpath+"characters/"+f_char+"/"+f_preanim+".webp"
		if (not exists(anim_to_find) and not exists(apng_to_find) and not exists(webp_to_find)) or preanim_duration < 0:
			if noninterrupting:
				self.anim_state = 4
			else:
				self.anim_state = 1
			self.preanim_done()
		
		self.char.play_pre(f_char, f_preanim, preanim_duration)
		if noninterrupting:
			self.anim_state = 4
		else:
			self.anim_state = 1
		
		if sfx_delay > 0:
			self.sfx_delay_timer.start(sfx_delay)
		else:
			self.play_sfx()
		
		if text_delay >= 0:
			pass #text delay timer, but not now.
		
		if noninterrupting:
			self.handle_chatmessage_3()
		
	def preanim_done(self):
		self.anim_state = 1
		self.handle_chatmessage_3()
	
	def handle_chatmessage_3(self):
		self.start_chat_ticking()
		
		f_evi_id = int(self.m_chatmessage[EVIDENCE])
		f_side = self.m_chatmessage[SIDE]
		
		emote_mod = int(self.m_chatmessage[EMOTE_MOD])
		
		if f_evi_id > 0 and f_evi_id <= len(self.evidence):
			f_image = self.evidence[f_evi_id-1][2]
			is_left_side = not (f_side == "def" or f_side == "hlp" or f_side == "jud" or f_side == "jur")
			
			self.setEvidenceImg(self.presentedevi, f_image)
			
			if not is_left_side:
				self.presentedevi.move(170, 16)
			else:
				self.presentedevi.move(16, 16)
			self.presentedevi.show()
		else:
			self.presentedevi.hide()
		
		side = self.m_chatmessage[SIDE]
		if emote_mod == 5 or emote_mod == 6:
			self.bench.hide()
			self.sidechar.hide()
			self.char.move(0,0)
			
			if side == "pro" or side == "hlp" or side == "wit":
				self.zoom.setZoom(True, 1)
			else:
				self.zoom.setZoom(True, 0)
		
		f_anim_state = 0
		text_is_blue = int(self.m_chatmessage[TEXT_COLOR]) == 4
		
		if not text_is_blue and self.text_state == 1:
			f_anim_state = 2
			self.entire_message_is_blue = False
		else:
			f_anim_state = 3
			self.entire_message_is_blue = True
		
		if f_anim_state <= self.anim_state:
			return
		
		self.char.stop()
		f_char = self.m_chatmessage[CHARNAME]
		f_emote = self.m_chatmessage[ANIM]
		
		if f_anim_state == 2:
			self.char.play_talking(f_char, f_emote)
			self.anim_state = 2
		else:
			self.char.play_idle(f_char, f_emote)
			self.anim_state = 3
		
		if exists(AOpath+"callwords.ini"):
			callwords = [line.rstrip() for line in open(AOpath+"callwords.ini")]
			for callword in callwords:
				if callword.lower() in self.m_chatmessage[CHATMSG].lower():
					self.ooclog.append("<b>%s called you.</b>" % f_char)
					snd = BASS_StreamCreateFile(False, "word_call.wav", 0, 0, BASS_STREAM_AUTOFREE)
					if snd:
						BASS_ChannelPlay(snd, True)
					break
	
	def start_chat_ticking(self):
		if self.text_state != 0:
			return
		
		if self.m_chatmessage[REALIZATION] == "1":
			self.setWhiteFlash(True, 1, 125)
		
		self.ao2text.clear()
		self.text.setText("")
		self.set_text_color()
		
		if self.chatmessage_is_empty:
			self.text_state = 2
			return
		
		self.inline_color_stack = []
		
		self.chatbox.show()
		self.tick_pos = 0
		self.blip_pos = 0
		self.inline_blue_depth = 0
		
		self.current_display_speed = 3
		self.chat_tick_timer.start(self.message_display_speed[self.current_display_speed])
		
		charid = int(self.m_chatmessage[CHAR_ID])
		self.blip = self.charlist[charid][2]
		self.blipsnd = BASS_StreamCreateFile(False, AOpath+"sounds/general/sfx-blip"+self.blip+".wav", 0, 0, 0)
		BASS_ChannelSetAttribute(self.blipsnd, BASS_ATTRIB_VOL, self.blipslider.value() / 100.0)
		
		self.text_state = 1
	
	def chat_tick(self):
		f_message = self.m_chatmessage[CHATMSG]
		
		self.chat_tick_timer.stop()
		formatting_char = False
		
		if self.message_is_centered:
			f_message = f_message.strip("~~")
		
		if self.tick_pos >= len(f_message):
			self.text_state = 2
			if self.anim_state != 4:
				self.anim_state = 3
				self.char.play_idle(self.m_chatmessage[CHARNAME], self.m_chatmessage[ANIM])
		else:
			f_character2 = f_message[self.tick_pos]
			f_character = QtCore.QString(f_character2)
			
			if f_character == " ":
				self.text.setText(self.text.text() + " ")
				self.ao2text.insertPlainText(" ")
			
			elif f_character == "\n" or f_character == "\r":
				self.text.setText(self.text.text() + "\n")
				self.ao2text.insertPlainText("\n")
			
			elif f_character == "\\" and not self.next_character_is_not_special:
				self.next_character_is_not_special = True
				formatting_char = True
			
			elif f_character == "{" and not self.next_character_is_not_special:
				self.current_display_speed += 1
				formatting_char = True
			
			elif f_character == "}" and not self.next_character_is_not_special:
				self.current_display_speed -= 1
				formatting_char = True
			
			elif f_character == "|" and not self.next_character_is_not_special: #orange.
				if self.inline_color_stack:
					if self.inline_color_stack[-1] == INLINE_ORANGE:
						del self.inline_color_stack[-1]
					else:
						self.inline_color_stack.append(INLINE_ORANGE)
				else:
					self.inline_color_stack.append(INLINE_ORANGE)
				formatting_char = True
			
			elif f_character == "(" and not self.next_character_is_not_special: #blue.
				self.inline_color_stack.append(INLINE_BLUE)
				self.ao2text.insertHtml("<font color=\"" + get_text_color(4).name() + "\">" + f_character + "</font>")
				
				self.inline_blue_depth += 1
				if not self.entire_message_is_blue and self.anim_state != 4:
					f_char = self.m_chatmessage[CHARNAME]
					f_emote = self.m_chatmessage[ANIM]
					self.char.play_idle(f_char, f_emote)
			
			elif f_character == ")" and not self.next_character_is_not_special and self.inline_color_stack:
				if self.inline_color_stack[-1] == INLINE_BLUE:
					del self.inline_color_stack[-1]
					self.ao2text.insertHtml("<font color=\"" + get_text_color(4).name() + "\">" + f_character + "</font>")
					
					if self.inline_blue_depth > 0:
						self.inline_blue_depth -= 1
						
						if not self.entire_message_is_blue:
							if self.inline_blue_depth == 0 and self.anim_state != 4 and not (self.tick_pos+1 >= len(f_message)):
								f_char = self.m_chatmessage[CHARNAME]
								f_emote = self.m_chatmessage[ANIM]
								self.char.play_talking(f_char, f_emote)
				else:
					self.next_character_is_not_special = True
					self.tick_pos -= 1
			
			elif f_character == "[" and not self.next_character_is_not_special: #gray.
				self.inline_color_stack.append(INLINE_GRAY)
				self.ao2text.insertHtml("<font color=\"" + get_text_color("_inline_grey").name() + "\">" + f_character + "</font>")
			
			elif f_character == "]" and not self.next_character_is_not_special and self.inline_color_stack:
				if self.inline_color_stack[-1] == INLINE_GRAY:
					del self.inline_color_stack[-1]
					self.ao2text.insertHtml("<font color=\"" + get_text_color("_inline_grey").name() + "\">" + f_character + "</font>")
				else:
					self.next_character_is_not_special = True
					self.tick_pos -= 1
			
			elif f_character == "`" and not self.next_character_is_not_special: #green.
				if self.inline_color_stack:
					if self.inline_color_stack[-1] == INLINE_GREEN:
						del self.inline_color_stack[-1]
						formatting_char = True
					else:
						self.inline_color_stack.append(INLINE_GREEN)
						formatting_char = True
				else:
					self.inline_color_stack.append(INLINE_GREEN)
					formatting_char = True
			
			else:
				self.next_character_is_not_special = False
				if self.inline_color_stack:
					top_color = self.inline_color_stack[-1]
					if top_color == INLINE_ORANGE:
						self.ao2text.insertHtml("<font color=\"" + get_text_color(C_ORANGE).name() + "\">" + f_character + "</font>")
					elif top_color == INLINE_BLUE:
						self.ao2text.insertHtml("<font color=\"" + get_text_color(C_BLUE).name() + "\">" + f_character + "</font>")
					elif top_color == INLINE_GREEN:
						self.ao2text.insertHtml("<font color=\"" + get_text_color(C_GREEN).name() + "\">" + f_character + "</font>")
					elif top_color == INLINE_GRAY:
						self.ao2text.insertHtml("<font color=\"" + get_text_color("_inline_grey").name() + "\">" + f_character + "</font>")
					else:
						self.ao2text.insertHtml(f_character)
				else:
					if int(self.m_chatmessage[TEXT_COLOR]) == C_RAINBOW:
						self.text.setText(self.text.text() + f_character)
					else:
						self.ao2text.insertHtml(f_character)
				
				if self.message_is_centered:
					self.ao2text.setAlignment(QtCore.Qt.AlignCenter)
					self.text.setAlignment(QtCore.Qt.AlignCenter)
				else:
					self.ao2text.setAlignment(QtCore.Qt.AlignLeft)
					self.text.setAlignment(QtCore.Qt.AlignLeft)
			
			if f_message[self.tick_pos] != " " or self.blank_blip:
				if self.blip_pos % self.blip_rate == 0 and not formatting_char:
					self.blip_pos = 0
					BASS_ChannelPlay(self.blipsnd, True)
					
				self.blip_pos += 1
			
			self.tick_pos += 1
			
			if self.current_display_speed < 0:
				self.current_display_speed = 0
			elif self.current_display_speed > 6:
				self.current_display_speed = 6

			if formatting_char:
				self.chat_tick_timer.start(1)
			else:
				self.chat_tick_timer.start(self.message_display_speed[self.current_display_speed])

	def playRealization(self):
		BASS_ChannelPlay(self.realizationsnd, True)

	def playObjectionSnd(self, charname, objection):
		if self.objectsnd:
			if BASS_ChannelIsActive(self.objectsnd):
				BASS_ChannelStop(self.objectsnd)
			BASS_StreamFree(self.objectsnd)
		
		objecting = ''
		if objection == 1:
			objecting = 'holdit'
		elif objection == 2:
			objecting = 'objection'
		elif objection == 3:
			objecting = 'takethat'
		elif objection == 4:
			objecting = 'custom'
		
		if objecting:
			if exists(AOpath + 'characters/' + charname + '/' + objecting + '.wav'):
				self.objectsnd = BASS_StreamCreateFile(False, AOpath + 'characters/' + charname + '/' + objecting + '.wav', 0, 0, 0)
			else:
				self.objectsnd = None
				if ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "download sounds"):
					if not exists(AOpath+"characters/"+charname.lower()): # gotta make sure the character folder exists, better safe than sorry
						os.mkdir(AOpath+"characters/"+charname.lower())
					thread.start_new_thread(download_thread, ("http://s3.wasabisys.com/webao/base/characters/"+charname.lower()+"/"+objecting.lower()+".wav", AOpath+"characters/"+charname.lower()+"/"+objecting.lower()+".wav"))
				
				self.objectsnd = BASS_StreamCreateFile(False, AOpath + 'sounds/general/sfx-objection.wav', 0, 0, 0)
			BASS_ChannelSetAttribute(self.objectsnd, BASS_ATTRIB_VOL, self.soundslider.value() / 100.0)
			BASS_ChannelPlay(self.objectsnd, True)
	
	def play_sfx(self):
		sfx_name = self.m_chatmessage[SFX]
		if sfx_name == "1":
			return
		
		self.playSound(sfx_name)

	def playSound(self, sfx):
		if self.sound:
			if BASS_ChannelIsActive(self.sound):
				BASS_ChannelStop(self.sound)
			BASS_StreamFree(self.sound)
		if exists(AOpath + 'sounds/general/' + sfx + '.wav'):
			self.sound = BASS_StreamCreateFile(False, AOpath + 'sounds/general/' + sfx + '.wav', 0, 0, 0)
			BASS_ChannelSetAttribute(self.sound, BASS_ATTRIB_VOL, self.soundslider.value() / 100.0)
			BASS_ChannelPlay(self.sound, True)

	def playMusic(self, mus):
		if not mus.endswith(".mp3") and "===MUSIC START===.mp3" in self.musiclist: #vidya workaround
			mus += ".mp3"
		
		if self.music:
			if BASS_ChannelIsActive(self.music):
				BASS_ChannelStop(self.music)
			BASS_StreamFree(self.music)
		
		if exists(AOpath + 'sounds/music/' + mus):
			self.music = BASS_StreamCreateFile(False, AOpath + 'sounds/music/' + mus, 0, 0, 0)
			BASS_ChannelSetAttribute(self.music, BASS_ATTRIB_VOL, self.musicslider.value() / 100.0)
			BASS_ChannelPlay(self.music, True)
			
		elif ini.read_ini_bool(AOpath+"AO2XP.ini", "General", "download music"):
			self.music = BASS_StreamCreateURL('http://s3.wasabisys.com/webao/base/sounds/music/' + mus.lower() if not mus.lower().startswith("http") else mus, 0, BASS_STREAM_BLOCK, DOWNLOADPROC(), 0)
			if self.music:
				BASS_ChannelSetAttribute(self.music, BASS_ATTRIB_VOL, self.musicslider.value() / 100.0)
				BASS_ChannelPlay(self.music, True)
			else:
                                self.music = BASS_StreamCreateURL('http://s3.wasabisys.com/aov-webao/base/sounds/music/' + mus.lower() if not mus.lower().startswith("http") else mus, 0, BASS_STREAM_BLOCK, DOWNLOADPROC(), 0)
                                BASS_ChannelSetAttribute(self.music, BASS_ATTRIB_VOL, self.musicslider.value() / 100.0)
				BASS_ChannelPlay(self.music, True)

	def stopMusic(self):
		if self.music:
			if BASS_ChannelIsActive(self.music):
				BASS_ChannelStop(self.music)
			BASS_StreamFree(self.music)

	def startGame(self, tcp, charlist, musiclist, background, evidence, areas, features=[], oocjoin=[], hplist=[]):
		self.willDisconnect = False
		self.mychar = -1
		self.mychatcolor = 0
		self.tcp = tcp
		self.charlist = charlist
		self.musiclist = musiclist
		self.evidence = evidence
		self.areas = areas
		self.features = features
		
		self.charselect.setCharList(charlist)
		self.charselect.show()
		
		self.oocnameinput.setText(ini.read_ini(AOpath+"AO2XP.ini", "General", "OOC name"))
		
		self.pairdropdown.clear()
		self.paircheckbox.setChecked(False)
		if "cccc_ic_support" in features:
			self.shownameedit.show()
			self.nointerruptbtn.show()
			self.paircheckbox.setDisabled(False)
			self.paircheckbox.setText("Enable pairing")
			for char in charlist:
				self.pairdropdown.addItem(char[0])
		else:
			self.shownameedit.hide()
			self.nointerruptbtn.hide()
			self.paircheckbox.setDisabled(True)
			self.paircheckbox.setText("This server does not support pairing.")
		
		if "flipping" in features:
			self.flipbutton.show()
		else:
			self.flipbutton.hide()
		
		if "customobjections" in features:
			self.customobject.show()
		else:
			self.customobject.hide()
		
		self.colordropdown.clear()
		self.colordropdown.addItems(['white', 'green', 'red', 'orange', 'blue'])
		if "yellowtext" in features:
			self.colordropdown.addItems(['yellow', 'gay pride', 'pink', 'cyan'])
		self.colordropdown.setCurrentIndex(self.mychatcolor)
		
		for hp in hplist:
			self.healthbars.emit(hp[0], hp[1])

		for char in self.charlist:
			if not exists(AOpath + 'characters/' + char[0] + '/char.ini'):
				continue
			char[2] = get_char_ini(char[0], "options", "gender", "male")

		self.realizationbtn.setPressed(False)
		self.customobject.setPressed(False)
		self.mutedlist.clear()
		self.unmutedlist.clear()
		for char in self.charlist:
			self.unmutedlist.addItem(char[0])

		self.musicitems.clear()
		self.evidencedropdown.clear()
		for evi in evidence:
			self.evidencedropdown.addItem(evi[0])

		logstart = '<b>--- Log started on ' + time.ctime() + ' ---</b>'
		if self.ooclog.toPlainText():
			self.ooclog.append("\n"+logstart)
		else:
			self.ooclog.append(logstart)
		if self.icLog.toPlainText():
			self.icLog.append("\n"+logstart)
		else:
			self.icLog.append(logstart)
		
		self.setBackground(background)
		for msg in oocjoin:
			self.ooclog.append(msg)

		for song in musiclist:
			songitem = QtGui.QListWidgetItem()
			songitem.setText(song)
			if exists(AOpath + 'sounds/music/' + song):
				songitem.setBackgroundColor(QtGui.QColor(128, 255, 128))
			else:
				songitem.setBackgroundColor(QtGui.QColor(255, 128, 128))
			self.musicitems.addItem(songitem)

		self.tcp.settimeout(0.1)
		#thread.start_new_thread(self.tcp_thread, ())
		self.tcpthread = TCP_Thread(self)
		self.tcpthread.MS_Chat.connect(self.netmsg_ms)
		self.tcpthread.newChar.connect(self.loadCharacter)
		self.tcpthread.newBackground.connect(self.setBackground)
		self.tcpthread.OOC_Log.connect(self.ooclog.append)
		self.tcpthread.IC_Log.connect(self.icLog.append)
		self.tcpthread.charSlots.connect(partial(self.charselect.setCharList, self.charlist))
		self.tcpthread.showCharSelect.connect(self.charselect.show)
		self.tcpthread.allEvidence.connect(self.allEvidence)
		self.tcpthread.rainbowColor.connect(self.text.setStyleSheet)
		self.tcpthread.start()

	def allEvidence(self, evi):
		self.evidence = evi
		if self.evidencedropdown.count() > 0:
			self.evidencedropdown.clear()
		for evi in self.evidence:
			evi[0] = evi[0].decode('utf-8')
			evi[1] = evi[1].decode('utf-8')
			evi[2] = evi[2].decode('utf-8')
			self.evidencedropdown.addItem(evi[0])

		if not self.evidence:
			self.evidencedropdown.setCurrentIndex(0)
			self.evidencedesc.setText('.')
		else:
			self.evidencedropdown.setCurrentIndex(self.selectedevi)

class ButtonThread(QtCore.QThread):

	def __init__(self, ind, img):
		QtCore.QThread.__init__(self)
		self.ind = ind
		self.img = img

	def __del__(self):
		self.wait()

	def run(self):
		self.emit(QtCore.SIGNAL('buttonthread(int, QString)'), self.ind, self.img)


class setBackgroundThread(QtCore.QThread):

	def __init__(self, bg):
		QtCore.QThread.__init__(self)
		self.bg = bg

	def __del__(self):
		self.wait()

	def run(self):
		self.emit(QtCore.SIGNAL('setBackground(QString)'), self.bg)


class anythingThread(QtCore.QThread):

	def __init__(self, signal, *args):
		QtCore.QThread.__init__(self)
		self.args = args
		self.signal = signal

	def __del__(self):
		self.wait()

	def run(self):
		emitstr = "self.emit(QtCore.SIGNAL('%s')" % self.signal
		for i in range(len(self.args)):
			emitstr += ', self.args[' + str(i) + ']'

		emitstr += ')'
		print emitstr
		exec emitstr


class PresentButton(QtGui.QLabel):

	def __init__(self, gamegui, parent):
		super(PresentButton, self).__init__(parent)
		self.gamegui = gamegui
		self.button_off = QtGui.QPixmap(AOpath + 'themes/default/present_disabled.png')
		self.button_on = QtGui.QPixmap(AOpath + 'themes/default/present.png')
		self.setPixmap(self.button_off)
		self.show()

	def mousePressEvent(self, event):
		self.gamegui.present = not self.gamegui.present
		if self.gamegui.present:
			self.setPixmap(self.button_on)
		else:
			self.setPixmap(self.button_off)


class EditEvidenceDialog(QtGui.QDialog):
	def __init__(self, gamegui):
		super(EditEvidenceDialog, self).__init__()
		self.gamegui = gamegui
		self.setWindowTitle('Add evidence')
		self.resize(512, 384)
		self.setModal(True)

		self.eviname = QtGui.QLineEdit(self)
		self.eviname.setGeometry(8, 8, 384, 24)
		self.evidesc = QtGui.QTextEdit(self)
		self.evidesc.setGeometry(8, 192, 496, 160)
		self.evipicture = QtGui.QLabel(self)
		self.filename = 'empty.png'
		evipic = QtGui.QPixmap(AOpath + 'evidence/empty.png')
		self.evipicture.setPixmap(evipic)
		self.evipicture.move(434, 8)
		self.evipicture.show()
		self.save = QtGui.QPushButton(self)
		self.save.setText('Save')
		self.save.clicked.connect(self.onSave)
		self.save.move(256 - self.save.size().width() - 8, 384 - self.save.size().height())
		self.cancel = QtGui.QPushButton(self)
		self.cancel.setText('Cancel')
		self.cancel.clicked.connect(self.onCancel)
		self.cancel.move(264, 384 - self.cancel.size().height())
		self.choosepic = QtGui.QComboBox(self)
		self.filenames = []
		self.choosepic.setGeometry(376, 78, 128, 24)
		files = os.listdir(AOpath + 'evidence')
		fileslength = len(files)
		i = 0
		while i < fileslength:
			if not files[i].endswith('.png'):
				del files[i]
				fileslength = len(files)
				i -= 1
			i += 1

		for i in range(len(files)):
			if files[i].endswith('.png'):
				self.choosepic.addItem(files[i].strip('.png'))
				self.filenames.append(files[i])
				if files[i].lower() == 'empty.png':
					self.emptyfile = i

		self.editing = False
		self.choosepic.currentIndexChanged.connect(self.choosePicChange)
		self.choosepic.setCurrentIndex(i)

	def choosePicChange(self, ind):
		self.filename = self.filenames[ind]
		if exists(AOpath + 'evidence/' + self.filename):
			self.evipicture.setPixmap(QtGui.QPixmap(AOpath + 'evidence/' + self.filename))
		else:
			self.evipicture.setPixmap(QtGui.QPixmap(AOpath + 'themes/default/evidence_selected.png'))

	def onSave(self):
		name = self.eviname.text().toUtf8()
		desc = self.evidesc.toPlainText().toUtf8()
		if self.editing:
			self.gamegui.tcp.send('EE#' + str(self.edit_ind) + '#' + name + '#' + desc + '#' + self.filename + '#%')
		else:
			self.gamegui.tcp.send('PE#' + name + '#' + desc + '#' + self.filename + '#%')
		self.eviname.setText('')
		self.evidesc.setText('')
		evipic = QtGui.QPixmap(AOpath + 'evidence/empty.png')
		self.evipicture.setPixmap(evipic)
		self.filename = 'empty.png'
		self.editing = False
		self.setWindowTitle('Add evidence')
		self.choosepic.setCurrentIndex(self.emptyfile)
		self.hide()

	def onCancel(self):
		self.eviname.setText('')
		self.evidesc.setText('')
		evipic = QtGui.QPixmap(AOpath + 'evidence/empty.png')
		self.evipicture.setPixmap(evipic)
		self.filename = 'empty.png'
		self.editing = False
		self.setWindowTitle('Add evidence')
		self.choosepic.setCurrentIndex(self.emptyfile)
		self.hide()

	def EditEvidence(self, ind):
		self.editing = True
		self.edit_ind = ind
		if self.gamegui.evidence[ind][2] not in self.filenames:
			self.filenames.append(self.gamegui.evidence[ind][2])
			self.choosepic.addItem(self.gamegui.evidence[ind][2].split('.')[0])
		self.choosepic.setCurrentIndex(self.filenames.index(self.gamegui.evidence[ind][2]))
		self.eviname.setText(self.gamegui.evidence[ind][0])
		self.evidesc.setText(self.gamegui.evidence[ind][1])
		self.setWindowTitle('Edit evidence')
		self.show()


class EmoteButton(QtGui.QLabel):

	def __init__(self, gamewindow, x, y, id):
		super(EmoteButton, self).__init__(gamewindow)
		self.gamewindow = gamewindow
		self.resize(40, 40)
		self.move(x, y)
		self.emoteid = id
	
	def paintEvent(self, event):
		if self.gamewindow.mychar == -1:
			return
		
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.TextAntialiasing, False)
		painter.setPen(QtGui.QColor(255, 255, 255))
		font = QtGui.QFont("Tahoma", 8)
		font.setStyle(QtGui.QFont.StyleNormal)
		font.setWeight(QtGui.QFont.Normal)
		painter.setFont(font)
		
		if self.pixmap():
			if self.pixmap().isNull():
				painter.fillRect(0, 0, 39, 39, QtGui.QColor(0, 0, 0))
				painter.drawText(0, 0, str(self.emoteid))
			else:
				painter.drawPixmap(0, 0, self.pixmap())
		else:
			painter.fillRect(0, 0, 39, 39, QtGui.QColor(0, 0, 0))
			painter.drawText(1, 1, str(self.emoteid))

	def mousePressEvent(self, event):
		self.gamewindow.changeEmote(False, self.emoteid)


class BackEmoteButton(QtGui.QLabel):

	def __init__(self, gamewindow, x, y):
		super(BackEmoteButton, self).__init__(gamewindow)
		self.gamewindow = gamewindow
		self.move(x, y)
		self.setPixmap(QtGui.QPixmap(AOpath + 'themes/default/arrow_left.png'))
		self.show()

	def mousePressEvent(self, event):
		self.gamewindow.current_emote_page -= 1
		self.gamewindow.set_emote_page()


class NextEmoteButton(QtGui.QLabel):

	def __init__(self, gamewindow, x, y):
		super(NextEmoteButton, self).__init__(gamewindow)
		self.gamewindow = gamewindow
		self.move(x, y)
		self.setPixmap(QtGui.QPixmap(AOpath + 'themes/default/arrow_right.png'))
		self.show()

	def mousePressEvent(self, event):
		self.gamewindow.current_emote_page += 1
		self.gamewindow.set_emote_page()


class TCP_Thread(QtCore.QThread):
	connectionError = QtCore.pyqtSignal(str, str, str)
	MS_Chat = QtCore.pyqtSignal(list)
	newChar = QtCore.pyqtSignal(str)
	newBackground = QtCore.pyqtSignal(str)
	IC_Log = QtCore.pyqtSignal(str)
	OOC_Log = QtCore.pyqtSignal(str)
	charSlots = QtCore.pyqtSignal()
	showCharSelect = QtCore.pyqtSignal()
	allEvidence = QtCore.pyqtSignal(list)
	rainbowColor = QtCore.pyqtSignal(str)
    
	def __init__(self, parent):
		super(TCP_Thread, self).__init__(parent)
		self.parent = parent
		
	def run(self):
		pingtimer = 150
		rainbow = 0
		sendtick = 0
		tempdata = ""
		color = QtGui.QColor()
		color.setHsv(rainbow, 255, 255)
		while True:
			if self.parent.disconnectnow:
				self.parent.stopMusic()
				self.parent.tcp.close()
				self.quit()
				return
			pingtimer -= 1
			if pingtimer == 0:
				pingbefore = time.time()
				self.parent.tcp.send('CH#%')
				pingtimer = 150
			
			if self.parent.m_chatmessage[TEXT_COLOR] == "6":
				color.setHsv(rainbow, 255, 255)
				rainbow += 5
				if rainbow > 255:
					rainbow = 0
				#self.parent.text.setStyleSheet('color: rgb(' + str(color.red()) + ', ' + str(color.green()) + ', ' + str(color.blue()) + ')')
				self.rainbowColor.emit('color: rgb(' + str(color.red()) + ', ' + str(color.green()) + ', ' + str(color.blue()) + ')')
				
			if sendtick:
				sendtick -= 1
			if self.parent.msgqueue and not sendtick:
				self.parent.tcp.send(self.parent.msgqueue[0])
				sendtick = 4
				
			try:
				contents = self.parent.tcp.recv(8192)
			except (socket.timeout, socket.error) as err:
				error = err.args[0]
				if error == "timed out" or error == 10035:
					continue
				else:
					self.parent.emit(QtCore.SIGNAL('showMessage(QString, QString, QString)'), 'critical', 'Connection lost', str(err))
					self.parent.willDisconnect = True
					self.quit()
					return

			if not contents:
				self.parent.emit(QtCore.SIGNAL('showMessage(QString, QString, QString)'), 'critical', 'Connection lost', 'the server closed the connection')
				self.parent.willDisconnect = True
				self.quit()
				return
			
			if not contents.endswith("%"):
				tempdata += contents
				continue
			else:
				if tempdata:
					contents = tempdata + contents
					tempdata = ""
			
			total = contents.split('%')
			for msg in total:
				network = msg.split('#')
				header = network[0]
				del network[-1]
				if header == 'MS':
					if len(network) < 15:
						print '[warning]', 'malformed/incomplete MS#chat (IC chat) network message was received'
						continue
					
					network[CHATMSG] = network[CHATMSG].decode('utf-8').replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#')
					self.MS_Chat.emit(network)
					
				elif header == 'MC':
					music = decode_ao_str(network[1])
					charid = int(network[2])
					t = time.localtime()
					if charid != -1:
						try:
							name = self.parent.charlist[charid][0]
						except:
							name = 'char id %d' % charid
						
						if len(network) > 3 and network[3]:
							name += " ("+network[3].decode("utf-8")+")"
						#self.parent.icLog.append('[%d:%.2d] %s changed the music to %s' % (t[3], t[4], name, music))
						self.IC_Log.emit('[%d:%.2d] %s changed the music to %s' % (t[3], t[4], name, music))
					else:
						self.IC_Log.emit('[%d:%.2d] the music was changed to %s' % (t[3], t[4], music))
					self.parent.playMusic(music)

				elif header == 'BN':
					self.newBackground.emit(network[1])
				
				elif header == 'CT':
					name = network[1].decode('utf-8').replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#').replace('<pound>', '#')
					chatmsg = network[2].decode('utf-8').replace('<dollar>', '$').replace('<percent>', '%').replace('<and>', '&').replace('<num>', '#').replace('<pound>', '#').replace("\n", "<br />")
					#self.parent.ooclog.append('<b>%s:</b> %s' % (name, chatmsg))
					self.OOC_Log.emit("<b>%s:</b> %s" % (name, chatmsg))
				
				elif header == 'PV':
					self.parent.mychar = int(network[3])
					self.parent.charselect.hide()
					if self.parent.swapping:
						continue
					self.newChar.emit(self.parent.charlist[self.parent.mychar][0])
				
				elif header == 'LE':
					del network[0]
					self.allEvidence.emit([evi.split('&') for evi in network])

				elif header == 'ZZ':
					if self.parent.modcall:
						BASS_ChannelPlay(self.parent.modcall, False)
					
					if len(network) > 1:
						self.OOC_Log.emit('<b>[MOD CALL] ' + network[1].replace("\n", "<br />") + '</b>')
					else:
						self.OOC_Log.emit('<b>[MOD CALL] But there was no extra information. (old server?)</b>')
				elif header == 'CharsCheck':
					del network[0]
					for i in range(len(network)):
						self.parent.charlist[i][1] = int(network[i])

					self.charSlots.emit()
				
				elif header == 'RT':
					testimony = network[1]
					if testimony == 'judgeruling':
						variant = int(network[2])
						if variant == 0:
							BASS_ChannelPlay(self.parent.notguiltysfx, True)
						elif variant == 1:
							BASS_ChannelPlay(self.parent.guiltysfx, True)
					else:
						variant = 0
						BASS_ChannelPlay(self.parent.wtcesfx, True)
					self.parent.WTCEsignal.emit(testimony, variant)
				
				elif header == 'HP':
					type = int(network[1])
					health = int(network[2])
					self.parent.healthbars.emit(type, health)
				
				elif header == 'KK':
					reason = network[1]
					self.parent.emit(QtCore.SIGNAL('showMessage(QString, QString, QString)'), 'critical', 'Connection lost', 'You were kicked off the server. (%s)' % reason)
				
				elif header == 'KB':
					reason = network[1]
					self.parent.emit(QtCore.SIGNAL('showMessage(QString, QString, QString)'), 'critical', 'Connection lost', 'You have been banned from the server. (%s)' % reason)
				
				elif header == "CHECK": #ping
					pingafter = time.time()
					self.parent.gotPing.emit(int((pingafter - pingbefore)*1000))
				
				elif header == 'DONE':
					self.showCharSelect.emit()
