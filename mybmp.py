# -*- coding: UTF-8 -*-
from struct import unpack, pack
import sys
import os
import getopt
import platform

# 读取并存储 bmp 文件
# bmp 图片的存储方式 从下到上从左到右


class ReadBMPFile:

    def __init__(self, file_path, force_revers=0, force_swap=0, printmsg = 0):
        self.file = open(file_path, "rb+")
        # 读取 bmp 文件的文件头    14 字节
        self.bfType = unpack("<h", self.file.read(2))[0]  # 0x4d42 对应BM 表示这是Windows支持的位图格式
        self.bfSize = unpack("<i", self.file.read(4))[0]  # 位图文件大小
        self.bfReserved1 = unpack("<h", self.file.read(2))[0]  # 保留字段 必须设为 0
        self.bfReserved2 = unpack("<h", self.file.read(2))[0]  # 保留字段 必须设为 0
        self.bfOffBits = unpack("<i", self.file.read(4))[0]  # 偏移量 从文件头到位图数据需偏移多少字节（位图信息头、调色板长度等不是固定的，这时就需要这个参数了）
        # 读取 bmp 文件的位图信息头 40 字节
        self.biSize = unpack("<i", self.file.read(4))[0]  # 所需要的字节数
        self.biWidth = unpack("<i", self.file.read(4))[0]  # 图像的宽度 单位 像素
        self.biHeight = unpack("<i", self.file.read(4))[0]  # 图像的高度 单位 像素
        self.biPlanes = unpack("<h", self.file.read(2))[0]  # 说明颜色平面数 总设为 1
        self.biBitCount = unpack("<h", self.file.read(2))[0]  # 说明比特数

        self.biCompression = unpack("<i", self.file.read(4))[0]  # 图像压缩的数据类型
        self.biSizeImage = unpack("<i", self.file.read(4))[0]  # 图像大小
        self.biXPixelsPerMeter = unpack("<i", self.file.read(4))[0]  # 水平分辨率
        self.biYPixelsPerMeter = unpack("<i", self.file.read(4))[0]  # 垂直分辨率
        self.biClrUsed = unpack("<i", self.file.read(4))[0]  # 实际使用的彩色表中的颜色索引数
        self.biClrImportant = unpack("<i", self.file.read(4))[0]  # 对图像显示有重要影响的颜色索引的数目
        self.head = []
        self.color_map = []
        self.bmp_data = []
        self.bf_map = []
        self.force_revers = force_revers
        self.force_swap = force_swap
        if self.biSize > 40:
            self.read_other(self.biSize-40)

        if self.biClrUsed == 0:
            colormap_num = 256
        else :
            colormap_num = self.biClrUsed

        if self.biBitCount == 8:
            for i in range(colormap_num):
                self.color_map.append(
                    [unpack("<B", self.file.read(1))[0], unpack("<B", self.file.read(1))[0],
                     unpack("<B", self.file.read(1))[0]])
                self.file.read(1)
        if self.biBitCount == 16 and self.biCompression == 3:
            for i in range(4):
                self.bf_map.append(
                    [unpack("<i", self.file.read(4))[0]]
                )
            if self.bf_map[0][0] == 63488 and self.bf_map[1][0] == 2016 and self.bf_map[2][0] == 31:
                self.bf = 565
            else:
                print("ERR! not support bf is not 565")
                self.show_bf_map()
        self.printmsg = printmsg	
        self.print_all_msg()
        if self.printmsg:
            print("just print msg\n")
            return 
        if self.biBitCount == 24:
            self.get_24bit_data()
        elif self.biBitCount == 16:
            if self.biCompression == 3:
                #self.show_bf_map()
                self.bmp16bit_to_24bit_bf()
            else:
                self.bmp16bit_to_24bit()
        elif self.biBitCount == 8:
            #self.show_color_map()
            if self.biCompression == 1:
                self.bmp8bit_to_24bit_rle()
            elif self.biCompression == 0:
                self.bmp8bit_to_24bit()
            else:
                print("err! bit_count is 8 while bit_compressoion is wrong")
        else:
            self.bmp32bit_to_24bit()
        # self.bmp8bitTo24bit()
        # self.show_color_map()
        # self.test()
        self.rb_swap = 0
        if self.bfReserved1 != 8399:
            self.reverse_bmp_data()
            print("reverse data by normal")
            self.rb_swap = 1
        if self.force_revers:
            self.reverse_bmp_data()
            print("reverse data by force")
        if self.force_swap:
            self.rb_swap = 1
            print("swap rb by force")
        self.write_24bit(self.rb_swap)
        self.file.close()

    def read_other(self, n):
        for i in range(n):
            self.file.read(1)

    def reverse_bmp_data(self):
        self.bmp_data.reverse()

    def show_color_map(self):
        for i in range(256):
            print("color map {} is {}".format(i, self.color_map[i]))

    def show_bf_map(self):
        for i in range(4):
            print("BF MAP {} is {}".format(i, self.bf_map[i]))

    def test(self):
        for height in range(abs(self.biHeight)):
            for width in range(self.biWidth):
                print(self.file.read(1))
                # print(unpack("<B", self.file.read(1)))
                # data = self.color_map[unpack("<B", self.file.read(1))[0]]
                # print(data)
                print("height is {} width is {}".format(height, width))

    @staticmethod
    def bmp_print(str):
        py_version = platform.python_version()
        if py_version[0] == 3:
            print(str)

    @staticmethod
    def get_16bit_bgr_bf(pixel):
        red = (pixel[1] & 0xf8) << 0
        green = ((pixel[1] & 0x07) << 5) | ((pixel[0] & 0xe0) >> 3)
        blue = ((pixel[0] & 0x1f) << 3)
        new_pixel = [blue, green, red]
        return new_pixel

    def bmp32bit_to_24bit(self):
        for height in range(abs(self.biHeight)):
            bmp_data_row = []
            # 四字节填充位检测
            count = 0
            for width in range(self.biWidth):
                bmp_data_row.append(
                    [unpack("<B", self.file.read(1))[0], unpack("<B", self.file.read(1))[0], unpack("<B", self.file.read(1))[0]])
                self.file.read(1)
                count = count + 4
            # bmp 四字节对齐原则
            while count % 4 != 0:
                self.file.read(1)
                count = count + 1
            self.bmp_data.append(bmp_data_row)
        # self.bmp_data.reverse()

    def bmp16bit_to_24bit_bf(self):
        self.get_16bit_data()
        temp_data = self.bmp_data
        self.bmp_data = []
        for height in range(abs(self.biHeight)):
            bmp_data_row = []
            for width in range(self.biWidth):
                bmp_data_row.append(
                    self.get_16bit_bgr_bf(temp_data[height][width])
                )
            self.bmp_data.append(bmp_data_row)

    def bmp8bit_to_24bit_rle(self):
        bmp_data_row = []
        data_x = []
        t_count = 0
        loop = 1
        while loop:
            data1 = unpack("<B", self.file.read(1))[0]
            if data1 > 0:
                data2 = unpack("<B", self.file.read(1))[0]
                for n in range(data1):
                    bmp_data_row.append(self.color_map[data2])
            if data1 == 0:
                data2 = unpack("<B", self.file.read(1))[0]
                if data2 > 2:
                    data_count = data2
                    data_temp = unpack("<B", self.file.read(1))[0]
                    data_x.append(data_temp)
                    while data_temp != 0:
                        data_temp = unpack("<B", self.file.read(1))[0]
                        data_x.append(data_temp)
                    for m in range(data_count):
                        bmp_data_row.append(self.color_map[data_x[m]])
                if data2 == 2:
                    print("data2 == 2")
                if data2 == 0:
                    t_count += 1
                    # print("row is %d" % t_count)
                    # print("size of bmp_data is %d" % len(bmp_data_row))
                    self.bmp_data.append(bmp_data_row)
                    bmp_data_row = []
                if data2 == 1:
                    print("encode over!")
                    loop = 0

    def bmp8bit_to_24bit(self):
        for height in range(abs(self.biHeight)):
            bmp_data_row = []
            # 四字节填充位检测
            data_count = 0
            count = 0
            for width in range(self.biWidth):
                if data_count > self.biSizeImage:
                    break
                bmp_data_row.append(
                    self.color_map[unpack("<B", self.file.read(1))[0]])
                data_count = data_count + 1
                count = count + 1
            # bmp 四字节对齐原则
            while count % 4 != 0:
                if data_count > self.biSizeImage:
		    break
                self.file.read(1)
                data_count = data_count + 1
                count = count + 1
            self.bmp_data.append(bmp_data_row)
        # self.bmp_data.reverse()

    @staticmethod
    def get_16bit_bgr(pixel):
        red = (pixel[1] & 0x7c) << 1
        green = ((pixel[1] & 0x03) << 6) | ((pixel[0] & 0xe0) >> 2)
        blue = ((pixel[0] & 0x1f) << 3
        new_pixel = [blue, green, red]
        return new_pixel

    def bmp16bit_to_24bit(self):
        self.get_16bit_data()
        temp_data = self.bmp_data
        self.bmp_data = []
        for height in range(abs(self.biHeight)):
            bmp_data_row = []
            for width in range(self.biWidth):
                bmp_data_row.append(
                    self.get_16bit_bgr(temp_data[height][width])
                )
            self.bmp_data.append(bmp_data_row)

    def get_head(self):
        self.file.seek(0, 0)
        for i in range(54):
            self.head.append(unpack("<B", self.file.read(1))[0])
        # self.file.seek(0,pop)
        return self.head

    def get_16bit_data(self):
        for height in range(abs(self.biHeight)):
            bmp_data_row = []
            count = 0
            for width in range(self.biWidth):
                bmp_data_row.append(
                    [unpack("<B", self.file.read(1))[0], unpack("<B", self.file.read(1))[0]])
                count = count + 2
            while count % 4 != 0:
                self.file.read(1)
                count = count + 1
            self.bmp_data.append(bmp_data_row)

    def get_24bit_data(self):
        for height in range(abs(self.biHeight)):
            bmp_data_row = []
            # 四字节填充位检测
            count = 0
            for width in range(self.biWidth):
                bmp_data_row.append(
                    [unpack("<B", self.file.read(1))[0], unpack("<B", self.file.read(1))[0], unpack("<B", self.file.read(1))[0]])
                count = count + 3
            # bmp 四字节对齐原则
            while count % 4 != 0:
                self.file.read(1)
                count = count + 1
            self.bmp_data.append(bmp_data_row)
        # self.bmp_data.reverse()

    def write_24bit(self,rb_swap):
        self.file.seek(0, 0)
        self.write_head_24bit()
        self.write_data_24bit(rb_swap)

    def write_head(self):
        self.file.write(pack("<h", self.bfType))
        self.file.write(pack("<i", self.bfSize))
        self.file.write(pack("<h", self.bfReserved1))
        self.file.write(pack("<h", self.bfReserved2))
        self.file.write(pack("<i", self.bfOffBits))  # bfOffBits
        self.file.write(pack("<i", self.biSize))  # biSize
        self.file.write(pack("<i", self.biWidth))

        self.file.write(pack("<i", self.biHeight * -1))
        self.file.write(pack("<h", self.biPlanes))
        self.file.write(pack("<h", self.biBitCount))  # biBitCount
        self.file.write(pack("<i", self.biCompression))  # biCompression
        self.file.write(pack("<i", self.biSizeImage))  # biSizeImage
        self.file.write(pack("<i", self.biXPixelsPerMeter))  # biXPixelsPerMeter
        self.file.write(pack("<i", self.biYPixelsPerMeter))  # biYPixelsPerMeter
        self.file.write(pack("<i", self.biClrUsed))  # biClrUsed
        self.file.write(pack("<i", self.biClrImportant))  # biClrImportant try to mark whether is reversed

    def write_head_24bit(self):
        temp_bi_width = self.biWidth * 3
        while temp_bi_width % 4 != 0:
            temp_bi_width = temp_bi_width + 1
        new_bf_size = temp_bi_width * abs(self.biHeight) + 54
        self.file.write(pack("<h", self.bfType))
        self.file.write(pack("<i", new_bf_size))
        self.file.write(pack("<h", 8399))
        self.file.write(pack("<h", self.bfReserved2))
        self.file.write(pack("<i", 54))  # bfOffBits
        self.file.write(pack("<i", 40))  # biSize
        self.file.write(pack("<i", self.biWidth))
        if self.biHeight > 0:
            self.file.write(pack("<i", self.biHeight * -1))
        else:
            self.file.write(pack("<i", self.biHeight))
        self.file.write(pack("<h", self.biPlanes))
        self.file.write(pack("<h", 24))  # biBitCount
        self.file.write(pack("<i", 0))  # biCompression
        self.file.write(pack("<i", 0))  # biSizeImage
        self.file.write(pack("<i", 0))  # biXPixelsPerMeter
        self.file.write(pack("<i", 0))  # biYPixelsPerMeter
        self.file.write(pack("<i", 0))  # biClrUsed
        self.file.write(pack("<i", 0))  # biClrImportant try to mark whether is reversed

    def write_data_24bit(self, rb_swap):
        for hg in range(abs(self.biHeight)):
            count = 0
            for wd in range(self.biWidth):
                if rb_swap:
                    self.file.write(pack("<B", self.bmp_data[hg][wd][2]))
                    self.file.write(pack("<B", self.bmp_data[hg][wd][1]))
                    self.file.write(pack("<B", self.bmp_data[hg][wd][0]))
                else:
                    self.file.write(pack("<B", self.bmp_data[hg][wd][0]))
                    self.file.write(pack("<B", self.bmp_data[hg][wd][1]))
                    self.file.write(pack("<B", self.bmp_data[hg][wd][2]))
                count = count + 3
            while count % 4 != 0:
                self.file.write(pack("<B", 0))
                count = count + 1

    def print_all_msg(self):
        print("bftype is {:x}\n"
              "bfSize is {:d}\n"
              "bfReserved1 is {:d}\n"
              "bfOffBits is {:d}\n"
              "biSize is {:d}\n"
              "biWidth is {:d}\n"
              "biHeight is {:d}\n"
              "biPlanes is {:d}\n"
              "biBitCount is {:d}\n"
              "biCompression is {:x}\n"
              "biSizeImage is {:d}\n"
              "biXPelsPerMeter is {:d}\n"
              "biYPelsPerMeter is {:d}\n"
              "biClrUsed is {:d}\n"
              "biClrImportant is {:d}\n"
              .format(self.bfType, self.bfSize, self.bfReserved1, self.bfOffBits, self.biSize, self.biWidth, self.biHeight,
                      self.biPlanes, self.biBitCount, self.biCompression, self.biSizeImage, self.biXPixelsPerMeter,
                      self.biYPixelsPerMeter, self.biClrUsed, self.biClrImportant))


if __name__ == "__main__":

    swap = 0
    revers = 0
    printmsg = 0
    par = len(sys.argv[1:])
    if par == 1:
        bmp = ReadBMPFile(sys.argv[1])
    elif par == 0:
        print("This program is trying to convert different format of bmpfile to a same format"
                "to make vop can handle bmpfile easily")
        print("try such cmd to make it work python bmpconvert xxx/xxx.bmp")
    else:
        try:
            opts, args = getopt.getopt(sys.argv[2:], "hrsp", ["help", "reverse", "swap", "print"])
            for opt, arg in opts:

                if opt in ('-h','--help'):
                    print("add -r option will force program to reverse data")
                    print("add -s option will force program to swap data of rb")
                if opt in ("-r", "--reverse"):
                    revers = 1
                if opt in ("-s", "--swap"):
                    swap = 1
                if opt in ("-p","--print"):
                    printmsg = 1
            bmp = ReadBMPFile(sys.argv[1], revers, swap, printmsg)
        except getopt.GetoptError:
            sys.exit(1)




