#import numpy as np
import sys
from mybmp import ReadBMPFile
from struct import unpack,pack
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as img
def print_np(np_arrat):
    print("type is {}\n"
          "ndim is {}\n"
          "size is {}\n"
          "shap is {}\n"
          "dtype is {}\n"
          .format(type(np_arrat), np_arrat.ndim, np_arrat.size, np_arrat.shape, np_arrat.dtype))
def bmp16bitTo24bit():

    pass
def bmp8bitTo24bit():
    pass

def write_head(fp,bmp):
    bfType = bmp.bfType
    bfSize = bmp.bfSize
    bfReserved1 = bmp.bfReserved1
    bfReserved2 = bmp.bfReserved2
    bfOffBits = bmp.bfOffBits
    biSize = bmp.biSize
    biWidth = bmp.biWidth
    biHeight = bmp.biHeight
    biPlanes = bmp.biPlanes
    biBitCount = bmp.biBitCount
    biCompression = bmp.biCompression
    biSizeImage = bmp.biSizeImage
    biXPelsPerMeter = bmp.biXPixelsPerMeter
    biYPelsPerMeter = bmp.biYPixelsPerMeter
    biClrUsed = bmp.biClrUsed
    biClrImportant = bmp.biClrImportant
    tempbiwidth = biWidth
    while tempbiwidth * 3 % 4 !=0:
        tempbiwidth = tempbiwidth + 1
    bfSize = tempbiwidth * biHeight * 3 + 54
    fp.write(pack("<h",bfType))
    fp.write(pack("<i",bfSize))
    fp.write(pack("<h",bfReserved1))
    fp.write(pack("<h",bfReserved2))
    fp.write(pack("<i",54)) # bfOffBits
    fp.write(pack("<i",40)) #biSize
    fp.write(pack("<i",biWidth))
    fp.write(pack("<i",biHeight))
    fp.write(pack("<h",biPlanes))
    fp.write(pack("<h",24))  # biBitCount
    fp.write(pack("<i",0))  # biCompression
    fp.write(pack("<i",0))  # biSizeImage
    fp.write(pack("<i",0))  # biXPixelsPerMeter
    fp.write(pack("<i",0))  # biYPixelsPerMeter
    fp.write(pack("<i",0))  # biClrUsed
    fp.write(pack("<i",0))  # biClrImportant
 #   for i in range(54):
 #       print(head[i])
 #       print(pack("<B",head[i]))
 #       fp.write(pack("<B", head[i]))

def write_data(fp,height,width,data):
    for hg in range(height):
        count = 0
        for wd in range(width):
            fp.write(pack("<B", data[hg][wd][0]))
            fp.write(pack("<B", data[hg][wd][1]))
            fp.write(pack("<B", data[hg][wd][2]))
            count = count + 3
        while count % 4 != 0:
            fp.write(pack("<B", 0))
            count = count + 1


def print_data(bmpFile, height, width):
    for ht in range(height):
        for wh in range(width):
            print(bmpFile[ht][wh])
# 命令行传入的文件路径
filePath = sys.argv[1]
# 读取 BMP 文件
nbmpFile = ReadBMPFile(filePath)
#head = nbmpFile.get_head()
data = nbmpFile.bmp_data
height = nbmpFile.biHeight
width = nbmpFile.biWidth
#print(data,height,width)
fp = open("hhht.bmp",'wb')
write_head(fp,nbmpFile)
write_data(fp,height,width,data)

nbmpFile.file.close()
fp.close()

#cv2.imwrite("hhht.bmp", n1)
resized_image = Image.open('hhht.bmp')
plt.imshow(resized_image)
plt.show()

#n1 = np.array(nbmpFile.bmp_data)
#bmpFile = nbmpFile.bmp_data
#nx = np.empty([100,30,3],dtype=np.uint8)
#print(nx.shape)
#print(nx)
#print(n1)
#print_np(n1)
#bmpFile = img.imread(filePath)
#newFile = bmpFile.astype(np.uint8)
#print(newFile.dtype)


#print_data(bmpFile)
#plt.imshow(bmpFile)
# R, G, B 三个通道 [0, 255]
#R = bmpFile.R
##G = bmpFile.G
#B = bmpFile.B

#print(R)
# 显示图像
#b = np.array(B, dtype = np.uint8)
# = np.array(G, dtype = np.uint8)
#r = np.array(R, dtype = np.uint8)
#merged = np.array((R,G,B),dtype=np.uint8)

#cv2.imwrite("filename.png", n1)
#resized_image = Image.open('filename.png')
#plt.imshow(resized_image)
#plt.show()

#print(b)
#print(g)
#print(r)
#im_r=Image.fromstring('L',(512,128),R.tostring())
#im_g=Image.fromstring('L',(512,128),G.tostring())
#im_b=Image.fromstring('L',(512,128),B.tostring())
#im_rgb=Image.merge('RGB',(im_r,im_g,im_b))
#im_rgb.save('rgb.bmp')
#im_rgb.show()

#cv2.imwrite('colorful.png', R)
#merged = cv2.merge([b, g, r]) #合并R、G、B分量 默认顺序为 B、G、R
#print(merged)
#cv2.imshow("Merged",merged)
