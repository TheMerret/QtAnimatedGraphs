from PyQt5.QtGui import QPixmap
import pyqtgraph as pg
import numpy as np

from .utils.utils_graphs import NullGraphFunction, GraphFunction


class GraphPlotWidget(pg.PlotWidget):

    def __init__(self, parent=None, **kargs):
        pg.setConfigOption('foreground', 'k')  # TODO: сделать неглобальную конфигурацию
        super(GraphPlotWidget, self).__init__(parent=parent, background=None,
                                              **kargs)
        self.disableAutoRange()  # Иначе пытается достичь конца бесконечности

        # Начальное положение (Покрутить значения)
        self.home_range = dict(xRange=(-10, 10), yRange=(-5, 5))
        self.dot_step = 1000  # типо разрешение графика
        self.graph_pen = pg.mkPen(color='r', width=2)

        # self.graphItem = pg.PlotCurveItem(parent=self.plot(), pen=self.graph_pen, antialias=True)
        self.graphItem = pg.PlotCurveItem(pen=self.graph_pen, antialias=True)
        self.plotItem.addItem(self.graphItem)

        # TODO: сделать оси на нулях
        self.showGrid(True, True)
        self.setRange(**self.home_range)
        self.setAspectLocked(True)

        # Заменяем оригинальный слот на нужный нам
        home_icon = QPixmap('resources/icons/plot_controls/home.svg')
        home_icon = home_icon.scaled(self.plotItem.autoBtn.pixmap.size())
        self.plotItem.autoBtn.setPixmap(home_icon)
        self.plotItem.autoBtn.setScale(.95)
        self.plotItem.autoBtn.clicked.disconnect()
        self.plotItem.autoBtn.clicked.connect(self.set_range_to_home)

        self.sigRangeChanged.connect(self.on_range_changed)

        self.nan_graph_fn = NullGraphFunction()
        self._graph_fn = self.nan_graph_fn

    @property
    def graph_fn(self):
        return self._graph_fn

    @graph_fn.setter
    def graph_fn(self, fn):
        self.set_graph_fn(fn)

    def set_graph_fn(self, fn):
        if fn is None or getattr(fn, 'func', None) is None:
            fn = self.nan_graph_fn
        elif not isinstance(fn, GraphFunction):
            raise ValueError('Function must be instance of GraphFunction')
        self._graph_fn = fn
        self.update_graph()

    def on_range_changed(self, _, rng):  # обманка для бесконечного графика
        (xmin, xmax), (_, _) = rng
        x = np.linspace(xmin, xmax, self.dot_step, endpoint=True)
        y = self.graph_fn(x)
        try:
            iter(y)
        except TypeError:
            _ = y
            y = x.copy()
            y.fill(_)
        # TODO: разделить несколько линий (гипербола)
        self.graphItem.setData(x, y, pen=self.graph_pen)

    def update_graph(self):
        self.sigRangeChanged.emit(self, self.viewRange())

    def set_range_to_home(self):
        self.plotItem.setRange(**self.home_range)
