import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint

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
        self.sumButton = QPushButton('Calculate Sum of Positions', self)

        tableLayout = QVBoxLayout()
        tableLayout.addWidget(self.tableWidget)
        tableLayout.addWidget(self.addButton)
        tableLayout.addWidget(self.delButton)
        tableLayout.addWidget(self.sumButton)

        # Image layout
        imageLayout = QVBoxLayout()
        self.imageLabel = QLabel(self)
        self.imageLabel.setPixmap(self.originalPixmap.scaled(437, 293, Qt.KeepAspectRatio))
        self.imageLabel.setFixedSize(437, 293)
        self.addFromImageButton = QPushButton('Add from Image Click', self)
        imageLayout.addWidget(self.imageLabel)
        imageLayout.addWidget(self.addFromImageButton)

        self.mainLayout.addLayout(tableLayout)
        self.mainLayout.addLayout(imageLayout)

        self.addButton.clicked.connect(self.addEntry)
        self.delButton.clicked.connect(self.deleteEntry)
        self.addFromImageButton.clicked.connect(self.addClickPositionToTable)
        self.sumButton.clicked.connect(self.calculateSumOfPositions)

        self.resize(900, 600)

    def addClickPositionToTable(self):
        if self.lastClickPosition:
            x, y = self.lastClickPosition
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

    def calculateSumOfPositions(self):
        total_x = total_y = 0
        for row in range(self.tableWidget.rowCount()):
            total_x += int(self.tableWidget.item(row, 0).text())
            total_y += int(self.tableWidget.item(row, 1).text())
        print(f"Total X: {total_x}, Total Y: {total_y}")

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
        self.imageLabel.setPixmap(pixmap.scaled(437, 293, Qt.KeepAspectRatio))

def main():
    app = QApplication(sys.argv)
    window = MyWindow("vowel_chart.png")
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
