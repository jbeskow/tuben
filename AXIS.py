import sys
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsLineItem, QGraphicsSimpleTextItem


class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()

        # 创建场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # 添加坐标轴和标签
        self.add_axis()

        self.add_draggable_rectangle()

    def add_axis(self):
        # 添加水平坐标轴
        self.scene.addLine(0, 200, 400, 200)  #
        # 添加垂直坐标轴
        self.scene.addLine(0, 0, 0, 200)

        # 添加水平坐标轴刻度
        for x in range(0, 201, 50):
            tick = QGraphicsLineItem(x, 195, x, 205)
            self.scene.addItem(tick)

            # 显示刻度数值
            text = QGraphicsSimpleTextItem(str(x))
            text.setPos(x - 5, 210)
            self.scene.addItem(text)

        # 添加垂直坐标轴刻度
        for y in range(0, 201, 50):
            tick = QGraphicsLineItem(-5, 200 - y, 5, 200 - y)
            self.scene.addItem(tick)

            # 显示刻度数值
            text = QGraphicsSimpleTextItem(str(y))
            text.setPos(-20, 200 - y - 5)
            self.scene.addItem(text)

        self.add_label(220, 200, "X")
        self.add_label(-20, -25, "Y")

    def add_label(self, x, y, text):
        label = QGraphicsTextItem(text)
        label.setPos(x, y)
        self.scene.addItem(label)

    def add_draggable_rectangle(self):
        # 创建长方形
        self.rect = QGraphicsRectItem(0, 150, 50, 50)
        self.rect.setBrush(Qt.blue)
        self.scene.addItem(self.rect)

        # 设置长方形可拖拽
        self.rect.setFlag(QGraphicsRectItem.ItemIsMovable, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = GraphicsView()
    view.show()
    sys.exit(app.exec_())
