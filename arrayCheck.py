# -*- coding: utf-8 -*-

"""
Module implementing ArrayCheck.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy.stats import norm,rayleigh
from Ui_arrayCheck import Ui_ArrayCheck

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class ArrayCheck(QMainWindow, Ui_ArrayCheck):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None, ruv=None, num_ant=None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        l = QVBoxLayout(self.graphic_widget)
        self.plot = MyStaticMplCanvas(self.graphic_widget, ruv=ruv)
        l.addWidget(self.plot)
        self.array_ar = 61800 / (100. * self.plot.interval[1])
        self.arrayar_line.setText(_translate("ArrayCheck", "%.2f" % self.array_ar, None))
        self.antennas_line_line.setText(_translate("ArrayCheck", "%d" % num_ant, None))
    
    @pyqtSignature("")
    def on_cancel_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.hide()
    
    @pyqtSignature("")
    def on_ok_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print self.plot.interval[1]
        self.hide()
        return self.plot.interval[1]

    @pyqtSignature("QPoint")
    def on_graphicsView_customContextMenuRequested(self, pos):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100, ruv=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called

        self.compute_initial_figure(ruv)

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self, ruv):
        pass

class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self, ruv):
        x = np.linspace(0, ruv.max() + 100., 1000)
        param = rayleigh.fit(ruv)
        pdf_fitted = rayleigh.pdf(x, loc=param[0], scale=param[1])
        self.axes.hist(ruv, bins=30, normed=True)
        self.axes.plot(x, pdf_fitted, 'r-')
        ylims = self.axes.get_ylim()
        self.interval = rayleigh.interval(0.995, loc=param[0], scale=param[1])
        self.axes.vlines(self.interval[1], 0, ylims[1], linestyles='dashed')
        self.axes.set_ylim(ylims)