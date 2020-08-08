from PyQt4 import QtGui, QtCore
import json, urllib, sys, requests, time, os, zipfile, sha

returncode = -4
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
    def showMessageBox(icon, title, msg):
        getattr(QtGui.QMessageBox, str(icon))(None, title, msg)
    
    thr = downloadThread(circus)
    thr.progressValue.connect(setProgressValue)
    thr.labelText.connect(setLabelText)
    thr.showMessageBox.connect(showMessageBox)
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
    showMessageBox = QtCore.pyqtSignal(str, str, str)
    finished = QtCore.pyqtSignal()

    def __init__(self, jm):
        super(self.__class__, self).__init__()
        self.jm = jm

    def run(self):
        global returncode, msgbox

        try:
            manifest = json.load(urllib.urlopen("http://s3.wasabisys.com/ao-manifests/assets.json"))
        except:
            self.showMessageBox.emit("critical", "Download failed", "Could not check for latest AO vanilla version.\nPlease check your internet connection.")
            self.finished.emit()
            return
            
        latest_version = manifest["versions"][0]["version"]
        print latest_version
        link = ""
        check_hash = ""
        for actions in manifest["versions"][0]["full"]:
            if actions["action"] == "dl":
                link = actions["url"]
                check_hash = actions["hash"]
                print link
                break

        #link = "http://somepeople.ddns.net/headbot/song.zip"

        resume_bytes = 0
        filename = os.path.basename(link)
        download_it = True
        if not os.path.exists(filename):
            downloadfile = open(filename, "wb")
        else:
            existing_data = open(filename, "rb").read()
            sha1 = sha.new(existing_data).hexdigest()
            downloadfile = open(filename, "ab")
            resume_bytes = len(existing_data)
            print resume_bytes
            del existing_data
            
            if sha1 == check_hash: # don't download, the local file already exists
                download_it = False
                downloadfile.close()

        if download_it:
            self.labelText.emit("Downloading version '%s'..." % latest_version)
            dl = resume_bytes
            speed = 0.0
            start = time.clock()
            zip = requests.get(link, stream=True, headers={"Range": "bytes=%d-" % resume_bytes})
            length = resume_bytes + int(zip.headers.get("content-length"))

            for noby in zip.iter_content(chunk_size=4096):
                if not self.jm.isVisible():
                    downloadfile.close()
                    returncode = -5
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
        os.remove(filename)

        returncode = 0
        self.finished.emit()