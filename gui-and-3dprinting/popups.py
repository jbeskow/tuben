import sys
from qt_test import Ui_TubeN
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, \
    QTableWidgetItem, QDialog, QLineEdit, QMainWindow, QFileDialog, QListWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from formantsynt import synthesize_vowel_sequence


# Receive two inputs
class InputDialogAdd(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input Dialog")
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Choose a file with tube parameters"))
        # Add button to load file
        self.loadButton = QPushButton("Load File", self)
        self.loadButton.setToolTip("Load a file with the first line being length and the second line \n"
                                   "being width (separate with comma)")
        self.loadButton.clicked.connect(self.loadFile)
        mainLayout.addWidget(self.loadButton)

        mainLayout.addWidget(QLabel("Or enter the parameters,\nSeparate by comma(,)"))
        # Create first input row
        row1Layout = QHBoxLayout()
        row1Layout.addWidget(QLabel("Length(s):"))
        self.input1 = QLineEdit(self)
        row1Layout.addWidget(self.input1)
        mainLayout.addLayout(row1Layout)

        # Create second input row
        row2Layout = QHBoxLayout()
        row2Layout.addWidget(QLabel("Area(s):"))
        self.input2 = QLineEdit(self)
        row2Layout.addWidget(self.input2)
        mainLayout.addLayout(row2Layout)

        okButton = QPushButton("OK", self)
        okButton.clicked.connect(self.accept)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)

    def loadFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            with open(file_path, "r") as file:
                lines = file.readlines()
            if len(lines) >= 2:
                self.input1.setText(lines[0].strip('\n'))
                self.input2.setText(lines[1])

    def getInputs(self):
        return self.input1.text(), self.input2.text()


class InputDialogAlter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input Dialog")
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Enter the new tube parameters"))
        # Create first input row
        row1Layout = QHBoxLayout()
        row1Layout.addWidget(QLabel("Length:"))
        self.input1 = QLineEdit(self)
        row1Layout.addWidget(self.input1)
        mainLayout.addLayout(row1Layout)

        # Create second input row
        row2Layout = QHBoxLayout()
        row2Layout.addWidget(QLabel("Area:"))
        self.input2 = QLineEdit(self)
        row2Layout.addWidget(self.input2)
        mainLayout.addLayout(row2Layout)

        okButton = QPushButton("OK", self)
        okButton.clicked.connect(self.accept)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)

    def getInputs(self):
        return self.input1.text(), self.input2.text()


class PlotSelectionDialog(QDialog):
    def __init__(self, options):
        super().__init__()
        self.selected_plots = []
        self.initUI(options)

    def initUI(self, options):
        layout = QVBoxLayout()

        self.listWidget = QListWidget()
        self.listWidget.addItems(options)
        self.listWidget.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.listWidget)

        select_button = QPushButton('Select')
        select_button.clicked.connect(self.select_plots)
        layout.addWidget(select_button)

        self.setLayout(layout)

    def select_plots(self):
        selected_items = self.listWidget.selectedItems()
        self.selected_plots = [item.text() for item in selected_items]
        self.accept()


class FigIllustration(QDialog):
    def __init__(self, fig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Illustration")
        self.fig = fig
        self.file_path = None
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()

        # 添加一个 QLabel 用于显示提示文本
        mainLayout.addWidget(QLabel("Illustration"))
        # 创建一个 FigureCanvas 对象，并将 matplotlib 图像添加到其中
        self.canvas = FigureCanvas(self.fig)
        mainLayout.addWidget(self.canvas)
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_plot)
        mainLayout.addWidget(save_button)
        self.setLayout(mainLayout)

    def save_plot(self):
        # 打开文件保存对话框
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "",
                                                   "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)",
                                                   options=options)
        if file_path:
            self.fig.savefig(file_path)


