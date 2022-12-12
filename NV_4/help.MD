https://github.com/el-NASA/CanSat-Ground-station


https://github.com/Suyash458/SoftwareOscilloscope

https://github.com/slaclab/pydm



You cannot add ScatterPlotItem directly to a GraphicsLayoutWidget but must use a PlotItem as an intermediary:

def create():
    x = [1, 2, 3, 4]
    y = [1, 2, 3, 4]

    plot_item = ui.w.addPlot()
    scatter_item = pg.ScatterPlotItem()
    scatter_item.setData(x, y)
    plot_item.addItem(scatter_item)

