import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsRectItem, QFileDialog, QGraphicsScene
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsLineItem, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QKeyEvent, QFont
import scipy.io.wavfile as wav
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sounddevice as sd
import pandas as pd
from new_main_window_2 import Ui_TubeN
import formantsynt
from tuben_gui import Tuben
import tube3dmodel
from popups import InputDialogAdd, InputDialogAlter, TrajectoryWindow, Click3dPrinting, \
    PlotSelectionDialog, FigIllustration
import base64
import math

# pyinstaller --onefile --icon=icon.ico --noconsole Tuben.py

img = "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"
tmp = open('vowel_chart.png', 'wb')
tmp.write(base64.b64decode(img))
tmp.close()


class MyRectItem(QGraphicsRectItem):
    def __init__(self, index, x, y, length, width, la, output_method=None):
        super().__init__(x, y, length, width)
        self.index = index  # index for each tube section
        self.la = la  # [length, area]
        self.setBrush(QColor.fromRgb(100, 120, 200))
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)  # to be selectable
        self.isClicked = False
        self.output_method = output_method

    def mousePressEvent(self, event):
        # Check if the mouse button pressed is the left button
        if event.button() == Qt.LeftButton:
            # Clear selection for all other Tube items
            for item in self.scene().items():
                # Check if the item is an instance of MyRectItem
                if isinstance(item, MyRectItem):
                    item.isClicked = False  # Reset its 'isClicked' state to False
            self.isClicked = True  # Now this item is 'selected'
            if self.output_method:
                self.output_method(
                    f'Index {self.index} clicked\nLength:{self.la[0]}\nArea:{self.la[1]}'
                )

