self.gamewindow.setFixedSize(714, 668)

self.ooclog.setGeometry(714 - 288, 0, 288, 256)
self.oocnameinput.resize(self.oocnameinput.sizeHint().width() - 32, self.oocnameinput.sizeHint().height())
self.oocnameinput.move(714 - 288, 256)
self.oocinput.resize(187, self.oocinput.sizeHint().height())
self.oocinput.move(714 - 288 + self.oocnameinput.size().width(), 256)
self.ooclogin.resize(48, 20)
self.ooclogin.move(714 - (self.ooclogin.size().width()), self.oocinput.y() + self.ooclogin.size().height())

self.musicitems.setGeometry(714 - 288, 348, 288, 320)

self.icLog.setGeometry(8, 8, 714 - 304 - 22, 212)

self.evidencedropdown.setGeometry(8, 8, 192, 20)
self.evidencedesc.setGeometry(8, 108, 714 - 304 - 22, 112)
self.evidenceimage.setGeometry(326, 8, 70, 70)
self.evidenceadd.move(8, 32)
self.evidenceedit.move(8, 56)
self.evidencedelete.move(8, 80)
self.evidencepresent.move((714 - 304 - 22) / 2 - self.evidencepresent.button_off.size().width() / 2, self.evidencedesc.y() - self.evidencepresent.button_off.size().height())

self.msgqueueList.setGeometry(8, 8, 714 - 304 - 22, 180)
self.removeQueue.resize(self.removeQueue.sizeHint())
self.removeQueue.move(8, self.msgqueueList.size().height() + 16)

self.notmutedlabel.move(8, 8)
self.unmutedlist.setGeometry(8, 24, 160, 192)
self.mutedlist.setGeometry(238, 24, 160, 192)
self.mutedlabel.move(238 + self.mutedlist.size().width() - self.mutedlist.size().width() - 8, 8)
self.mutebtn.setGeometry((714 - 304) / 2 - 26, 64, 48, 32)
self.unmutebtn.setGeometry((714 - 304) / 2 - 26, 128, 48, 32)

self.iniswaplist.setGeometry(8, 8, 192, self.iniswaplist.sizeHint().height())
self.iniswapconfirm.resize(self.iniswapconfirm.sizeHint())
self.iniswapconfirm.move(714 - 304 - 22 - self.iniswapconfirm.size().width(), 8)
self.iniswapreset.resize(self.iniswapconfirm.size())
self.iniswapreset.move(714 - 304 - 22 - self.iniswapconfirm.size().width(), 16 + self.iniswapconfirm.size().height())
self.iniswapinfo.setGeometry(8, 32, 192, 24)
self.iniswaprefresh.move(8, 64)
self.iniswaprefresh.resize(self.iniswaprefresh.sizeHint())

self.paircheckbox.setGeometry(16, 16, 128, 24)
self.pairdropdown.setGeometry(112, 64, 192, 18)
self.pairoffset.setGeometry(114, 128, 192, 24)
self.pairoffset_l.move(self.pairoffset.x() - 88, self.pairoffset.y()+4)
self.pairoffsetreset.move(self.pairoffset.x() + self.pairoffset.size().width() + 8, self.pairoffset.y())
self.spacebartext.move(self.mocktext.x(), self.mocktext.y()+24)
self.autocaps.move(self.spacebartext.x(), self.spacebartext.y()+24)

self.gametabs.move(8, 402)
self.gametabs.resize(714 - 304, 256)

self.musicslider.setGeometry(self.oocnameinput.x(), self.oocnameinput.y()+24, 192, 16)
self.soundslider.setGeometry(self.oocnameinput.x(), self.oocnameinput.y()+48, 192, 16)
self.blipslider.setGeometry(self.oocnameinput.x(), self.oocnameinput.y()+72, 192, 16)

self.sliderlabel1.move(self.musicslider.x() + self.musicslider.size().width()+8, self.musicslider.y())
self.sliderlabel2.move(self.soundslider.x() + self.soundslider.size().width()+8, self.soundslider.y())
self.sliderlabel3.move(self.blipslider.x() + self.blipslider.size().width()+8, self.blipslider.y())

self.pinglabel.setGeometry(self.sliderlabel3.x() + 32, self.sliderlabel3.y(), 96, 14)