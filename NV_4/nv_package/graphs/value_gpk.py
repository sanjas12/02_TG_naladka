import pyqtgraph as pg


class value_gpk(pg.PlotItem):
        
    def __init__(self, color, parent=None, name=None, labels=None, title='Value', viewBox=None, axisItems=None, enableMenu=True, font = None,**kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        self.color = color
        self.hideAxis('bottom')
        self.hideAxis('left')
        self.value_text = pg.TextItem("start", anchor=(0.5, 0.5), color=self.color)
        if font != None:
            self.value_text.setFont(font)
        self.addItem(self.value_text)

    def update(self, value):
        self.value_text.setText(str(value))