from cnocr import CnOcr
import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np

ocr_conf = 0.5

img_fp = 'IMG_42.jpg'
img = cv2.imread(img_fp)
height, width = img.shape[:2]
ocr = CnOcr(rec_model_name='chinese_cht_PP-OCRv3')
out = ocr.ocr(img)

text = ''
fontPath = 'NotoSerifTC-Regular.otf'
font = ImageFont.truetype(fontPath, 20)    #set font size
imgPil = Image.fromarray(img)
draw = ImageDraw.Draw(imgPil)
for i in range(len(out)):
    if out[i]['score'] > 0.5:
        coords = out[i]['position']
        minX = 100000
        maxX = -1
        minY = 100000
        maxY = -1
        for coord in coords:
            x = int(coord[0])
            y = int(coord[1])
            minX = minX if minX < x else x
            minY = minY if minY < y else y
            maxX = maxX if maxX > x else x
            maxY = maxY if maxY > y else y
        if len(out[i]['text']) <= 0:
            print("skip")
            continue
        text = text + out[i]['text']
        draw.rectangle([(minX, minY), (maxX, maxY)], outline="green")
        text_x = min(minX+10, width-1)
        text_y = max(0, minY-5)

        draw.text((text_x, text_y), out[i]['text'], fill=(0,0,255), font=font)

print(text)
image = np.array(imgPil)
cv2.imwrite("result.jpg", image)
