from PyQt4 import QtCore, QtGui
import os

AOpath = "base/"
#AOpath = "I:/aovanilla1.7.5/client/base/"

class AOToggleButton(QtGui.QLabel):
	pressed = False
	clicked = QtCore.pyqtSignal()

	def __init__(self, parent, x, y, btnname):
		super(AOToggleButton, self).__init__(parent)
		self.parent = parent
		self.notpressed_pix = QtGui.QPixmap(AOpath+"themes/default/%s.png" % btnname)
		self.pressed_pix = QtGui.QPixmap(AOpath+"themes/default/%s_pressed.png" % btnname)
		self.setPixmap(self.notpressed_pix)
		self.setGeometry(x, y, self.notpressed_pix.size().width(), self.notpressed_pix.size().height())
		self.show()
	
	def setPressed(self, on):
		self.pressed = on
		self.setPixmap(self.pressed_pix if on else self.notpressed_pix)
	
	def isPressed(self):
		return self.pressed
	
	def mousePressEvent(self, event):
		self.setPressed(not self.isPressed())
		self.clicked.emit()

class CustomObjection(QtGui.QLabel):
	pressed = False
	def __init__(self, parent, x, y):
		super(CustomObjection, self).__init__(parent)
		self.parent = parent
		self.setGeometry(x, y, 76, 28)
		self.notpressed_pix = QtGui.QPixmap(AOpath+"themes/default/custom.png")
		self.pressed_pix = QtGui.QPixmap(AOpath+"themes/default/custom_selected.png")
		self.setPixmap(self.notpressed_pix)
		self.show()
	
	def setPressed(self, on):
		self.pressed = on
		if on:
			self.setPixmap(self.pressed_pix)
		else:
			self.setPixmap(self.notpressed_pix)
	
	def isPressed(self):
		return self.pressed
	
	def mousePressEvent(self, event):
		self.setPressed(not self.isPressed())
		self.parent.objectbtn.setPressed(False)
		self.parent.holditbtn.setPressed(False)
		self.parent.takethatbtn.setPressed(False)

class WTCEbuttons(QtGui.QLabel):
	clicked = QtCore.pyqtSignal(int, int)
	type = 0
	variant = 0
	def __init__(self, parent, x, y, type, variant=0):
		super(WTCEbuttons, self).__init__(parent)
		self.setGeometry(x, y, 85, 42)
		if type == 0:
			self.setPixmap(QtGui.QPixmap(AOpath+"themes/default/witnesstestimony.png"))
		elif type == 1:
			self.setPixmap(QtGui.QPixmap(AOpath+"themes/default/crossexamination.png"))
		elif type == 2:
			if variant == 0:
				self.setPixmap(QtGui.QPixmap(AOpath+"themes/default/notguilty.png"))
			elif variant == 1:
				self.setPixmap(QtGui.QPixmap(AOpath+"themes/default/guilty.png"))
		self.type = type
		self.variant = variant
	
	def mousePressEvent(self, event):
		self.clicked.emit(self.type, self.variant)

