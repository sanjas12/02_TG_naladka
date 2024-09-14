import pyqtgraph as pg

class MultiplePlotAxesExample:
    def __init__(self):
        # Create application and PlotWidget
        self.app = pg.mkQApp()
        self.pw = pg.PlotWidget()
        self.pw.setWindowTitle("pyqtgraph example: MultiplePlotAxes")
        self.pw.show()

        self.p1 = self.pw.plotItem
        self.p1.setLabels(left="axis 1")

        # Create a new ViewBox, link the right axis to its coordinate system
        self.p2 = pg.ViewBox()
        self.p1.showAxis("right")
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis("right").linkToView(self.p2)
        self.p2.setXLink(self.p1)
        self.p1.getAxis("right").setLabel("axis2", color="#0000ff")

        # Create third ViewBox, and a new axis
        self.p3 = pg.ViewBox()
        self.ax3 = pg.AxisItem("right")
        self.p1.layout.addItem(self.ax3, 2, 3)
        self.p1.scene().addItem(self.p3)
        self.ax3.linkToView(self.p3)
        self.p3.setXLink(self.p1)
        self.ax3.setZValue(-10000)
        self.ax3.setLabel("axis 3", color="#ff0000")

        # Handle view resizing
        self.updateViews()
        self.p1.vb.sigResized.connect(self.updateViews)

        # Plot data
        self.p1.plot([1, 2, 4, 8, 16, 32])
        self.p2.addItem(pg.PlotCurveItem([10, 20, 40, 80, 40, 20], pen="b"))
        self.p3.addItem(pg.PlotCurveItem([3200, 1600, 800, 400, 200, 100], pen="r"))

    def updateViews(self):
        # Update auxiliary views to match when resized
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        self.p3.setGeometry(self.p1.vb.sceneBoundingRect())

        # Update linked axes
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)
        self.p3.linkedViewChanged(self.p1.vb, self.p3.XAxis)

    def run(self):
        # Start the application loop
        pg.exec()


def main():
    example = MultiplePlotAxesExample()
    example.run()



# To run the example
if __name__ == "__main__":
    main()
