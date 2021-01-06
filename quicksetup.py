import urllib2
import zipfile
import subprocess
import sys
import os
import platform

def pip_install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

print "installing requests"
pip_install('requests')
import requests

print "downloading pybass"
filedata = urllib2.urlopen('http://master.dl.sourceforge.net/project/pybass/pybass_055.zip')
datatowrite = filedata.read()

with open('pybass_055.zip', 'wb') as f:  
    f.write(datatowrite)
    f.close()

print "extracting pybass"
zip_ref = zipfile.ZipFile('pybass_055.zip', 'r')
zip_ref.extractall()
zip_ref.close()

print "renaming pybass.py"
if os.path.exists("pybass/__init__.py"): os.remove('pybass/__init__.py')
os.rename('pybass/pybass.py', 'pybass/__init__.py')

BASSZIP = "bass24.zip"
BASSDLL = "bass.dll"
BASSOPUSZIP = "bassopus24.zip"
BASSOPUSDLL = "bassopus.dll"
if platform.system() == "Darwin":
    BASSZIP = "bass24-osx.zip"
    BASSDLL = "libbass.dylib"
    BASSOPUSZIP = "bassopus24-osx.zip"
    BASSOPUSDLL = "libbassopus.dylib"
elif platform.system() == "Linux":
    BASSZIP = "bass24-linux.zip"
    BASSDLL = "libbass.so"
    BASSOPUSZIP = "bassopus24-linux.zip"
    BASSOPUSDLL = "libbassopus.so"

print "downloading", BASSZIP
filedata = urllib2.urlopen('http://us.un4seen.com/files/'+BASSZIP)
datatowrite = filedata.read()

with open(BASSZIP, 'wb') as f:  
    f.write(datatowrite)
    f.close()

print "extracting "+BASSDLL+" from "+BASSZIP
zip_ref = zipfile.ZipFile(BASSZIP, 'r')
zip_ref.extract(BASSDLL)
zip_ref.close()

print "downloading", BASSOPUSZIP
filedata = urllib2.urlopen('http://us.un4seen.com/files/'+BASSOPUSZIP)
datatowrite = filedata.read()

with open(BASSOPUSZIP, 'wb') as f:
    f.write(datatowrite)
    f.close()

print "extracting "+BASSOPUSDLL+" from "+BASSOPUSZIP
zip_ref = zipfile.ZipFile(BASSOPUSZIP, 'r')
zip_ref.extract(BASSOPUSDLL)
zip_ref.close()

print "installing apng"
pip_install("apng")

try:
    from PIL import Image
    if Image.__version__ != "5.3.0":
        jm = raw_input("Pillow version 5.3.0 is recommended for compatibility with AO2XP; You have version %s\nReplace with version 5.3.0? (Y/N) > " % Image.__version__).lower()
        if jm == "y":
            print "installing Pillow 5.3.0"
            pip_install("Pillow==5.3.0")
    else:
        print "Pillow 5.3.0 already exists, skipping"

except ImportError:
    print "installing Pillow 5.3.0"
    pip_install("Pillow==5.3.0")

print "installing pyinstaller"
pip_install('pyinstaller')

if platform.system() == "Windows":
    print "downloading pyqt4"
    filedata = requests.get('http://raw.githubusercontent.com/dhb52/python-lib/master/PyQt4-4.11.4-cp27-cp27m-win32.whl')  
    datatowrite = filedata.content

    with open('PyQt4-4.11.4-cp27-cp27m-win32.whl', 'wb') as f:  
        f.write(datatowrite)
        f.close()

    print "installing pyqt4"
    pip_install('PyQt4-4.11.4-cp27-cp27m-win32.whl')

elif platform.system() == "Darwin":
    print "installing pyobjc"
    pip_install("pyobjc")

    print "for Mac OS X, use homebrew or macports to install pyqt4:"
    print "  brew install cartr/qt4/pyqt"
    print "  sudo port install py27-pyqt4"

elif platform.system() == "Linux":
    print "you need to install PyQt4 on your linux distro after this"

print "done"
