# tg-naladka\src\ui\test_pyqtgrayh_refactored.py
from PyQt5 import QtWidgets
import pyqtgraph as pg


class MultiAxisGraphWidget(QtWidgets.QGroupBox):
    """
    Виджет с многоосевым графиком.
    Основной график имеет собственную ось Y,
    остальные графики отображаются с дополнительными осями, синхронизированными по X.
    """
    def __init__(self, parent=None):
        super().__init__("Multi-axis Graph", parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self._create_graph()

    def _create_graph(self):
        """Создает график с основной и дополнительными осями."""
        x = [1, 2, 3, 4, 5, 6]
        y_data_list = [
            ('Axis 1', '#FFFFFF', [0, 4, 6, 8, 10, 4]),
            ('Axis 2', '#2E2EFE', [0, 5, 7, 9, 11, 3]),
            # ('Axis 3', '#2EFEF7', [0, 1, 2, 3, 4, 12]),
            # ('Axis 4', '#2EFE2E', [0, 8, 0.3, 0.4, 2, 5]),
            # ('Axis 5', '#FFFF00', [0, 1, 6, 4, 2, 1]),
            # ('Axis 6', '#FE2E64', [0, 0.2, 0.3, 0.4, 0.5, 0.6]),
        ]

        self.plot_widget = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.plot_widget)

        # Переменные для основной и вторичных осей
        self.secondary_viewboxes = []
        self.main_viewbox = None
        previous_viewbox = None
        self.main_layout = None

        for i, (name, color, y_data) in enumerate(y_data_list):
            curve = self._create_curve(x, y_data, color, name)
            if i == 0:
                self.main_viewbox, self.main_layout = self._create_main_plot(curve, name, color)
                previous_viewbox = self.main_viewbox
            else:
                vb = self._create_secondary_axis(curve, name, color, previous_viewbox, column=len(y_data_list) - i)
                previous_viewbox = vb

        # Обновляем размеры вторичных графиков при изменении размера основного
        self._update_secondary_views()

    def _create_curve(self, x, y, color, name):
        """Создает график (PlotDataItem) для данных."""
        pen = pg.mkPen(width=1, color=color)
        curve = pg.PlotDataItem(x, y, pen=pen, name=name, autoDownsample=True)
        return curve

    def _create_main_plot(self, curve, name, color):
        """Создает основной график с собственной осью Y."""
        plot_item = pg.PlotItem()
        main_y_axis = plot_item.getAxis("left")
        main_y_axis.setTextPen(pg.mkPen(color=color))
        main_y_axis.setLabel(name)

        main_x_axis = plot_item.getAxis("bottom")
        viewbox = plot_item.vb
        viewbox.setMouseMode(pg.ViewBox.RectMode)
        layout = plot_item.layout

        # Убираем стандартные элементы и размещаем в своей сетке
        layout.removeItem(main_y_axis)
        layout.removeItem(main_x_axis)
        layout.removeItem(viewbox)
        column = 1  # фиксируем колонку для основного графика
        layout.addItem(main_y_axis, 2, column)
        layout.addItem(viewbox, 2, column + 1)
        layout.addItem(main_x_axis, 3, column + 1)
        layout.setColumnStretchFactor(column + 1, 100)
        layout.setColumnStretchFactor(1, 0)

        self.plot_widget.addItem(plot_item, row=0, col=column + 1)
        viewbox.addItem(curve)
        return viewbox, layout

    def _create_secondary_axis(self, curve, name, color, x_link_viewbox, column):
        """Создает вторичную ось Y, синхронизированную с основным графиком по X."""
        axis = pg.AxisItem("left")
        axis.setTextPen(pg.mkPen(color=color))
        axis.setLabel(name)

        viewbox = pg.ViewBox()
        viewbox.setXLink(x_link_viewbox)
        axis.linkToView(viewbox)
        self.plot_widget.scene().addItem(viewbox)
        viewbox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
        viewbox.addItem(curve)
        self.secondary_viewboxes.append(viewbox)

        # Размещаем ось в основной сетке
        self.main_layout.addItem(axis, 2, column)
        return viewbox

    def _update_secondary_views(self):
        """Синхронизирует размеры всех вторичных графиков с основным."""
        def update():
            for vb in self.secondary_viewboxes:
                vb.setGeometry(self.main_viewbox.sceneBoundingRect())
        self.main_viewbox.sigResized.connect(update)
        update()


class MainWindow(QtWidgets.QMainWindow):
    """Главное окно приложения с многоосевым графиком."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtGraph Multi-axis Example")
        self.resize(900, 600)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        graph_groupbox = MultiAxisGraphWidget()
        layout.addWidget(graph_groupbox)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
