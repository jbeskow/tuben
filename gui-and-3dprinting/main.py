import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsRectItem, QFileDialog
from PyQt5.QtWidgets import QGraphicsSimpleTextItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsScene
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPolygonF
import scipy.io.wavfile as wav
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from qt_test import Ui_TubeN
import formantsynt
from tuben_gui import Tuben
import tube3dmodel
from popups import InputDialogAdd, InputDialogAlter, TrajectoryWindow, Click3dPrinting, \
    PlotSelectionDialog, FigIllustration
import sounddevice as sd
import pandas as pd


class MyRectItem(QGraphicsRectItem):
    def __init__(self, index, x, y, length, width, la, output_method=None):
        super().__init__(x, y, length, width)
        self.index = index  # save index for each tube section
        self.la = la
        self.setBrush(QColor.fromRgb(200, 0, 0))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)  # to be selebtable
        self.isClicked = False
        self.output_method = output_method

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.isClicked = True
            if self.output_method:
                self.output_method('Index {} clicked\nLength:{}\nArea:{}'.format(self.index, self.la[0], self.la[1]))
        super().mousePressEvent(event)


# Create a subclass of QMainWindow to set up the GUI
class AppWindow(QMainWindow, Ui_TubeN):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_add.clicked.connect(self.menu_add)
        self.pushButton_remove.clicked.connect(self.menu_remove)
        self.pushButton_alter.clicked.connect(self.menu_alter)
        self.doubleSpinBox_scale.setDecimals(1)
        self.doubleSpinBox_scale.setValue(0.0)
        self.pushButton_scale.clicked.connect(self.menu_scale)
        self.pushButton_save.clicked.connect(self.menu_save)
        self.pushButton_sound.clicked.connect(self.menu_sound)
        self.play_audio.clicked.connect(self.play_sound)
        self.pushButton_illustrate.clicked.connect(self.menu_illustrate)
        self.pushButton_3d.clicked.connect(self.menu_3d)
        self.pushButton_obliviate.clicked.connect(self.menu_obliviate)
        self.pushButton_trajectory.clicked.connect(self.menu_trajectory)

        self.setTip()
        self.tub = Tuben()
        self.rect_items = []
        self.scene1 = QGraphicsScene()
        self.illustration.setScene(self.scene1)
        self.add_axis()
        self.scene2 = QGraphicsScene()
        self.graphics_formants.setScene(self.scene2)

        self.selected_plots = []

        self.example_a.clicked.connect(self.show_example_a)
        self.example_i.clicked.connect(self.show_example_i)
        self.example_u.clicked.connect(self.show_example_u)
        self.L = []
        self.A = []
        self.L_all = []
        self.A_all = []
        self.action = []
        self.F_all = []
        self.samplerate = 16000
        self.index = None
        # trajectory window
        self.trajectoryWindow = TrajectoryWindow()

    def get_message(self, message):
        self.input_information_output.clear()
        self.input_information_output.insertPlainText(message)

    def get_index(self):
        if self.rect_items is not None:
            for item in self.rect_items:
                if item.isClicked:
                    self.index = item.index
                    item.isClicked = False

    def menu_add(self):
        dialog = InputDialogAdd(self)
        dialog.setWindowTitle("add")
        if dialog.exec_():
            lengths, areas = dialog.getInputs()
            match_l = bool(re.match(r'^\d+(\.\d+)?(,\s?\d+(\.\d+)?)*$', lengths))
            match_a = bool(re.match(r'^\d+(\.\d+)?(,\s?\d+(\.\d+)?)*$', lengths))
            if lengths == '' or areas == '':
                self.get_message('Empty Input Value')
            elif match_l and match_a:
                le = [float(l) for l in lengths.split(',')]
                ar = [float(a) for a in areas.split(',')]
                if len(le) == len(ar) and len(le) >= 1:
                    self.get_index()
                    if len(self.L) == 0 or len(self.A) == 0:
                        # create tube sections
                        self.L = le
                        self.A = ar
                    elif self.index is not None:
                        # add new sections after given index of the tube
                        if self.index < len(self.L):
                            self.L[self.index+1:self.index+1] = le
                            self.A[self.index+1:self.index+1] = ar
                            self.index = None
                        else:
                            self.L += le
                            self.A += ar
                            self.index = None
                    elif self.index is None:
                        # add new sections after the current tube
                        self.L += le
                        self.A += ar
                else:
                    self.get_message('Invalid input: lengths and areas lists must be of equal length')
                if len(self.L) == len(self.A):
                    self.visualization(self.L, self.A)
                    self.visualize_formants()
                    self.action.append('Add')
                    self.L_all.append(self.L)
                    self.A_all.append(self.L)
                    fmt, _ = self.tub.get_formants(self.L, self.A)
                    self.F_all.append(fmt.tolist())
            else:
                self.get_message('Invalid input, please try again')

    def menu_remove(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        else:
            self.get_index()
            if self.index is not None:  # pop the section that has been clicked
                self.L.pop(self.index)
                self.A.pop(self.index)
                if len(self.L) == len(self.A) and len(self.L) > 0:
                    self.visualization(self.L, self.A)
                    self.visualize_formants()
                    self.action.append('Remove')
                    self.L_all.append(self.L)
                    self.A_all.append(self.L)
                    fmt, _ = self.tub.get_formants(self.L, self.A)
                    self.F_all.append(fmt.tolist())
                else:
                    self.scene1.clear()
                    self.add_axis()
                    self.get_message('Empty Input Value')
                self.index = None
            else:
                self.get_message('Select a section first')

    def menu_alter(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        else:
            self.get_index()
            if self.index is not None:
                try:
                    dialog = InputDialogAlter(self)
                    dialog.setWindowTitle("alter")
                    if dialog.exec_():
                        new_length, new_area = dialog.getInputs()
                        l = float(new_length)
                        a = float(new_area)
                        if l > 0 and a > 0:
                            self.L[self.index] = l
                            self.A[self.index] = a
                            self.visualization(self.L, self.A)
                            self.visualize_formants()
                            self.action.append('Alter')
                            self.L_all.append(self.L)
                            self.A_all.append(self.L)
                            fmt, _ = self.tub.get_formants(self.L, self.A)
                            self.F_all.append(fmt.tolist())
                        else:
                            self.get_message('Invalid Input: new parameter(s) should be larger than 0')
                        self.index = None
                except ValueError:
                    self.get_message('Invalid Input: new parameter(s) should be numbers')
            else:
                self.get_message('Select a section first')

    def menu_save(self):
        history = pd.DataFrame()
        history['Action'] = self.action
        history['Length'] = self.L_all
        history['Area'] = self.A_all
        history['Predicted Formants'] = self.F_all
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            if not file_path.endswith(".csv"):
                file_path += ".csv"
            history.to_csv(file_path, encoding='UTF-8', index=False)

    def add_axis(self):
        # horizontal axis
        self.scene1.addLine(0, 150, 500, 150)
        # vertical axis
        self.scene1.addLine(0, -100, 0, 150)

        # horizontal arrow
        arrow = QPolygonF([QPointF(505, 150), QPointF(500, 155), QPointF(500, 145)])
        self.scene1.addPolygon(arrow)

        # vertical arrow
        arrow = QPolygonF([QPointF(0, -105), QPointF(5, -100), QPointF(-5, -100)])
        self.scene1.addPolygon(arrow)

        # horizontal scale
        for x in range(25, 501, 25):
            tick = QGraphicsLineItem(x, 140, x, 150)
            self.scene1.addItem(tick)

            # scale values
            text = QGraphicsSimpleTextItem(str(int(x/25)))
            text.setPos(x-5, 160)
            self.scene1.addItem(text)

        # vertical scale
        for y in range(25, 251, 25):
            tick = QGraphicsLineItem(0, 150 - y, 5, 150 - y)
            self.scene1.addItem(tick)

            # scale values
            text = QGraphicsSimpleTextItem(str(int(y/25)))
            text.setPos(-30, 140 - y)
            self.scene1.addItem(text)

        self.add_label(-20, 160, "0")
        self.add_label(-20, 180, "Lips")
        self.add_label(520, 150, "X (cm)")
        self.add_label(450, 180, "Glottis")
        self.add_label(10, -120, "Y (cm\u00B2)")

    def add_label(self, x, y, text):
        label = QGraphicsTextItem(text)
        label.setPos(x, y)
        self.scene1.addItem(label)

    def visualization(self, l, a):
        self.scene1.clear()
        self.add_axis()
        x_offset = 0
        i = 0
        for length, width in zip(l, a):
            la = [l[i], a[i]]
            rect = MyRectItem(i, x_offset, 150-int(width*25), length * 25, width * 25, la, self.get_message)
            # i:index, x_offset:X, 50:Y, length, width, info of tube, message
            self.scene1.addItem(rect)
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
            fmt, _ = self.tub.get_formants(self.L, self.A)
            x = formantsynt.impulsetrain(self.samplerate, 70.0, 1.5)
            y = formantsynt.ffilter(self.samplerate, x, fmt)
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "", "WAV Files (*.wav);;All Files (*)")
            if file_path:
                if not file_path.endswith(".wav"):
                    file_path += ".wav"
                wav.write(file_path, self.samplerate, y)
                self.get_message(file_path + '.wav Created')

    def play_sound(self):
        fmt, _ = self.tub.get_formants(self.L, self.A)
        x = formantsynt.impulsetrain(self.samplerate, 70.0, 1.5)
        y = formantsynt.ffilter(self.samplerate, x, fmt)
        data = np.array(y)
        data_float32 = data.astype(np.float32)
        sd.play(data_float32, self.samplerate)
        sd.wait()

    def generate_image(self):
        fig, ax = plt.subplots(len(self.selected_plots), 1, figsize=(8, len(self.selected_plots) * 3))
        if len(self.selected_plots) == 1:
            ax = [ax]

        # 生成子图
        x = 0
        plot_index = 0
        F = np.arange(1, 8000)
        fmt, Y = self.tub.get_formants(self.L, self.A)
        fs = 16000
        f, h = formantsynt.get_transfer_function(fs, fmt)
        if 'tube' in self.selected_plots:
            for l, a in zip(self.L, self.A):
                ax[plot_index].add_patch(Rectangle((x, 0), l, a, ls='--', ec='k'))
                x += l
            ax[plot_index].set_xlim([0, x])
            ax[plot_index].set_ylim([0, max(self.A) * 1.1])
            ax[plot_index].set_title('tube')
            ax[plot_index].set_xlabel('distance from lips (cm)')
            ax[plot_index].set_ylabel('area ($cm^2$)')
            plot_index += 1

        if 'peak function' in self.selected_plots:
            ax[plot_index].plot(F, Y, ':')
            ax[plot_index].plot(F[fmt], Y[fmt], '.')
            ax[plot_index].set_title('peakfunction: determinant')
            ax[plot_index].set_xlabel('frequency (Hz)')
            plot_index += 1

        if 'transfer function' in self.selected_plots:
            ax[plot_index].set_title('transfer function')
            ax[plot_index].set_xlabel('frequency (Hz)')
            ax[plot_index].set_ylabel('dB')
            ax[plot_index].plot(f, h)
            plot_index += 1
        plt.tight_layout()
        return fig

    def menu_illustrate(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        elif len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        else:
            options = ['tube', 'peak function', 'transfer function']
            dialog = PlotSelectionDialog(options)
            if dialog.exec_():
                self.selected_plots = dialog.selected_plots
            if len(self.selected_plots) == 0:
                self.get_message('Empty input: choose at least one option to generate the image')
            else:
                fig = self.generate_image()
                plot = FigIllustration(fig)
                plot.setWindowTitle("Illustration")
                plot.exec_()

    def menu_scale(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        else:
            value = self.doubleSpinBox_scale.value()
            if value:
                self.L = [x * value for x in self.L]
                self.A = [y * (value ** 2) for y in self.A]
                self.visualization(self.L, self.A)
                self.visualize_formants()
                self.action.append('Scale')
                self.L_all.append(self.L)
                self.A_all.append(self.L)
                fmt, _ = self.tub.get_formants(self.L, self.A)
                self.F_all.append(fmt.tolist())
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
        elif sum(self.L) > 22:
            self.get_message('Invalid input: for printable purpose, the total length should be no longer than 22 cm')
        else:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save STL File", "",
                                                       "All Files (*)",
                                                       options=options)
            if file_path:
                if not file_path.endswith(".stl"):
                    file_path += "_con.stl"
                tube3dmodel.tubemaker_3d(self.L, self.A, file_path)
                self.get_message(f'STL file created: {file_path}')

    def det3d(self):
        if len(self.L) == 0 or len(self.A) == 0:
            self.get_message('Empty Input Value')
        elif len(self.L) != len(self.A):
            self.get_message('Invalid input: lengths and areas lists must be of equal length')
        else:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Save STL File", "",
                                                       "All Files (*)",
                                                       options=options)
            if file_path:
                tube3dmodel.detachable_tubemaker_3d(self.L, self.A, file_path)
                self.get_message(f'Detachable STL file created')

    def menu_obliviate(self):
        self.scene1.clear()
        self.scene2.clear()
        self.add_axis()
        self.L = []
        self.A = []
        self.index = None
        self.get_message('Obliviate! All input has been removed')

    def show_example_a(self):
        self.L = [1.5, 0.5, 3.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        self.A = [5, 6.5, 8, 6.5, 5, 4, 3.2, 1.6, 2.6, 2, 1.6, 1.3, 1, 0.65, 1, 1.6, 2.6, 4, 1, 1.3, 1.6, 2.6]
        self.visualization(self.L, self.A)
        self.visualize_formants()

    def show_example_i(self):
        self.L = [1, 0.5, 0.5, 0.5, 0.5, 3, 0.5, 0.5, 0.5, 0.5, 1, 4, 1, 1, 0.5, 0.5]
        self.A = [4, 3.2, 1.6, 1.3, 1, 0.65, 1.3, 2.6, 4, 6.5, 8, 10.5, 8, 2, 2.6, 3.2]
        self.visualization(self.L, self.A)
        self.visualize_formants()

    def show_example_u(self):
        self.L = [1, 1, 0.5, 0.5, 0.5, 2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5,
                  0.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 0.5, 0.5, 1, 1.5, 1, 1]
        self.A = [0.65, 0.32, 2, 5, 10.5, 13, 10.5, 8, 6.5, 5, 3.2, 2.6, 2,
                  1.6, 1.3, 2, 1.6, 1, 1.3, 1.6, 3.2, 5, 8, 10.5, 2, 2.6]
        self.visualization(self.L, self.A)
        self.visualize_formants()

    def menu_trajectory(self):
        # if it is already shown then nothing happens
        self.trajectoryWindow.show()
        if not self.L:
            return
        # TODO pick a better one between these two
        # self.fmt, self.Y = tub.get_formants(self.L, self.A)
        fmt, _ = self.tub.get_formants(self.L, self.A)
        self.trajectoryWindow.addEntry(fmt=fmt)
        self.trajectoryWindow.raise_()
        self.trajectoryWindow.activateWindow()

    def visualize_formants(self):
        self.scene2.clear()
        F = np.arange(1, 8000)
        fmt, Y = self.tub.get_formants(self.L, self.A)
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(F, Y, ':')
        ax.plot(F[fmt], Y[fmt], '.')
        for idx in fmt:
            x_val = F[idx]
            y_val = Y[idx]
            ax.axvline(x_val, color='gray', linestyle='--')
            ax.annotate(f'{x_val}', xy=(x_val, y_val), xytext=(x_val, y_val + 0.05),
                        textcoords='data', ha='center', va='bottom', arrowprops=dict(arrowstyle='-', linestyle=':'))
        ax.annotate('frequency (Hz)', xy=(1.1, 0), xycoords='axes fraction', ha='right', va='bottom')
        fig.patch.set_facecolor((234 / 255, 233 / 255, 255 / 255))
        canvas = FigureCanvas(fig)
        self.scene2.addWidget(canvas)
        self.graphics_formants.setScene(self.scene2)

    def setTip(self):
        self.pushButton_add.setToolTip('This button is for adding tube parameters in two ways.\n'
                                       'Load a file or manually type in the parameters')
        self.pushButton_remove.setToolTip('This button is for deleting a tube section.\n'
                                          'You can click the section and click this button to remove it')
        self.pushButton_alter.setToolTip('This button is for changing the length and/or width '
                                         'of a certain tube section.\n'
                                         'You can click the section and click this button to enter the new parameters')
        self.pushButton_scale.setToolTip('This button is for changing the entire tube proportionally.\n'
                                         'You can type in or click the spinbox on the left to set the proportion\n'
                                         'and click this button to get new tube parameters')
        self.pushButton_save.setToolTip('This button is for saving all the changes you have made.')
        self.pushButton_sound.setToolTip('This button is for generating .wav file with given tube parameters.')
        self.play_audio.setToolTip('Click this button to hear the synthesized sound based on given tube parameters.')
        self.pushButton_illustrate.setToolTip('This button is for generating tube related illustration.\n'
                                              'With Tube model, Peak function plot and Transfer function options\n'
                                              'You can save the plot as a .png file')
        self.pushButton_3d.setToolTip('This button is for generating 3D-printable file (.stl)')
        self.example_a.setToolTip('This button is an example of tube parameters that sounds like /a/.\n'
                                  'You can click this button to get the parameters then test them with other buttons')
        self.example_i.setToolTip('This button is an example of tube parameters that sounds like /i/.\n'
                                  'You can click this button to get the parameters then test them with other buttons')
        self.example_u.setToolTip('This button is an example of tube parameters that sounds like /u/.\n'
                                  'You can click this button to get the parameters then test them with other buttons')
        self.pushButton_obliviate.setToolTip('This button is for deleting all tube parameters.\n'
                                             'Name after a spell in Harry Potter')
        self.pushButton_trajectory.setToolTip('This button is for setting the current tube parameters\n'
                                              'as an anchor for vowel sequence synthesis.')
        self.pushButton_explore.setToolTip('Under Construction')


# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = AppWindow()
    myWindow.show()
    sys.exit(app.exec_())
