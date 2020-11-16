import numpy as np
from math import*
import qrcode
from PIL import Image

f = open("/Users/Tony/Desktop/science.pdf", "r")
I = Image.open("/Users/Tony/Desktop/ref_1.png")

array = np.arange(0., pi, 0.01)
qr = qrcode.QRCode(box_size = 10, border = 4)
qr.add_data(array)
qr.make(fit=True)
img = qr.make_image()

img.save("qrcode.png")