from PyQt4 import QtGui, QtCore
import socket, thread, time
from os.path import exists
from functools import partial
from buttons import PixmapButton

AOpath = "base/"
#AOpath = "I:/aovanilla1.7.5/client/base/"

def get_option(section, value, default=""):
        tempini = ConfigParser()
	tempini.read("base/ao2xp.ini")
	return ini.read_ini(tempini, section, value, default)

class CharIcon(QtGui.QLabel):
	def __init__(self, parent, ind):
		super(CharIcon, self).__init__(parent)
		self.parent = parent
		self.ind = ind
	
	def mousePressEvent(self, event):
		self.parent.onCharClicked(self.ind)

class charselect(QtGui.QWidget):
	setBtnImage = QtCore.pyqtSignal(str, int)
	def __init__(self, parent):
		super(charselect, self).__init__(parent)
		self.parent = parent
		self.page = 0
		self.image = QtGui.QLabel(self)
		self.image.setPixmap(QtGui.QPixmap(AOpath+"themes/default/charselect_background.png"))
		self.image.show()
		
		self.quittolobby = QtGui.QPushButton(self)
		self.quittolobby.setText("Disconnect")
		self.quittolobby.resize(self.quittolobby.sizeHint())
		self.quittolobby.clicked.connect(self.quitToLobby)
		
		self.buttons = []
		self.chartaken = []
		
		#directly stolen from ao2 source code and default theme because i was stuck (i'm so sorry)
		btn_width, btn_height = 60, 60
		x_spacing, y_spacing = 7, 7
		x_mod_count, y_mod_count = 0, 0
		left, top = 25, 36
		width, height = 663, 596
		columns = (width - btn_width) / (x_spacing + btn_width) +1
		rows = (height - btn_height) / (y_spacing + btn_height) +1
		self.max_chars_on_page = columns * rows
		for i in range(self.max_chars_on_page):
			self.buttons.append(CharIcon(self, i))
			self.chartaken.append(QtGui.QLabel(self))
			self.chartaken[i].setPixmap(QtGui.QPixmap(AOpath+"themes/default/char_taken.png"))
			self.chartaken[i].hide()
			
			x_pos = (btn_width + x_spacing) * x_mod_count
			y_pos = (btn_height + y_spacing) * y_mod_count
			self.buttons[i].setGeometry(left+x_pos, top+y_pos, btn_width, btn_height)
			self.chartaken[i].move(left+x_pos, top+y_pos)
			self.buttons[i].show()
			
			x_mod_count += 1
			if x_mod_count == columns:
				y_mod_count += 1
				x_mod_count = 0
		
		self.prevpage = PixmapButton(self, QtGui.QPixmap(AOpath+"themes/default/arrow_left.png"))
		self.prevpage.move(left - self.prevpage.pixmap.size().width(), top + height)
		self.prevpage.clicked.connect(self.prevPageButton)
		self.prevpage.show()
		self.nextpage = PixmapButton(self, QtGui.QPixmap(AOpath+"themes/default/arrow_right.png"))
		self.nextpage.move(left + width, top + height)
		self.nextpage.clicked.connect(self.nextPageButton)
		self.nextpage.show()
		
		self.setBtnImage.connect(self.setButtonImage)
	
	def quitToLobby(self):
		self.parent.gamewindow.returnToMenu()
	
	def setPic(self, pixmap, ind):
		self.buttons[ind].setPixmap(QtGui.QPixmap(pixmap))
	
	def setCharList(self, charlist):
		self.charlist = charlist
		self.page = 0
		self.showCharPage()
	
	def nextPageButton(self):
		self.page += 1
		self.showCharPage()
	
	def prevPageButton(self):
		self.page -= 1
		self.showCharPage()
		
	def showCharPage(self):
		for ind in range(self.page * self.max_chars_on_page, self.max_chars_on_page * (self.page+1)):
			i = ind - (self.page * self.max_chars_on_page)
			if ind >= len(self.charlist):
				self.chartaken[i].hide()
				self.buttons[i].hide()
				self.nextpage.hide()
				continue
			else:
				self.nextpage.show()
			
			if self.page > 0:
				self.prevpage.show()
			else:
				self.prevpage.hide()
			
			if exists(AOpath+"characters/"+self.charlist[ind][0]+"/char_icon.png"): # AO2
				self.setBtnImage.emit(AOpath+"characters/"+self.charlist[ind][0]+"/char_icon.png", i)
			elif exists(AOpath+"misc/demothings/"+self.charlist[ind][0]+"_char_icon.png"): # AO 1.7.5/1.8
				self.setBtnImage.emit(AOpath+"misc/demothings/"+self.charlist[ind][0]+"_char_icon.png", i)
			else:
				self.setBtnImage.emit("placeholder.png", i)
			
			if self.charlist[ind][1] == 0: # free slot
				self.chartaken[i].hide()
			else:
				self.chartaken[i].show()
			
			self.buttons[i].show()
	
	def setButtonImage(self, filename, ind):
		self.buttons[ind].setPixmap(QtGui.QPixmap(filename))
	
	def onCharClicked(self, ind):
		self.parent.tcp.send("CC#0#"+str(ind+(self.page*self.max_chars_on_page))+"#ur mom gay#%")

	def show(self):
		super(charselect, self).show()
		self.parent.gamewindow.setFixedSize(714, 668)
