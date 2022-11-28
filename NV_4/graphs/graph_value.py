import pyqtgraph as pg


class graph_value(pg.PlotItem):
        
    def __init__(self, color, parent=None, name=None, labels=None, title='Value', viewBox=None, axisItems=None, enableMenu=True, font = None,**kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        

        self.color = color
        self.hideAxis('bottom')
        self.hideAxis('left')
        self.time_text = pg.TextItem("test", anchor=(0.5, 0.5), color=self.color)
        if font != None:
            self.time_text.setFont(font)
        self.addItem(self.time_text)


    def update(self, value):
        # print(self.color, value)
        self.time_text.setText(str(value))