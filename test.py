

# import sys
# from PyQt5.QtWidgets import QWidget, QApplication
# from PyQt5.QtGui import QPainter, QPolygon
# from math import sin, cos, radians, degrees
#
#
# def except_hook(cls, exception, traceback):
#     """Функция для отлова возможных исключений, вознкающих при работе с Qt"""
#     sys.__excepthook__(cls, exception, traceback)
#
#
# class Triangle(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setGeometry(300, 300, 300, 300)
#         self.alpha = 0
#         self.xc = self.yc = 0
#         self.s = 0
#         self.find_center()
#
#     def find_center(self):
#         side = 50
#         x, y = 75, 150
#         x2 = x + side * cos(radians(30))
#         x3 = x + side * cos(radians(30))
#         y2 = y + side * sin(radians(30))
#         y3 = y + side * sin(radians(-30))
#         self.xc = (x + x2 + x3) / 3
#         self.yc = (y + y2 + y3) / 3
#         self.s = ((self.xc - x) ** 2 + (self.yc - y) ** 2) ** 0.5
#
#     def paintEvent(self, event) -> None:
#         qp = QPainter()
#         qp.begin(self)
#         self.draw(qp)
#         qp.end()
#
#     def keyPressEvent(self, event) -> None:
#         self.alpha = (self.alpha + 1) % 360
#         self.repaint()
#
#     def draw(self, qp: QPainter):
#         side = 100
#         alpha = self.alpha
#         x, y = 75, 150
#         # alpha = 0
#         x2 = x + side * cos(radians(-30) - radians(alpha))
#         y2 = y + side * sin(radians(-30) - radians(alpha))
#         # x3 = x2 + side * cos(radians(90))
#         # y3 = y2 + side * sin(radians(90))
#         x3 = x + side * cos(radians(30) - radians(alpha))
#         y3 = y + side * sin(radians(30) - radians(alpha))
#         print((x, y), (x2, y2), (x3, y3))
#
#         # x_new = x * cos(alpha) - y * sin(alpha)
#         # y_new = x * cos(alpha) + y * sin(alpha)
#         #
#         # x2_new = x2 * cos(alpha) - y2 * sin(alpha)
#         # y2_new = x2 * cos(alpha) + y2 * sin(alpha)
#         #
#         # x3_new = x3 * cos(alpha) - y3 * sin(radians(90) - alpha)
#         # y3_new = x3 * cos(alpha) + y3 * sin(radians(90) - alpha)
#
#
#         # points = [(x_new, y_new), (x2_new, y2_new), (x3_new, y3_new)]
#         # print(*points)
#         points = [(x, y), (x2, y2), (x3, y3)]
#         # points = self.rotate_figure(points, alpha)
#         qp.drawPolygon(QPolygon([j for i in points for j in i]))
#
#     def rotate_figure(self, points, alpha):
#         """Функция для поворота фигуры на определенный угол"""
#         new_points = []
#         xc, yc = self.xc, self.yc
#         xc, yc = 75, 150
#         for i in points:
#             x, y = i
#             x -= xc
#             y -= yc
#             x_new = x * cos(alpha) - y * sin(alpha)
#             y_new = x * cos(alpha) + y * sin(alpha)
#             # new_points.append((temp_x + r * cos(alpha), temp_y + r * sin(alpha)))
#             new_points.append(
#                 (x_new + xc, y_new + yc)
#             )
#             # new_points.append(
#             #     (temp_x * cos(alpha) - temp_y * sin(alpha),
#             #      temp_x * cos(alpha) + temp_y * sin(alpha))
#             # )
#         return new_points
#
#
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Triangle()
#     ex.show()
#     sys.excepthook = except_hook
#     sys.exit(app.exec())
#
#
# # from csv import DictWriter, writer
# # from itertools import product
# # data_list = {
# #     ('A', 'B'): (10, 0),
# #     ('B', 'C'): (15, 1),
# #     ('C', 'D'): (1, 1),
# #     ('D', 'E'): (5, 0),
# #     ('E', 'F'): (9, 1),
# #     ('F', 'D'): (24, 0)
# # }
# #
# # data_matrix = [
# #     ['', 'A', 'B', 'C', 'D', 'E', 'F'],
# #     ['A', '', '10.0', '', '', '', ''],
# #     ['B', '10.0', '', '15.0', '', '', ''],
# #     ['C', '', '', '', '1.0', '', ''],
# #     ['D', '', '', '', '', '5.0', '24.0'],
# #     ['E', '', '', '', '5.0', '', '9.0'],
# #     ['F', '', '', '', '24.0', '', '']
# # ]
# #
# # # with open('test_list.csv', 'w', newline='') as f:
# # #     writer = DictWriter(f, delimiter=',',
# # #                         fieldnames=['start', 'end', 'weight', 'is_directed'])
# # #     writer.writeheader()
# # #     for i in data_list:
# # #         arg = dict()
# # #         arg['start'] = i[0]
# # #         arg['end'] = i[1]
# # #         arg['weight'] = data_list[i][0]
# # #         arg['is_directed'] = data_list[i][1]
# # #         writer.writerow(arg)
# #
# # # with open('test_matrix.csv', 'w', newline='') as f:
# # #     wr = writer(f, delimiter=';')
# # #     wr.writerows(data_matrix)
# #
# # print(set(product(range(10), repeat=2)))