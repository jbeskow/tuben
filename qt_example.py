import re
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
from qt_test import Ui_TubeN
import formantsynt
from tuben_gui import Tuben
import cy_test
from popups import InputDialogAdd, InputDialogAlter, TrajectoryWindow, Click3dPrinting
from AXIS import Axis


class MyRectItem(QGraphicsRectItem):
    def __init__(self, index, x, y, length, width, la, output_method=None):
        super().__init__(x, y, length, width)
        self.index = index  # 存储索引值
        self.la = la
        self.setBrush(QColor.fromRgb(200, 0, 0))  # 设置矩形颜色
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)  # 允许选择
        # self.setFlag(QGraphicsRectItem.ItemIsMovable, True)  # 允许拖拽
        self.isClicked = False
        self.output_method = output_method

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isClicked = True
            if self.output_method:
                self.output_method('Index: {} clicked\nLength {}\nArea {}'.format(self.index, self.la[0], self.la[1]))
        super().mousePressEvent(event)


# Create a subclass of QMainWindow to setup the GUI
class AppWindow(QMainWindow, Ui_TubeN):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_add.clicked.connect(self.menu_add)
        self.pushButton_remove.clicked.connect(self.menu_remove)
        self.pushButton_alter.clicked.connect(self.menu_alter)
        self.pushButton_sound.clicked.connect(self.menu_sound)
        self.play_audio.clicked.connect(self.play_sound)
        self.pushButton_illustrate.clicked.connect(self.menu_illustrate)
        self.doubleSpinBox_scale.setDecimals(1)
        self.doubleSpinBox_scale.setValue(0.0)
        self.pushButton_scale.clicked.connect(self.menu_scale)
        self.pushButton_3d.clicked.connect(self.menu_3d)
        self.pushButton_obliviate.clicked.connect(self.menu_obliviate)
        self.pushButton_trajectory.clicked.connect(self.menu_trajectory)

        self.rect_items = []
        self.scene = QtWidgets.QGraphicsScene()
        self.illustration.setScene(self.scene)

        self.example_a.clicked.connect(self.show_example_a)
        self.example_i.clicked.connect(self.show_example_i)
        self.example_o.clicked.connect(self.show_example_o)
        self.L = []
        self.A = []
        self.index = None
        self.audio_name = ''

    def get_message(self, message):
        self.input_information_output.clear()
        self.input_information_output.insertPlainText(message)

    def get_index(self):
        if self.rect_items is not None:
            for item in self.rect_items:
                if item.isClicked:
                    self.index = item.index

    def menu_add(self):
        dialog = InputDialogAdd(self)
        dialog.setWindowTitle("add")
        if dialog.exec_():
            self.get_index()
            lengths, areas = dialog.getInputs()
            match_l = bool(re.match(r'^\d(,\d)*$', lengths))
            match_a = bool(re.match(r'^\d(,\d)*$', lengths))
            if lengths == '' or areas == '':
                self.get_message('Empty Input Value')
            elif match_l and match_a:
                le = [float(l) for l in lengths.split(',')]
                ar = [float(a) for a in areas.split(',')]
                if len(le) == len(ar) and len(le) >= 1:
                    if len(self.L) == 0 or len(self.A) == 0:
                        # create tube sections
                        self.L = le
                        self.A = ar
                    elif self.index is not None and sum(self.L) < 16:
                        # add new sections to the tube
                        self.L[self.index:self.index] = le
                        self.A[self.index:self.index] = ar
                    else:
                        self.get_message('Invalid input: the total length must be under or equal to 16 centimeters')
                else:
                    self.get_message('Invalid input: lengths and areas lists must be of equal length')
                if len(self.L) == len(self.A) and sum(self.L) <= 16:
                    self.visualization(self.L, self.A)
            else:
                self.get_message('Invalid input, please try again')
            # Process the inputs or pass them to another part of the program here

    def menu_remove(self):
        if len(self.L) == 0 or len(self.A) == 0:
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
        dialog = InputDialogAlter(self)
        dialog.setWindowTitle("alter")
        if dialog.exec_():
            if len(self.L) == 0 or len(self.A) == 0:
                self.get_message('Empty Input Value')
            else:
                self.get_index()
                new_length, new_area = dialog.getInputs()
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
        diameter = [2 * math.sqrt(i / 3.14) for i in a]
        x_offset = 0
        i = 0
        for length, width in zip(l, diameter):
            la = [l[i], a[i]]
            rect = MyRectItem(i, x_offset, 300, length * 25, width * 25, la, self.get_message)
            # i:index, x_offset:X, 300:Y, length, width, info of tube, message
            self.scene.addItem(rect)
            self.rect_items.append(rect)
            x_offset += length * 25
            i += 1
        self.get_message('Length:{}\nArea:{}'.format(l, a))
        self.illustration.update()

    def menu_sound(self):
        if len(self.L) == 0 or len(self.A) == 0:
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
        if self.audio_name == '':
            self.get_message("No Audio Generated")
        else:
            # open the audio file
            fs, data = wav.read(self.audio_name + '.wav')
            sd.play(data, fs)
            sd.wait()  # wait for the play process to finish

    def generate_image(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        elif len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        elif self.audio_name == '':
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
        if self.audio_name == '':
            self.get_message("No Audio Generated")
        else:
            self.scene.clear()
            # 创建 QPixmap 并加载 PNG 图像
            pixmap = QtGui.QPixmap(self.audio_name + '.png')
            # 创建 QGraphicsPixmapItem 并添加到 QGraphicsScene 中
            pixmap_item = QtWidgets.QGraphicsPixmapItem(pixmap)
            self.scene.addItem(pixmap_item)
            self.illustration.update()

    def menu_scale(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        else:
            value = self.doubleSpinBox_scale.value()
            if value:
                self.L = [x * value for x in self.L]
                self.A = [y * (value ** 2) for y in self.A]
                self.visualization(self.L, self.A)
            else:
                self.get_message('Empty Scale Argument')

    def menu_3d(self):
        threeD = Click3dPrinting()
        threeD.setWindowTitle("3d printing")
        threeD.ConButton.clicked.connect(self.con3d)
        threeD.DetButton.clicked.connect(self.det3d)
        if threeD.exec_():
            pass

    def con3d(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        elif len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        else:
            cy_test.tubemaker_3d(self.L, self.A, self.audio_name)
            stl_file_path = self.audio_name + '_con' + '.stl'
            self.get_message(f'STL file created: {stl_file_path}')

    def det3d(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        elif len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        else:
            cy_test.detachable_tubemaker_3d(self.L, self.A, self.audio_name)
            self.get_message(f'Detachable STL file created')

    def menu_obliviate(self):
        self.scene.clear()
        self.L = []
        self.A = []
        self.index = None
        self.audio_name = ''
        self.get_message('Obliviate! All input has been removed')

    def show_example_a(self):
        self.L = [1, 1, 3, 3, 3, 3, 1, 1]
        self.A = [1, 2, 5, 2, 1, 0.2, 2, 1]
        self.audio_name = 'a'
        self.visualization(self.L, self.A)
        fs = 16000
        tub = Tuben()
        self.fmt, self.Y = tub.get_formants(self.L, self.A)
        x = formantsynt.impulsetrain(fs, 70.0, 1.5)
        y = formantsynt.ffilter(fs, x, self.fmt)
        wav.write(self.audio_name + '.wav', fs, y)
        self.get_message('Audio ' + self.audio_name + '.wav Created')

    def show_example_i(self):
        self.L = [1, 1, 3, 3, 3, 3, 1, 1]
        self.A = [1, 2, 0.2, 1, 2, 5, 2, 1]
        self.audio_name = 'i'
        self.visualization(self.L, self.A)
        fs = 16000
        tub = Tuben()
        self.fmt, self.Y = tub.get_formants(self.L, self.A)
        x = formantsynt.impulsetrain(fs, 70.0, 1.5)
        y = formantsynt.ffilter(fs, x, self.fmt)
        wav.write(self.audio_name + '.wav', fs, y)
        self.get_message('Audio ' + self.audio_name + '.wav Created')

    def show_example_o(self):
        self.L = [2, 6, 6, 2]
        self.A = [0.1, 5, 1, 2]
        self.audio_name = 'o'
        self.visualization(self.L, self.A)
        fs = 16000
        tub = Tuben()
        self.fmt, self.Y = tub.get_formants(self.L, self.A)
        x = formantsynt.impulsetrain(fs, 70.0, 1.5)
        y = formantsynt.ffilter(fs, x, self.fmt)
        wav.write(self.audio_name + '.wav', fs, y)
        self.get_message('Audio ' + self.audio_name + '.wav Created')

    def menu_trajectory(self):
        trajectory = TrajectoryWindow(self)


# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = AppWindow()
    myWindow.show()
    sys.exit(app.exec_())
