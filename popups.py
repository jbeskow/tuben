import sys
from qt_test import Ui_TubeN
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, \
    QTableWidgetItem, QDialog, QLineEdit, QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from formantsynt import synthesize_vowel_sequence


# 接收两个输入
class InputDialogAdd(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input Dialog")
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Enter the tube parameters,\nSeparate by comma(,)"))
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
        mainLayout.addWidget(QLabel("peak & transfer function"))
        # 创建一个 FigureCanvas 对象，并将 matplotlib 图像添加到其中
        self.canvas = FigureCanvas(self.fig)
        mainLayout.addWidget(self.canvas)
        self.setLayout(mainLayout)


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

        self.addButton.clicked.connect(self.addEntry)
        self.delButton.clicked.connect(self.deleteEntry)
        self.addFromImageButton.clicked.connect(self.addClickPositionToTable)
        self.sumButton.clicked.connect(
            lambda: synthesize_vowel_sequence(fs=16000, formant_sequence=self.list_prepare()))

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

    def addEntry(self, fmt=(0, 0)):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        for i in range(4):
            if i == 2:  # Name column
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem("vowel"))
            elif i == 3:  # Duration column
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem("1"))
            elif i == 0:
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem(str(fmt[0])))
            else:
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem(str(fmt[1])))

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


# 壳子 测试用
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
            print(type(lengths))
            print("Length(s):", lengths)
            print("Area(s):", areas)
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
