from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

pg.mkQApp()


x = [1, 2, 3, 4, 5, 6]
y = [
    ('axis 1','#FFFFFF',[0, 4, 6, 8, 10, 4]),
    ('axis 2','#2E2EFE',[0, 5, 7, 9, 11, 3]),
    ('axis 3','#2EFEF7',[0, 1, 2, 3, 4, 12]),
    ('axis 4','#2EFE2E',[0, 8, 0.3, 0.4, 2, 5]),
    ('axis 5','#FFFF00',[0, 1, 6, 4, 2, 1]),
    ('axis 6','#FE2E64',[0, 0.2, 0.3, 0.4, 0.5, 0.6]),
]

# main view
pw = pg.GraphicsView()
pw.setWindowTitle('pyqtgraph example: multiple y-axis')
pw.show()

# layout
layout = pg.GraphicsLayout()
pw.setCentralWidget(layout)

# utility variables
secondary_viewboxes = []
plot_item = None
main_viewbox = None
previous_viewbox = None
main_layout = None

for i, (name, color, y_data) in enumerate(y):
    pen = pg.mkPen(width=1,  color=color)
    column = len(y) - i

    curve = pg.PlotDataItem(x, y_data, pen=pen, name=name, autoDownsample=True)

    if i == 0: # first, main plot
        plot_item = pg.PlotItem()

        main_y_axis = plot_item.getAxis("left") # get Y axis
        main_y_axis.setTextPen(pen)
        main_y_axis.setLabel(name)
        main_x_axis = plot_item.getAxis("bottom") # get x axis
        main_viewbox = plot_item.vb # get main viewbox
        main_viewbox.setMouseMode(pg.ViewBox.RectMode)

        # trick
        main_layout = plot_item.layout # get reference to QGraphicsGridLayout from plot_item
        main_layout.removeItem(main_y_axis) # remove items created in PlotItem from its layout
        main_layout.removeItem(main_x_axis)
        main_layout.removeItem(main_viewbox)

        main_layout.addItem(main_y_axis, 2, column)  # shift them to the right, making space for secondary axes
        main_layout.addItem(main_viewbox, 2, column + 1)
        main_layout.addItem(main_x_axis,  3, column + 1)

        main_layout.setColumnStretchFactor(column + 1, 100) # fix scaling factor, in original layout col 1 contains
        main_layout.setColumnStretchFactor(1, 0)            # the view_box and it's stretched
        #  /trick
        layout.addItem(plot_item, row=0, col=column + 1)
        viewbox = previous_viewbox = main_viewbox
    else: # Secondary "sub" plots
        axis = pg.AxisItem("left")  # create axis
        axis.setTextPen(pen)
        axis.setLabel(name)
        main_layout.addItem(axis, 2, column)  # trick, add axis it into original plot_item layout
        viewbox = pg.ViewBox()  # create ViewBox
        viewbox.setXLink(previous_viewbox)  # link to previous
        previous_viewbox = viewbox
        axis.linkToView(viewbox)  # link axis with viewbox
        layout.scene().addItem(viewbox)  # add viewbox to layout
        viewbox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)  # autorange once to fit views at start

        secondary_viewboxes.append(viewbox)

    viewbox.addItem(curve)

# slot: update view when resized
def updateViews():
    for vb in secondary_viewboxes:
        vb.setGeometry(main_viewbox.sceneBoundingRect())


main_viewbox.sigResized.connect(updateViews)
updateViews()

if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()