# Create a subclass of QMainWindow to set up the GUI
class AppWindow(QMainWindow, Ui_TubeN):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setMinimumSize(400, 300)
        self.setMaximumSize(16777215, 16777215)
        self.pushButton_add.clicked.connect(self.menu_add)
        self.pushButton_remove.clicked.connect(self.menu_remove)
        self.pushButton_alter.clicked.connect(self.menu_alter)
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
        # Ensure that the QGraphicsView can receive focus and handle keyboard events
        self.illustration.setFocusPolicy(Qt.StrongFocus)
        self.illustration.installEventFilter(self)
        self.installEventFilter(self)  # Install an event filter to capture keyboard events

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

    def add_axis(self, l, a, scale_x=15, scale_y=8):
        """
        Add coordinate axes
        Y-axis: positioned at the left edge of the leftmost Tube, unit: cm²
        X-axis: positioned at the midpoint of the leftmost Tube, unit: cm
        """
        if not l or not a:
            return

        # total length of the tube
        total_length = sum(l)

        # area of the first tube
        first_area = a[0]
        first_rect_height = first_area * scale_y

        # at the left edge of the first Tube
        y_axis_x = 0
        # at the midpoint of the first Tube
        x_axis_y = -first_rect_height / 2 + first_rect_height / 2

        # Y-axis
        max_area = max(a)
        max_area_int = math.ceil(max_area / 2 + 1)  # Round up for axis range
        y_axis = QGraphicsLineItem(
            y_axis_x,
            -max_area_int * scale_y,
            y_axis_x,
            max_area_int * scale_y
        )
        self.scene1.addItem(y_axis)
        # draw Y-axis ticks and labels
        for cm2 in range(-max_area_int, max_area_int + 1):
            if cm2 == 0:
                continue
            y_pos = -cm2 * scale_y
            tick = QGraphicsLineItem(y_axis_x, y_pos, y_axis_x + 2, y_pos)
            self.scene1.addItem(tick)

            if cm2 % 2 == 0:  # label every 2 cm2
                label_value = abs(cm2)
                label = QGraphicsTextItem(str(label_value))
                label.setFont(QFont("Arial", 3))
                text_rect = label.boundingRect()
                label.setPos(y_axis_x - text_rect.width() - 2, y_pos - text_rect.height() / 2)
                self.scene1.addItem(label)
        unit_label_y = QGraphicsTextItem("cm²")
        unit_label_y.setFont(QFont("Arial", 3, QFont.Bold))
        unit_label_y.setPos(
            y_axis_x - 15,  # shift left by 15
            max_area_int * scale_y + 3)  # at the bottom of y-axis with 3 units further down
        self.scene1.addItem(unit_label_y)

        # X-axis
        max_length_int = math.ceil(total_length)
        x_axis = QGraphicsLineItem(
            y_axis_x, x_axis_y,
            max_length_int * scale_x, x_axis_y
        )
        self.scene1.addItem(x_axis)

        for cm in range(0, max_length_int + 1):
            if cm == 0:
                continue
            x_pos = cm * scale_x
            tick = QGraphicsLineItem(x_pos, x_axis_y - 2, x_pos, x_axis_y)
            self.scene1.addItem(tick)

            if cm % 2 == 0:  # label every 2 cm
                label = QGraphicsTextItem(str(cm))
                label.setFont(QFont("Arial", 3))
                text_rect = label.boundingRect()
                text_width = text_rect.width()
                text_height = text_rect.height()
                label.setPos(x_pos - text_width / 2, x_axis_y + 2)  # 居中对齐
                self.scene1.addItem(label)
        unit_label_x = QGraphicsTextItem("cm")
        unit_label_x.setFont(QFont("Arial", 3, QFont.Bold))
        unit_label_x.setPos(max_length_int * scale_x + 2, x_axis_y + 2)
        self.scene1.addItem(unit_label_x)

        # add "Lips" at the left end of X-axis
        lips_label = QGraphicsTextItem("lips")
        lips_label.setFont(QFont("Verdana", 3))
        lips_label.setPos(0, max_area_int * scale_y-5)
        self.scene1.addItem(lips_label)

        # add "Glottis" at the right end of X-axis
        glottis_label = QGraphicsTextItem("glottis")
        glottis_label.setFont(QFont("Verdana", 3))
        glottis_label.setPos(total_length * scale_x-10, max_area_int * scale_y-5)
        self.scene1.addItem(glottis_label)

    def get_rect_with_margin(self, rect, margin_factor=1.5):
        """
        Return a QRectF expanded by margin_factor.
        bigger margin_factor means smaller tube
        """
        return rect.adjusted(
            -rect.width() * (margin_factor - 1) / 2,
            -rect.height() * (margin_factor - 1) / 2,
            rect.width() * (margin_factor - 1) / 2,
            rect.height() * (margin_factor - 1) / 2,
        )

    def visualization(self, l, a):
        self.scene1.clear()
        x_offset = 0
        scale_x = 15
        scale_y = 8

        for i, (length, width) in enumerate(zip(l, a)):
            rect_length = length * scale_x
            rect_height = width * scale_y
            rect_y = -rect_height / 2  # center on X-axis
            rect = MyRectItem(
                i,
                x_offset,
                rect_y,
                rect_length,
                rect_height,
                [length, width],
                self.get_message
            )
            self.scene1.addItem(rect)
            self.rect_items.append(rect)
            x_offset += rect_length

        self.add_axis(l, a, scale_x, scale_y)
        # adjust view to fit scene with margin
        rect = self.scene1.itemsBoundingRect()
        rect_with_margin = self.get_rect_with_margin(rect)
        self.get_message(f'Length:{l}\nArea:{a}')
        self.illustration.fitInView(rect_with_margin, Qt.KeepAspectRatio)
        self.illustration.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.scene1.itemsBoundingRect()
        rect_with_margin = self.get_rect_with_margin(rect)
        self.illustration.fitInView(rect_with_margin, Qt.KeepAspectRatio)

    def _change_area(self, index, delta):
        self.A[index] = round(max(0.1, self.A[index] + delta), 1)

    def _change_length(self, index, delta):
        self.L[index] = round(max(0.1, self.L[index] + delta), 1)

    def eventFilter(self, obj, event):
        # handle keyboard input for selected Tube
        if event.type() == QEvent.KeyPress:
            if isinstance(event, QKeyEvent):
                self.get_index()
                if self.index is not None:
                    step = 0.1  # increment/decrement for length/area
                    # map keys to actions
                    key_map = {
                        Qt.Key_Up: lambda: self._change_area(self.index, step),
                        Qt.Key_Down: lambda: self._change_area(self.index, -step),
                        Qt.Key_Right: lambda: self._change_length(self.index, step),
                        Qt.Key_Left: lambda: self._change_length(self.index, -step)
                    }
                    if event.key() in key_map:
                        key_map[event.key()]()  # apply change
                        self.visualization(self.L, self.A)
                        self.visualize_formants()
                        return True
        return super().eventFilter(obj, event)

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
                self.get_message(file_path + ' Created')

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
                tube3dmodel.tubemaker_3d(self.L, self.A, file_path)
                self.get_message(f'STL file created: {file_path}.stl')

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
        if hasattr(self, 'formants_canvas') and self.formants_canvas:
            layout = self.graphics_formants.layout()
            if layout:
                layout.removeWidget(self.formants_canvas)  # remove from layout
            self.formants_canvas.setParent(None)  # detach from parent
            del self.formants_canvas
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
        # Get the layout of the QWidget; create one if it doesn't exist
        layout = self.graphics_formants.layout()
        if layout is None:
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            self.graphics_formants.setLayout(layout)

        # Create Figure and Canvas the first time
        if not hasattr(self, 'formants_canvas'):
            self.fig, self.ax = plt.subplots(figsize=(10, 3))
            self.formants_canvas = FigureCanvas(self.fig)
            self.formants_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(self.formants_canvas)
            self.graphics_formants.setStyleSheet("background-color: white;")
            # Create top axis only once
            self.ax_top = self.ax.twiny()
            for spine in ['top', 'right', 'left', 'bottom']:
                self.ax_top.spines[spine].set_visible(False)
            self.ax_top.xaxis.set_tick_params(direction='out', pad=5)
        else:
            # Clear Axes but keep the Canvas
            self.ax.clear()

        # Compute formants
        F = np.arange(1, 8000)
        fmt, Y = self.tub.get_formants(self.L, self.A)
        fs = 16000
        f, h = formantsynt.get_transfer_function(fs, fmt)

        self.ax.plot(f, h)  #
        self.ax.set_ylabel('dB', fontsize=15, fontweight='bold')
        self.ax.tick_params(axis='both', labelsize=20)

        for idx in fmt:
            x_val = F[idx]
            self.ax.axvline(x_val, color='pink', linestyle='--')

        # Update top axis with formant labels
        self.ax_top.set_xlim(self.ax.get_xlim())
        self.ax_top.set_xticks([F[idx] for idx in fmt])
        self.ax_top.set_xticklabels([f'{F[idx]}' for idx in fmt],
                                    fontsize=15, fontweight='bold')

        # Refresh the FigureCanvas to display the updated plot
        self.formants_canvas.draw()

    def setTip(self):
        self.pushButton_add.setToolTip('This button adds tube parameters in two ways.\n'
                                       'Load a file or manually type in the parameters')
        self.pushButton_remove.setToolTip('This button deletes a tube section.\n'
                                          'You can click the section and click this button to remove it')
        self.pushButton_alter.setToolTip('This button changes the length and/or width '
                                         'of a certain tube section.\n'
                                         'You can click the section and click this button to enter the new parameters')
        self.pushButton_save.setToolTip('This button saves all the changes you have made.')
        self.pushButton_sound.setToolTip('This button generates .wav file with given tube parameters.')
        self.play_audio.setToolTip('Click this button to hear the synthesized sound based on given tube parameters.')
        self.pushButton_illustrate.setToolTip('This button generates tube related illustration.\n'
                                              'With Tube model, Peak function plot and Transfer function options\n'
                                              'You can save the plot as a .png file')
        self.pushButton_3d.setToolTip('This button generates 3D-printable file (.stl)')
        self.example_a.setToolTip('This button is an example of tube parameters that sounds like /a/.\n'
                                  'You can click this button to get the parameters then test them with other buttons')
        self.example_i.setToolTip('This button is an example of tube parameters that sounds like /i/.\n'
                                  'You can click this button to get the parameters then test them with other buttons')
        self.example_u.setToolTip('This button is an example of tube parameters that sounds like /u/.\n'
                                  'You can click this button to get the parameters then test them with other buttons')
        self.pushButton_obliviate.setToolTip('This button deletes all tube parameters.\n'
                                             'Name after a spell in Harry Potter')
        self.pushButton_trajectory.setToolTip('This button sets the current tube parameters\n'
                                              'as an anchor for vowel sequence synthesis.')


# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = AppWindow()
    myWindow.show()
    sys.exit(app.exec_())