class Objections(QtGui.QLabel):
	pressed = False
	type = 0
	def __init__(self, parent, x, y, type):
		super(Objections, self).__init__(parent)
		self.parent = parent
		self.type = type
		self.setGeometry(x, y, 76, 28)
		if type == 1:
			self.notpressed_pix = QtGui.QPixmap(AOpath+"themes/default/holdit.png")
			self.pressed_pix = QtGui.QPixmap(AOpath+"themes/default/holdit_selected.png")
		elif type == 2:
			self.notpressed_pix = QtGui.QPixmap(AOpath+"themes/default/objection.png")
			self.pressed_pix = QtGui.QPixmap(AOpath+"themes/default/objection_selected.png")
		elif type == 3:
			self.notpressed_pix = QtGui.QPixmap(AOpath+"themes/default/takethat.png")
			self.pressed_pix = QtGui.QPixmap(AOpath+"themes/default/takethat_selected.png")
		self.setPixmap(self.notpressed_pix)
		self.show()
	
	def setPressed(self, on):
		self.pressed = on
		if on:
			self.setPixmap(self.pressed_pix)
		else:
			self.setPixmap(self.notpressed_pix)
	
	def isPressed(self):
		return self.pressed
	
	def mousePressEvent(self, event):
		self.setPressed(not self.isPressed())
		self.parent.customobject.setPressed(False)
		if self.type == 1:
			self.parent.objectbtn.setPressed(False)
			self.parent.takethatbtn.setPressed(False)
		elif self.type == 2:
			self.parent.holditbtn.setPressed(False)
			self.parent.takethatbtn.setPressed(False)
		elif self.type == 3:
			self.parent.objectbtn.setPressed(False)
			self.parent.holditbtn.setPressed(False)

class PixmapButton(QtGui.QAbstractButton):
	def __init__(self, parent, pixmap):
		super(PixmapButton, self).__init__(parent)
		self.pixmap = pixmap

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.drawPixmap(event.rect(), self.pixmap)

	def sizeHint(self):
		return self.pixmap.size()
	
	def setPixmap(self, pixmap):
		self.pixmap = pixmap

class PixmapButton2(QtGui.QLabel):
	clicked = QtCore.pyqtSignal()
	rightClicked = QtCore.pyqtSignal()
	
	def __init__(self, parent, pixmap):
		super(PixmapButton2, self).__init__(parent)
		self.setPixmap(pixmap)
		self.show()
	
	def mousePressEvent(self, ev):
		if ev.buttons() == QtCore.Qt.LeftButton:
			self.clicked.emit()
		elif ev.buttons() == QtCore.Qt.RightButton:
			self.rightClicked.emit()

class PenaltyBars(QtGui.QLabel):
	minusClicked = QtCore.pyqtSignal(int)
	plusClicked = QtCore.pyqtSignal(int)
	def __init__(self, parent, type):
		super(PenaltyBars, self).__init__(parent)
		self.parent = parent
		self.penaltybars = []
		self.type = type
		self.health = 10
		self.resize(84, 14)
		if type == 1: #defense bar.
			for i in range(11):
				self.penaltybars.append(QtGui.QPixmap(AOpath+"themes/default/defensebar"+str(i)+".png"))
			side = "def"
		elif type == 2: #prosecution bar
			for i in range(11):
				self.penaltybars.append(QtGui.QPixmap(AOpath+"themes/default/prosecutionbar"+str(i)+".png"))
			side = "pro"
		self.side = side
		self.minusbtn = PixmapButton(parent, QtGui.QPixmap(AOpath+"themes/default/"+side+"minus.png"))
		self.plusbtn = PixmapButton(parent, QtGui.QPixmap(AOpath+"themes/default/"+side+"plus.png"))
		self.minusbtn.clicked.connect(self.minusClick)
		self.plusbtn.clicked.connect(self.plusClick)
		self.setPixmap(self.penaltybars[10])
		self.minusbtn.show()
		self.plusbtn.show()
		self.show()
	
	def moveBar(self, x, y):
		self.move(x, y)
		self.minusbtn.move(x-(9/2), y+(14/2)-(9/2))
		self.plusbtn.move(x+84-(9/2), y+(14/2)-(9/2))
	
	def plusClick(self):
		self.plusClicked.emit(self.type)
	
	def minusClick(self):
		self.minusClicked.emit(self.type)
	
	def setHealth(self, health):
		self.minusbtn.setPixmap(QtGui.QPixmap(AOpath+"themes/default/"+self.side+"minus.png"))
		self.plusbtn.setPixmap(QtGui.QPixmap(AOpath+"themes/default/"+self.side+"plus.png"))
		self.setPixmap(self.penaltybars[health])
		self.health = health
		
	def getHealth(self):
		return self.health
