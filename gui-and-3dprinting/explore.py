from PyQt5 import QtWidgets, QtCore
from itertools import product
from tuben_gui import Tuben  # use get_formants()
import csv
from explore_window import Ui_MainWindow


class Explore(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # access UI elements
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'tableWidget')

        #self.pushButton.clicked.connect(self.add_table_row)
        self.pushButton.clicked.connect(self.explore)

        self.show()

    def build_table(self, L, A):
        # empty the table
        self.tableWidget.setRowCount(0)

        for i in range(len(L)):
            # add a row at the end
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)

            # insert L[i] column 1  (idx 0)
            #self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(L[i])))
            item_L = QtWidgets.QTableWidgetItem(str(L[i]))
            item_L.setFlags(item_L.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(rowPosition, 0, item_L)
            # fill in other column
            for col in range(1, 4):
                self.tableWidget.setItem(rowPosition, col, QtWidgets.QTableWidgetItem("0"))

            # A[i] to column 5 列
            item_A = QtWidgets.QTableWidgetItem(str(A[i]))
            item_A.setFlags(item_A.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(rowPosition, 4, item_A)

            # fill in other column
            for col in range(5, self.tableWidget.columnCount()):
                self.tableWidget.setItem(rowPosition, col, QtWidgets.QTableWidgetItem("0"))

    def get_ranges(self):
        #read the window table and return every parameter as (lower upper,step)
        #lengths come first, areas come second
        ranges = []
        #current = []
        row_count = self.tableWidget.rowCount()

        # read in column 2,3,4
        for row in range(row_count):
            current_L = float(self.tableWidget.item(row, 0).text())
            lower_bound = float(self.tableWidget.item(row, 1).text())
            upper_bound = float(self.tableWidget.item(row, 2).text())
            step = float(self.tableWidget.item(row, 3).text())
            range_tuple = (current_L, lower_bound, upper_bound, step)
            ranges.append(range_tuple)
            #current.append(current_L)

        # read in column 6,7,8
        for row in range(row_count):
            current_A = float(self.tableWidget.item(row, 4).text())
            lower_bound = float(self.tableWidget.item(row, 5).text())
            upper_bound = float(self.tableWidget.item(row, 6).text())
            step = float(self.tableWidget.item(row, 7).text())
            range_tuple = (current_A, lower_bound, upper_bound, step)
            ranges.append(range_tuple)
            #current.append(current_A)
        print(ranges)
        return ranges

    def generate_combinations(self, ranges):
        all_ranges = []
        for i, (current, lower, upper, step) in enumerate(ranges):
            print(f"Processing range {i}: lower={lower}, upper={upper}, step={step}")
            possible_values = self.frange(current, lower, upper, step)
            all_ranges.append(possible_values)

        combinations = [list(combination) for combination in product(*all_ranges)]
        if len(combinations)==0:
            print(all_ranges)
        return combinations

    def explore(self):
        ranges = self.get_ranges()
        combinations = self.generate_combinations(ranges)
        size = int(len(combinations[0]) / 2)
        print(size)
        tub = Tuben()

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if filename:
            if not filename.endswith(".csv"):
                filename += ".csv"
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                # 遍历所有组合
                for comb in combinations:
                    # get formants
                    L = comb[:size]
                    A = comb[size:]
                    fmts, _ = tub.get_formants(L, A)
                    if len(fmts) == 4:
                        row = [item for pair in zip(L, A) for item in pair] + [int(fmts[0]), int(fmts[1]), int(fmts[2]),
                                                                               int(fmts[3])]
                    elif len(fmts) == 3:
                        row = [item for pair in zip(L, A) for item in pair] + [int(fmts[0]), int(fmts[1]), int(fmts[2])]
                    elif len(fmts) == 2:
                        row = [item for pair in zip(L, A) for item in pair] + [int(fmts[0]), int(fmts[1])]
                    elif len(fmts) == 1:
                        row = [item for pair in zip(L, A) for item in pair] + [int(fmts[0])]
                    writer.writerow(row)

            print(f"Data written to {filename}")

    def frange(self, current, start, stop, step):
        if step == 0 or stop > start:
            yield current
            return
        while start <= stop:
            yield round(start, 10)
            start += step


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Explore()
    L = [2, 6, 6, 2]
    A = [1, 1, 1, 1]
    window.build_table(L, A)
    app.exec_()
