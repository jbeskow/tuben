import sys
from PyQt5.QtWidgets import QApplication, QMainWindow


# Create a subclass of QMainWindow to setup the GUI
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Hello PyQt'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()


# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppWindow()
    sys.exit(app.exec_())
