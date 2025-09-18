# tg-naladka\src\ui\test_pyqtgrayh_mainwindow.py
from PyQt5 import QtWidgets
import pyqtgraph as pg


class MultiAxisGraphWidget(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Multi-axis Graph", parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self._create_graph()

    def _create_graph(self):
        x = [1, 2, 3, 4, 5, 6]
        y = [
            ('axis 1', '#FFFFFF', [0, 4, 6, 8, 10, 4]),
            ('axis 2', '#2E2EFE', [0, 5, 7, 9, 11, 3]),
            ('axis 3', '#2EFEF7', [0, 1, 2, 3, 4, 12]),
            ('axis 4', '#2EFE2E', [0, 8, 0.3, 0.4, 2, 5]),
            ('axis 5', '#FFFF00', [0, 1, 6, 4, 2, 1]),
            ('axis 6', '#FE2E64', [0, 0.2, 0.3, 0.4, 0.5, 0.6]),
        ]

        self.plot_widget = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.plot_widget)

        secondary_viewboxes = []
        main_viewbox = None
        previous_viewbox = None
        plot_item = None
        main_layout = None

        for i, (name, color, y_data) in enumerate(y):
            pen = pg.mkPen(width=1, color=color)
            column = len(y) - i
            curve = pg.PlotDataItem(x, y_data, pen=pen, name=name, autoDownsample=True)

            if i == 0:  # main plot
                plot_item = pg.PlotItem()
                main_y_axis = plot_item.getAxis("left")
                main_y_axis.setTextPen(pen)
                main_y_axis.setLabel(name)
                main_x_axis = plot_item.getAxis("bottom")
                main_viewbox = plot_item.vb
                main_viewbox.setMouseMode(pg.ViewBox.RectMode)

                main_layout = plot_item.layout
                main_layout.removeItem(main_y_axis)
                main_layout.removeItem(main_x_axis)
                main_layout.removeItem(main_viewbox)
                main_layout.addItem(main_y_axis, 2, column)
                main_layout.addItem(main_viewbox, 2, column + 1)
                main_layout.addItem(main_x_axis, 3, column + 1)
                main_layout.setColumnStretchFactor(column + 1, 100)
                main_layout.setColumnStretchFactor(1, 0)

                self.plot_widget.addItem(plot_item, row=0, col=column + 1)
                viewbox = previous_viewbox = main_viewbox
            else:  # secondary axes
                axis = pg.AxisItem("left")
                axis.setTextPen(pen)
                axis.setLabel(name)
                main_layout.addItem(axis, 2, column)

                viewbox = pg.ViewBox()
                viewbox.setXLink(previous_viewbox)
                previous_viewbox = viewbox
                axis.linkToView(viewbox)
                self.plot_widget.scene().addItem(viewbox)
                viewbox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
                secondary_viewboxes.append(viewbox)

            viewbox.addItem(curve)

        def updateViews():
            for vb in secondary_viewboxes:
                vb.setGeometry(main_viewbox.sceneBoundingRect())

        main_viewbox.sigResized.connect(updateViews)
        updateViews()


class MainWindow(QtWidgets.QMainWindow):
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
