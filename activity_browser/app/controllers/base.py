# -*- coding: utf-8 -*-
from PySide2.QtCore import QObject


class BaseController(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connect_signals()

    def connect_signals(self):
        raise NotImplementedError  # pragma: no cover
