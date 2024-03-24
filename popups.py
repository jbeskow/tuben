import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMainWindow, QWidget, QHBoxLayout
from tuben.qt_test import Ui_TubeN

#接收两个输入
class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input Dialog")
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Enter the tube parameters,\nmax 4 sections:Separate by comma(,)"))
        # Create first input row
        row1Layout = QHBoxLayout()
        row1Layout.addWidget(QLabel("Input 1:"))
        self.input1 = QLineEdit(self)
        row1Layout.addWidget(self.input1)
        mainLayout.addLayout(row1Layout)

        # Create second input row
        row2Layout = QHBoxLayout()
        row2Layout.addWidget(QLabel("Input 2:"))
        self.input2 = QLineEdit(self)
        row2Layout.addWidget(self.input2)
        mainLayout.addLayout(row2Layout)

        okButton = QPushButton("OK", self)
        okButton.clicked.connect(self.accept)
        mainLayout.addWidget(okButton)

        self.setLayout(mainLayout)

    def getInputs(self):
        return self.input1.text(), self.input2.text()


#壳子 测试用
class MainWindow(QMainWindow, Ui_TubeN):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_add.clicked.connect(self.openInputDialog)
        #self.button.clicked.connect(self.openInputDialog)

        #self.setCentralWidget(self.button)

    def openInputDialog(self):
        dialog = InputDialog(self)
        dialog.setWindowTitle("add")


        if dialog.exec_():
            input1, input2 = dialog.getInputs()
            print("Input 1:", input1)
            print("Input 2:", input2)
            # Process the inputs or pass them to another part of the program here

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
