from PIL import Image
from PyQt4 import QtGui
from apng import APNG
import io

def load_apng(file):
	pass

def load_webp(file):
	pass

def get_apng_duration(file):
    img = APNG.open(file)
    dur = 0
    
    for frame, frame_info in img.frames:
        dur += frame_info.delay*10 # it's in centiseconds, convert to milliseconds

    return dur

def get_webp_duration(file):
    img = Image.open(file)
    dur = 0
    
    for i in range(img.n_frames):
        img.seek(i)
        img.load() # strange thing with Pillow and animated webp's is that the img.info dictionary attr doesn't update unless you call a function like this
        dur += img.info["duration"]

    return dur