class Click3dPrinting(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3d Printing")
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Choose a type of tube:"))
        # Create buttons for function selection
        self.ConButton = QPushButton("Continuous", self)
        mainLayout.addWidget(self.ConButton)
        self.DetButton = QPushButton("Detachable", self)
        mainLayout.addWidget(self.DetButton)

        self.setLayout(mainLayout)


class TrajectoryWindow(QWidget):
    def __init__(self, imagePath='vowel_chart.png'):
        super().__init__()
        self.imagePath = imagePath
        self.setWindowTitle("Main Window with Image Click")
        self.originalPixmap = QPixmap(imagePath)
        self.initUI()

    def initUI(self):
        self.mainLayout = QHBoxLayout(self)

        # Table with additional columns for Name and Duration
        self.tableWidget = QTableWidget(0, 4)
        self.tableWidget.setHorizontalHeaderLabels(['F1', 'F2', 'Name', 'Duration'])
        self.addButton = QPushButton('Add Entry', self)
        self.delButton = QPushButton('Delete Entry', self)
        self.sumButton = QPushButton('Synthesize Trajectory', self)

        tableLayout = QVBoxLayout()
        f0Layout = QHBoxLayout()
        f0Layout.setAlignment(Qt.AlignLeft)  # 设置居中对齐
        self.f0Label = QLabel('F0(Hz):', self)
        self.f0Input = QLineEdit(self)
        self.f0Input.setMaximumWidth(100) # 设置输入框的最大宽度为100像素
        self.f0Input.setText("100")
        f0Layout.addWidget(self.f0Label)
        f0Layout.addWidget(self.f0Input)
        f0Layout.setSpacing(10)  # 设置标签和输入框之间的间距为10像素
        tableLayout.addLayout(f0Layout)

        tableLayout.addWidget(self.tableWidget)
        tableLayout.addWidget(self.addButton)
        tableLayout.addWidget(self.delButton)
        tableLayout.addWidget(self.sumButton)


        # Image layout
        imageLayout = QVBoxLayout()
        self.imageLabel = QLabel(self)
        self.imageLabel.setPixmap(self.originalPixmap.scaled(316, 215, Qt.KeepAspectRatio))
        self.imageLabel.setFixedSize(316, 215)
        self.addFromImageButton = QPushButton('Add from Image Click', self)
        imageLayout.addWidget(self.imageLabel)
        imageLayout.addWidget(self.addFromImageButton)

        self.mainLayout.addLayout(tableLayout)
        self.mainLayout.addLayout(imageLayout)

        self.addButton.clicked.connect(lambda: self.addEntry(fmt=(0,0)))
        self.delButton.clicked.connect(self.deleteEntry)
        self.addFromImageButton.clicked.connect(self.addClickPositionToTable)
        self.sumButton.clicked.connect(
            lambda: synthesize_vowel_sequence(fs=16000, formant_sequence=self.list_prepare(),base_freq=int(self.f0Input.text())))

        self.resize(900, 600)

    def addClickPositionToTable(self):
        if self.lastClickPosition:
            x, y = self.lastClickPosition
            # manually calculated scaling
            x = int(2.111 * x + 248.27)
            y = int(-106 / 15 * y + 2300.666)
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QTableWidgetItem(str(x)))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QTableWidgetItem(str(y)))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2, QTableWidgetItem("vowel"))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 3, QTableWidgetItem("1"))
            self.lastClickPosition = None  # Reset after adding

    def addEntry(self,fmt):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        #print(type(fmt)) without lambda fmt is bool?
        for i in range(4):
            if i == 2:  # Name column
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem("vowel"))
            elif i == 3:  # Duration column
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem("1"))
            elif i == 0:
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem(str(int(fmt[0])+1)))
            else:
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem(str(int(fmt[1])+1)))

    def deleteEntry(self):
        selected_rows = set(index.row() for index in self.tableWidget.selectedIndexes())
        for row in sorted(selected_rows, reverse=True):
            self.tableWidget.removeRow(row)

    def list_prepare(self):
        traj_list = []
        for row in range(self.tableWidget.rowCount()):
            traj_list.append(([float(self.tableWidget.item(row, 0).text()),
                               float(self.tableWidget.item(row, 1).text())],
                              float(self.tableWidget.item(row, 3).text())))
        return traj_list

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            clickPosition = self.imageLabel.mapFromGlobal(self.mapToGlobal(event.pos()))
            if 0 <= clickPosition.x() < self.imageLabel.width() and 0 <= clickPosition.y() < self.imageLabel.height():
                x_ratio = self.originalPixmap.width() / self.imageLabel.width()
                y_ratio = self.originalPixmap.height() / self.imageLabel.height()
                scaled_x = int(clickPosition.x() * x_ratio)
                scaled_y = int(clickPosition.y() * y_ratio)
                self.lastClickPosition = (scaled_x, scaled_y)
                self.markPoint(scaled_x, scaled_y)

    def markPoint(self, x, y):
        pixmap = self.originalPixmap.copy()
        painter = QPainter(pixmap)
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(10)
        painter.setPen(pen)
        painter.drawPoint(QPoint(x, y))
        painter.end()
        self.imageLabel.setPixmap(pixmap.scaled(316, 215, Qt.KeepAspectRatio))


# for testing
class MainWindow(QMainWindow, Ui_TubeN):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_add.clicked.connect(self.openInputDialog)
        # self.button.clicked.connect(self.openInputDialog)
        self.L = []
        self.A = []
        # self.setCentralWidget(self.button)

    def openInputDialog(self):
        dialog = InputDialogAdd(self)
        dialog.setWindowTitle("add")
        if dialog.exec_():
            lengths, areas = dialog.getInputs()
            le = [float(l) for l in lengths.split(',')]
            ar = [float(a) for a in areas.split(',')]
            self.L.append(le)
            self.A.append(ar)
            # Process the inputs or pass them to another part of the program here


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
