import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsLineItem, QGraphicsSimpleTextItem
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPolygonF
from PyQt5.QtCore import Qt, QPointF


class Axis(QGraphicsView):
    def __init__(self):
        super().__init__()

        # 创建场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # 添加坐标轴和标签
        self.add_axis()
        # self.add_draggable_rectangle()

    def add_axis(self):
        # 添加水平坐标轴
        self.scene.addLine(0, 200, 400, 200)
        # 添加垂直坐标轴
        self.scene.addLine(0, -200, 0, 200)

        # 添加水平坐标轴箭头
        arrow = QPolygonF([QPointF(405, 200), QPointF(400, 205), QPointF(400, 195)])
        self.scene.addPolygon(arrow)

        # 添加垂直坐标轴箭头
        arrow = QPolygonF([QPointF(0, -205), QPointF(5, -200), QPointF(-5, -200)])
        self.scene.addPolygon(arrow)

        # 添加水平坐标轴刻度
        for x in range(50, 401, 50):
            tick = QGraphicsLineItem(x, 195, x, 200)
            self.scene.addItem(tick)

            # 显示刻度数值
            text = QGraphicsSimpleTextItem(str(x))
            text.setPos(x-10, 210)
            self.scene.addItem(text)

        # 添加垂直坐标轴刻度
        for y in range(50, 401, 50):
            tick = QGraphicsLineItem(0, 200 - y, 5, 200 - y)
            self.scene.addItem(tick)

            # 显示刻度数值
            text = QGraphicsSimpleTextItem(str(y))
            text.setPos(-30, 190 - y)
            self.scene.addItem(text)

        self.add_label(-20, 210, "0")
        self.add_label(430, 200, "X")
        self.add_label(-5, -240, "Y")

    def add_label(self, x, y, text):
        label = QGraphicsTextItem(text)
        label.setPos(x, y)
        self.scene.addItem(label)

    def add_draggable_rectangle(self):
        # 创建长方形
        self.rect = QGraphicsRectItem(0, 150, 50, 50)
        self.rect.setBrush(Qt.blue)
        self.scene.addItem(self.rect)
        # # 设置长方形可拖拽
        # self.rect.setFlag(QGraphicsRectItem.ItemIsMovable, True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = GraphicsView()
    view.show()
    sys.exit(app.exec_())
