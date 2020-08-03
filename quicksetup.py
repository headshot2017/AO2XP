import urllib2
import zipfile
import subprocess
import sys
import os

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


print "downloading bass"
filedata = urllib2.urlopen('http://us.un4seen.com/files/bass24.zip')
datatowrite = filedata.read()

with open('bass24.zip', 'wb') as f:  
    f.write(datatowrite)
    f.close()

print "extracting bass"
zip_ref = zipfile.ZipFile('bass24.zip', 'r')
zip_ref.extract('bass.dll')
zip_ref.close()

print "downloading bassopus"
filedata = urllib2.urlopen('http://us.un4seen.com/files/bassopus24.zip')
datatowrite = filedata.read()

with open('bassopus24.zip', 'wb') as f:  
    f.write(datatowrite)
    f.close()

print "extracting bassopus"
zip_ref = zipfile.ZipFile('bassopus24.zip', 'r')
zip_ref.extract('bassopus.dll')
zip_ref.close()

print "installing apng"
pip_install("apng")

try:
    from PIL import Image
    if Image.__version__ != "6.1.0":
        jm = raw_input("Pillow version 6.1.0 is recommended for compatibility with PyQt4; You have version %s\nReplace with version 6.1.0? (Y/N) > " % Image.__version__).lower()
        if jm == "y":
            print "installing Pillow 6.1.0"
            pip_install("Pillow==6.1.0")
    else:
        print "Pillow 6.1.0 already exists, skipping"

except ImportError:
    print "installing Pillow 6.1.0"
    pip_install("Pillow==6.1.0")


print "downloading pyqt4"
filedata = requests.get('http://raw.githubusercontent.com/dhb52/python-lib/master/PyQt4-4.11.4-cp27-cp27m-win32.whl')  
datatowrite = filedata.content

with open('PyQt4-4.11.4-cp27-cp27m-win32.whl', 'wb') as f:  
    f.write(datatowrite)
    f.close()


print "installing pyqt4"
pip_install('PyQt4-4.11.4-cp27-cp27m-win32.whl')

print "installing pyinstaller"
pip_install('pyinstaller')

print "done"
