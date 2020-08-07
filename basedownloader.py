from PyQt4 import QtGui, QtCore
import json, urllib, sys, requests, time, os, zipfile

returncode = 4
msgbox = ["", "", ""]

def downloadVanilla():
    circus = QtGui.QProgressDialog()
    circus.setWindowTitle("AO2XP content downloader")
    circus.setAutoClose(False)
    circus.setAutoReset(False)
    circus.setLabelText("Getting AO vanilla zip link...")
    circus.resize(512, 96)
    circus.show()
    
    def setProgressValue(value):
        circus.setValue(value)
    def setLabelText(msg):
        circus.setLabelText(msg)
    
    thr = downloadThread(circus)
    thr.progressValue.connect(setProgressValue)
    thr.labelText.connect(setLabelText)
    thr.finished.connect(circus.close)
    thr.start()

    circus.exec_()
    if thr.isRunning(): thr.wait()

    if msgbox[0]:
        getattr(QtGui.QMessageBox, msgbox[0])(None, msgbox[1], msgbox[2])

    print returncode
    if returncode != 0: sys.exit(returncode)

class downloadThread(QtCore.QThread):
    progressValue = QtCore.pyqtSignal(int)
    labelText = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()

    def __init__(self, jm):
        super(self.__class__, self).__init__()
        self.jm = jm

    def run(self):
        global returncode, msgbox

        try:
            manifest = json.load(urllib.urlopen("http://s3.wasabisys.com/ao-manifests/assets.json"))
        except:
            msgbox[0] = "critical"
            msgbox[1] = "Download failed"
            msgbox[2] = "Could not check for latest AO vanilla version.\nPlease check your internet connection."
            return
            
        latest_version = manifest["versions"][0]["version"]
        print latest_version
        link = ""
        for actions in manifest["versions"][0]["full"]:
            if actions["action"] == "dl":
                link = actions["url"]
                print link
                break

        #link = "http://somepeople.ddns.net/headbot/song.zip"
        self.labelText.emit("Downloading version '%s'..." % latest_version)
        start = time.clock()
        zip = requests.get(link, stream=True)
        length = int(zip.headers.get("content-length"))
        dl = 0
        speed = 0.0

        filename = os.path.basename(link)
        if not os.path.exists(filename):
            downloadfile = open(filename, "wb")

            for noby in zip.iter_content(chunk_size=4096):
                if not self.jm.isVisible():
                    downloadfile.close()
                    os.remove(filename)
                    returncode = 4
                    return

                downloadfile.write(noby)
                dl += len(noby)
                percent = 100 * dl / length
                if percent != self.jm.value():
                    self.progressValue.emit(percent)
                    self.labelText.emit("Downloading version '%s'... %.1f KB/s" % (latest_version, speed))
                
                if (time.clock() - start) >= 1:
                    speed = (dl//(time.clock() - start)) / 1024.
                    self.labelText.emit("Downloading version '%s'... %.1f KB/s" % (latest_version, speed))

            print "downloaded"
            downloadfile.close()

        self.labelText.emit("Opening '%s'..." % filename)
        zip = zipfile.ZipFile(filename)

        notheme_list = []
        
        for f in zip.filelist:
            if not "base/themes" in f.filename:
                notheme_list.append(f.filename)

        self.labelText.emit("Extracting '%s'..." % filename)
        for f in notheme_list:
            i = notheme_list.index(f)
            zip.extract(f)
            self.progressValue.emit(100 * i / len(notheme_list))
        zip.close()

        returncode = 0
        self.finished.emit()