import sys
import time
import math
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsRectItem
from PyQt5.QtGui import QColor
from qt_test import Ui_MainWindow
import scipy.io.wavfile as wav
import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import formantsynt
from tuben_gui import Tuben
import cy_test


# Create a subclass of QMainWindow to setup the GUI
class AppWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_add.clicked.connect(self.menu_add)
        self.pushButton_remove.clicked.connect(self.menu_remove)
        self.pushButton_sound.clicked.connect(self.menu_sound)
        self.play_audio.clicked.connect(self.play_sound)
        self.pushButton_illustrate.clicked.connect(self.menu_illustrate)
        self.pushButton_3dfile.clicked.connect(self.menu_3d)
        self.L = None
        self.A = None
        self.audio_name = ''
        # 创建 QGraphicsScene
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)

    def menu_add(self):
        lengths = self.lengths.toPlainText()
        areas = self.areas.toPlainText()
        if self.L is None or self.A is None:
            self.L = [float(l) for l in lengths.split(',')]
            self.A = [float(a) for a in areas.split(',')]
        else:
            self.L += [float(l) for l in lengths.split(',')]
            self.A += [float(a) for a in areas.split(',')]
        if len(self.L) != len(self.A):
            print('the "lengths" and "areas" lists must be of equal length')
            exit(1)
        print(self.L, self.A)
        self.visualization(self.L, self.A)

    def menu_remove(self):
        if self.L is None or self.A is None:
            print('no input value')
            exit(1)
        self.L.pop()
        self.A.pop()
        print(self.L, self.A)
        self.visualization(self.L, self.A)

    def visualization(self, l, a):
        self.scene.clear()
        diameter = [2*math.sqrt(i/3.14) for i in a]
        x_offset = 0
        for length, width in zip(l, diameter):
            rect = QGraphicsRectItem(x_offset, 0, length*25, width*25)
            rect.setBrush(QColor.fromRgb(0, 255, 0))  # 设置矩形颜色
            self.scene.addItem(rect)
            x_offset += length*25
        self.graphicsView.update()

    def menu_sound(self):
        if self.L is None or self.A is None:
            print('no input value')
            exit(1)
        fs = 16000
        tub = Tuben()
        print(self.L, self.A)
        self.fmt, self.Y = tub.get_formants(self.L, self.A)
        x = formantsynt.impulsetrain(fs, 70.0, 1.5)
        y = formantsynt.ffilter(fs, x, self.fmt)
        self.audio_name = str(time.strftime("%H-%M-%S"))
        wav.write(self.audio_name + '.wav', fs, y)
        print('wrote:', self.audio_name + '.wav')

    def play_sound(self):
        # 读取音频文件
        fs, data = wav.read(self.audio_name + '.wav')
        # 播放音频文件
        sd.play(data, fs)
        sd.wait()  # 等待播放结束

    def generate_image(self):
        if len(self.L) != len(self.A):
            print('the "lengths" and "areas" lists must be of equal length')
            exit(1)
        fig, ax = plt.subplots(3, 1)
        fig.tight_layout(pad=2.5)

        # plot tube
        x = 0
        for l, a in zip(self.L, self.A):
            ax[0].add_patch(Rectangle((x, 0), l, a, ls='--', ec='k'))
            x += l

        ax[0].set_xlim([0, x])
        ax[0].set_ylim([0, max(self.A) * 1.1])
        ax[0].set_title('tube')
        ax[0].set_xlabel('distance from lips (cm)')
        ax[0].set_ylabel('area ($cm^2$)')

        F = np.arange(1, 8000)

        # plot function & peaks
        ax[1].plot(F, self.Y, ':')
        ax[1].plot(F[self.fmt], self.Y[self.fmt], '.')
        ax[1].set_title('peakfunction:' + "determinant")
        ax[1].set_xlabel('frequency (Hz)')

        ax[2].set_title('transfer function')
        ax[2].set_xlabel('frequency (Hz)')
        ax[2].set_ylabel('dB')
        plt.sca(ax[2])

        fs = 16000

        f, h = formantsynt.get_transfer_function(fs, self.fmt)
        ax[2].plot(f, h)
        # plt.show()
        plt.savefig(self.audio_name + '.png')

    def menu_illustrate(self):
        self.scene.clear()
        self.generate_image()
        # 创建 QPixmap 并加载 PNG 图像
        pixmap = QtGui.QPixmap(self.audio_name + '.png')
        # 创建 QGraphicsPixmapItem 并添加到 QGraphicsScene 中
        pixmap_item = QtWidgets.QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.graphicsView.update()

    def menu_3d(self):
        if self.L is None or self.A is None:
            print('no input value')
            exit(1)
        cy_test.tubemaker_3d(self.L, self.A)


# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = AppWindow()
    myWindow.show()
    sys.exit(app.exec_())
