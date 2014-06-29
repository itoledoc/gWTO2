# -*- coding: utf-8 -*-

"""
Module implementing ArrayCheck.
"""

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature

from Ui_arrayCheck import Ui_ArrayCheck

class ArrayCheck(QMainWindow, Ui_ArrayCheck):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
    
    @pyqtSignature("")
    def on_cancel_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_ok_button_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("QPoint")
    def on_graphicsView_customContextMenuRequested(self, pos):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
