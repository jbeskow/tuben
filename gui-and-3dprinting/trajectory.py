import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, \
    QTableWidgetItem
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint
from formantsynt import synthesize_vowel_sequence
import base64
from vowel_chart_png import img


tmp = open('vowel_chart.png', 'wb')
tmp.write(base64.b64decode(img))
tmp.close()


class MyWindow(QWidget):
    def __init__(self, imagePath):
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
        self.sumButton.clicked.connect(lambda: synthesize_vowel_sequence(fs=16000, formant_sequence=self.list_prepare()))

        self.resize(900, 600)

    def addClickPositionToTable(self):
        if self.lastClickPosition:
            x, y = self.lastClickPosition
            # manually calculated scaling
            x = int(2.111*x+248.27)
            y = int(-106/15*y+2300.666)
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QTableWidgetItem(str(x)))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QTableWidgetItem(str(y)))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2, QTableWidgetItem("vowel"))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 3, QTableWidgetItem("1"))
            self.lastClickPosition = None  # Reset after adding

    def addEntry(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        for i in range(4):
            if i == 2:  # Name column
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem("vowel"))
            elif i == 3:  # Duration column
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem("1"))
            else:
                self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i, QTableWidgetItem("0"))

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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.initUI()
        self.childWindow = MyWindow('vowel_chart.png')  # Create instance of your child window

    def initUI(self):
        layout = QVBoxLayout(self)
        openChildWindowButton = QPushButton('Open Child Window', self)
        setFeaturesButton = QPushButton('Set Features in Child Window', self)

        layout.addWidget(openChildWindowButton)
        layout.addWidget(setFeaturesButton)

        openChildWindowButton.clicked.connect(self.openChildWindow)
        setFeaturesButton.clicked.connect(self.setFeaturesInChild)

    def openChildWindow(self):
        self.childWindow.show()  # Show the child window in a non-blocking way

    def setFeaturesInChild(self):
        # Example of setting features in the child window
        # This can be adapted to set whatever data or features you need
        if self.childWindow.isVisible():
            self.childWindow.addEntry()  # Add an entry to the child window's table


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
