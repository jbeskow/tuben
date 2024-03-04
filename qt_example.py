import sys
import time
import math
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsRectItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import scipy.io.wavfile as wav
import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from qt_test import Ui_MainWindow
import formantsynt
from tuben_gui import Tuben
import cy_test


class MyRectItem(QGraphicsRectItem):
    def __init__(self, index, x, y, length, width, la, output_method=None):
        super().__init__(x, y, length, width)
        self.index = index  # 存储索引值
        self.la = la
        self.setBrush(QColor.fromRgb(0, 255, 0))  # 设置矩形颜色
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)  # 允许选择
        self.isClicked = False
        self.output_method = output_method

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isClicked = True
            if self.output_method:
                self.output_method('Index: {} clicked\nLength {}\nArea {}'.format(self.index, self.la[0], self.la[1]))
        super().mousePressEvent(event)


# Create a subclass of QMainWindow to setup the GUI
class AppWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_add.clicked.connect(self.menu_add)
        self.pushButton_remove.clicked.connect(self.menu_remove)
        self.pushButton_alter.clicked.connect(self.menu_alter)
        self.pushButton_sound.clicked.connect(self.menu_sound)
        self.play_audio.clicked.connect(self.play_sound)
        self.pushButton_illustrate.clicked.connect(self.menu_illustrate)
        self.pushButton_3dfile.clicked.connect(self.menu_3d)
        self.L = None
        self.A = None
        self.index = None
        self.audio_name = None
        self.rect_items = []
        self.scene = QtWidgets.QGraphicsScene()
        self.illustration.setScene(self.scene)

    def get_message(self, message):
        self.input_information_output.clear()
        self.input_information_output.insertPlainText(message)

    def get_index(self):
        if self.rect_items is not None:
            for item in self.rect_items:
                if item.isClicked:
                    self.index = item.index

    def menu_add(self):
        self.get_index()
        lengths = self.lengths.toPlainText()
        areas = self.areas.toPlainText()
        if self.L is None or self.A is None:
            # add sections
            self.L = [float(l) for l in lengths.split(',')]
            self.A = [float(a) for a in areas.split(',')]
        elif self.index is not None:
            # add a new section after the clicked section
            self.L.insert(self.index+1, float(lengths))
            self.A.insert(self.index+1, float(areas))
            self.index = None
        elif self.index is None and len(self.L) < 4:
            # add more sections at the end of tube if not clicking any tube section
            self.L += [float(l) for l in lengths.split(',')]
            self.A += [float(a) for a in areas.split(',')]
        if len(self.L) == len(self.A) and len(self.L) <= 4:
            self.visualization(self.L, self.A)
        elif len(self.L) > 4:
            self.get_message('Invalid input: Maximum 4 Tube Sections')
        else:
            self.get_message('Invalid input: lengths and areas lists must be of equal length')

    def menu_remove(self):
        if self.L is None or self.A is None:
            self.get_message('Empty Input Value')
        else:
            self.get_index()
            if self.index is not None:  # pop the section that has been clicked
                self.L.pop(self.index)
                self.A.pop(self.index)
                self.index = None
            else:  # otherwise pop the last section of the tube
                self.L.pop()
                self.A.pop()
            if len(self.L) == len(self.A) and len(self.L) > 0:
                self.visualization(self.L, self.A)
            else:
                self.scene.clear()
                self.get_message('Length:[]\nArea:[]')

    def menu_alter(self):
        if self.L is None or self.A is None:
            self.get_message('Empty Input Value')
        else:
            self.get_index()
            new_length = self.lengths.toPlainText()
            new_area = self.areas.toPlainText()
            if self.index is not None:
                try:
                    self.L[self.index] = float(new_length)
                    self.A[self.index] = float(new_area)
                    self.visualization(self.L, self.A)
                    self.index = None
                except ValueError:
                    self.get_message('Invalid Input')

    def visualization(self, l, a):
        self.scene.clear()
        diameter = [2*math.sqrt(i/3.14) for i in a]
        x_offset = 0
        i = 0
        for length, width in zip(l, diameter):
            la = [l[i], a[i]]
            rect = MyRectItem(i, x_offset, 0, length*25, width*25, la, self.get_message)
            self.scene.addItem(rect)
            self.rect_items.append(rect)
            x_offset += length*25
            i += 1
        self.get_message('Length:{}\nArea:{}'.format(self.L, self.A))
        self.illustration.update()

    def menu_sound(self):
        if self.L is None or self.A is None:
            self.get_message('Empty Input Value')
        elif len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        else:
            fs = 16000
            tub = Tuben()
            self.fmt, self.Y = tub.get_formants(self.L, self.A)
            x = formantsynt.impulsetrain(fs, 70.0, 1.5)
            y = formantsynt.ffilter(fs, x, self.fmt)
            self.audio_name = str(time.strftime("%H-%M-%S"))
            wav.write(self.audio_name + '.wav', fs, y)
            self.get_message('Audio ' + self.audio_name + '.wav Created')

    def play_sound(self):
        if self.audio_name is None:
            self.get_message("No Audio Generated")
        else:
            # open the audio file
            fs, data = wav.read(self.audio_name + '.wav')
            sd.play(data, fs)
            sd.wait()  # wait for the play process to finish

    def generate_image(self):
        if len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        if self.audio_name is None:
            self.get_message("No Audio Generated")
        else:
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
            plt.savefig(self.audio_name + '.png')
            self.get_message('Picture ' + self.audio_name + '.png Created')

    def menu_illustrate(self):
        self.generate_image()
        if self.audio_name is None:
            self.get_message("No Audio Generated")
        else:
            self.scene.clear()
            # 创建 QPixmap 并加载 PNG 图像
            pixmap = QtGui.QPixmap(self.audio_name + '.png')
            # 创建 QGraphicsPixmapItem 并添加到 QGraphicsScene 中
            pixmap_item = QtWidgets.QGraphicsPixmapItem(pixmap)
            self.scene.addItem(pixmap_item)
            self.illustration.update()

    def menu_3d(self):
        if self.L is None or self.A is None:
            self.get_message('Empty Input Value')
        elif len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        else:
            cy_test.tubemaker_3d(self.L, self.A)


# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = AppWindow()
    myWindow.show()
    sys.exit(app.exec_())
