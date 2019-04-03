import urllib2
import zipfile
import subprocess
import sys
import os

def pip_install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

print "downloading pybass"
filedata = urllib2.urlopen('https://datapacket.dl.sourceforge.net/project/pybass/pybass_055.zip')  
datatowrite = filedata.read()

with open('pybass_055.zip', 'wb') as f:  
    f.write(datatowrite)
    f.close()

print "extracting pybass"
zip_ref = zipfile.ZipFile('pybass_055.zip', 'r')
zip_ref.extractall()
zip_ref.close()

print "renaming pybass.py"
os.remove('pybass/__init__.py')
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

print "downloading pyqt4"
filedata = urllib2.urlopen('https://download.lfd.uci.edu/pythonlibs/u2hcgva4/PyQt4-4.11.4-cp27-cp27m-win32.whl')  
datatowrite = filedata.read()

with open('PyQt4-4.11.4-cp27-cp27m-win32.whl', 'wb') as f:  
    f.write(datatowrite)
    f.close()

print "installing pyqt4"
pip_install('PyQt4-4.11.4-cp27-cp27m-win32.whl')

print "installing pyinstaller"
pip_install('pyinstaller')

print "done"
