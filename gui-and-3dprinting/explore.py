import sys
from PyQt5 import QtWidgets, uic,QtCore
from itertools import product
from tuben_gui import Tuben  #use get_formants()
import csv


class Explore(QtWidgets.QMainWindow):
    def __init__(self):
        super(Explore, self).__init__()
        uic.loadUi('explore.ui', self)  # 加载 .ui 文件

        # 访问 UI 元素
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, 'tableWidget')

        # 绑定按钮点击事件到自定义槽函数
        #self.pushButton.clicked.connect(self.add_table_row)
        self.pushButton.clicked.connect(self.explore)

        self.show()


    def build_table(self, L, A):
        # 清空表格中的所有行
        self.tableWidget.setRowCount(0)

        # 假设表格有至少 5 列
        for i in range(len(L)):
            # 在表格末尾添加一行
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)

            # 将 L[i] 插入到第 1 列 (索引 0)
            #self.tableWidget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(L[i])))
            item_L = QtWidgets.QTableWidgetItem(str(L[i]))
            item_L.setFlags(item_L.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(rowPosition, 0, item_L)
            # 填充其他列（例如，第 2 到第 4 列）为默认值 "0"
            for col in range(1, 4):
                self.tableWidget.setItem(rowPosition, col, QtWidgets.QTableWidgetItem("0"))

            # 将 A[i] 插入到第 5 列 (索引 4)
            item_A = QtWidgets.QTableWidgetItem(str(A[i]))
            item_A.setFlags(item_A.flags() & ~QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(rowPosition, 4, item_A)

            # 填充剩余的列（例如，第 6 到第 9 列）为默认值 "0"
            for col in range(5, self.tableWidget.columnCount()):
                self.tableWidget.setItem(rowPosition, col, QtWidgets.QTableWidgetItem("0"))

    def get_ranges(self):
        #read the window table and return every parameter as (lower upper,step)
        #lengths come first, areas come second
        ranges = []
        #current = []
        row_count = self.tableWidget.rowCount()

        # 先读取每一行的第 2、3、4 列的值
        for row in range(row_count):
            current_L = float(self.tableWidget.item(row, 0).text())
            lower_bound = float(self.tableWidget.item(row, 1).text())
            upper_bound = float(self.tableWidget.item(row, 2).text())
            step = float(self.tableWidget.item(row, 3).text())
            range_tuple = (current_L, lower_bound, upper_bound, step)
            ranges.append(range_tuple)
            #current.append(current_L)

        # 再读取每一行的第 6、7、8 列的值
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
        filename = 'testexplore.csv'
        # 打开一个 CSV 文件以写入模式
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)

            # 遍历所有组合
            for comb in combinations:
                # 获取 formants
                L=comb[:size]
                A=comb[size:]
                fmts, _ = tub.get_formants(L,A)

                # 将组合及其对应的 formants 写入 CSV 文件
                #row = [(L[i],A[i]) for i in range(size)] + [int(fmts[0]), int(fmts[1])]
                row = [item for pair in zip(L, A) for item in pair] + [int(fmts[0]), int(fmts[1])]

                writer.writerow(row)

        print(f"Data written to {filename}")


    def frange(current, start, stop, step):
        if step == 0 or stop > start:
            yield current
            return
        while start <= stop:
            yield round(start, 10)  # 使用 round() 防止浮点数精度问题
            start += step

    # 示例调用


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = Explore()
    L = [2, 6, 6, 2]
    A = [1, 1, 1, 1]
    window.build_table(L, A)
    app.exec_()
