import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsRectItem, QFileDialog, QGraphicsScene
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsLineItem, QSizePolicy, QVBoxLayout
from PyQt5.QtWidgets import QPushButton, QGraphicsProxyWidget
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QKeyEvent, QFont, QPen
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sounddevice as sd
from main_window_ui import Ui_TubeN
import formantsynt
from tuben_gui import Tuben
import tube3dmodel
from popups import InputDialogAdd, InputDialogAlter, Click3dPrinting, \
    PlotSelectionDialog, FigIllustration
import math
# pyuic5 -o main_window_ui.py main_window.ui
# pyinstaller --onefile --icon=icon.ico --noconsole Tuben_new.py


class MyRectItem(QGraphicsRectItem):
    def __init__(self, index, x, y, length, width, la, output_method=None):
        super().__init__(x, y, length, width)
        self.index = index  # index for each tube section
        self.la = la  # [length, area]
        # Fill color: light blue with transparency (alpha = 200, range 0–255)
        brush = QColor(41, 109, 186, 200)
        self.setBrush(brush)
        # Outline color: dark gray
        pen = QPen(QColor(96, 96, 96))
        pen.setWidth(0)  # very thin border
        self.setPen(pen)

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
        # self.play_audio.clicked.connect(self.play_sound)
        self.pushButton_illustrate.clicked.connect(self.menu_illustrate)
        self.pushButton_3d.clicked.connect(self.menu_3d)
        self.pushButton_obliviate.clicked.connect(self.menu_obliviate)

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
        self.samplerate = 16000
        self.index = None
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
                    fmt, _ = self.tub.get_formants(self.L, self.A)
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
                        else:
                            self.get_message('Invalid Input: new parameter(s) should be larger than 0')
                        self.index = None
                except ValueError:
                    self.get_message('Invalid Input: new parameter(s) should be numbers')
            else:
                self.get_message('Select a section first')


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
                label.setFont(QFont("Book Antiqua", 3))
                text_rect = label.boundingRect()
                label.setPos(y_axis_x - text_rect.width() - 2, y_pos - text_rect.height() / 2)
                self.scene1.addItem(label)
        unit_label_y = QGraphicsTextItem("cm²")
        unit_label_y.setFont(QFont("Book Antiqua", 3, QFont.Bold))
        unit_label_y.setPos(
            y_axis_x - 15,  # shift left by 15
            max_area_int * scale_y + 3)  # at the bottom of y-axis with 3 units further down
        self.scene1.addItem(unit_label_y)

        self.play_button = QPushButton()
        self.play_button.setFixedSize(35, 25)
        self.play_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)
        self.play_button.setText("▶")
        font = self.play_button.font()
        font.setBold(True)
        font.setPointSize(8)
        self.play_button.setFont(font)
        self.play_button.clicked.connect(self.play_sound)

        proxy = QGraphicsProxyWidget()
        proxy.setWidget(self.play_button)
        proxy.setPos(-50, -15)
        self.scene1.addItem(proxy)

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
                label.setFont(QFont("Book Antiqua", 3))
                text_rect = label.boundingRect()
                text_width = text_rect.width()
                text_height = text_rect.height()
                label.setPos(x_pos - text_width / 2, x_axis_y + 2)
                self.scene1.addItem(label)
        unit_label_x = QGraphicsTextItem("cm")
        unit_label_x.setFont(QFont("Book Antiqua", 3, QFont.Bold))
        unit_label_x.setPos(max_length_int * scale_x + 2, x_axis_y + 2)
        self.scene1.addItem(unit_label_x)

        # add "Lips" at the left end of X-axis
        lips_label = QGraphicsTextItem("lips")
        lips_label.setFont(QFont("Book Antiqua", 3))
        lips_label.setPos(0, max_area_int * scale_y-5)
        self.scene1.addItem(lips_label)

        # add "Glottis" at the right end of X-axis
        glottis_label = QGraphicsTextItem("glottis")
        glottis_label.setFont(QFont("Book Antiqua", 3))
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

        for i, idx in enumerate(fmt, start=1):
            x_val = F[idx]  # formant frequency
            self.ax.axvline(x_val, color='pink', linestyle='--')  # draw vertical line
            # find the nearest index in f to get amplitude (dB)
            nearest_idx = np.argmin(np.abs(f - x_val))
            y_val = h[nearest_idx]
            if i % 2 == 1:  # odd index (1st, 3rd): label above peak
                self.ax.text(x_val, y_val, f"{x_val}",
                             ha="center", va="bottom", fontsize=17, fontweight="bold")
            else:  # even index (2nd, 4th): label below peak
                self.ax.text(x_val, y_val - 14, f"{x_val}",
                             ha="center", va="top", fontsize=17, fontweight="bold")

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
        # self.play_audio.setToolTip('Click this button to hear the synthesized sound based on given tube parameters.')
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

# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = AppWindow()
    myWindow.show()
    sys.exit(app.exec_())
