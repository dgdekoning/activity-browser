# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from .databases_table import ActivitiesTableWidget
from brightway2 import *
from PyQt4 import QtCore, QtGui


class CSListModel(QtCore.QAbstractListModel):
    def rowCount(self, *args):
        return len(calculation_setups)

    def data(self, index, *args):
        row = index.row()
        names = sorted(calculation_setups.keys())
        return names[row]


class CSListWidget(QtGui.QComboBox):
    def __init__(self):
        super(CSListWidget, self).__init__()
        self._model = CSListModel()
        self.setModel(self._model)

    def select(self, name):
        index = sorted(calculation_setups.keys()).index(name)
        self.setCurrentIndex(index)


class CSActivityItem(QtGui.QTableWidgetItem):
    def __init__(self, *args, key=None):
        super(CSActivityItem, self).__init__(*args)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
        self.key = key


class CSAmount(QtGui.QTableWidgetItem):
    def __init__(self, *args, key=None):
        super(CSAmount, self).__init__(*args)
        self.key = key


class CSActivityTableWidget(QtGui.QTableWidget):
    COLUMNS = {
        0: "name",
        1: "amount",
        2: "unit",
    }

    def __init__(self):
        super(CSActivityTableWidget, self).__init__()
        self.setColumnCount(3)
        if not len(calculation_setups):
            self.setVisible(False)
        self.setSortingEnabled(True)
        self.setAcceptDrops(True)
        self.setHorizontalHeaderLabels(["Activity name", "Amount", "Unit"])

    def dragEnterEvent(self, event):
        if isinstance(event.source(), ActivitiesTableWidget):
            event.accept()

    def dropEvent(self, event):
        new_keys = [item.key for item in event.source().selectedItems()]
        for key in new_keys:
            act = get_activity(key)
            if act['type'] != "process":
                continue

            new_row = self.rowCount()
            self.insertRow(new_row)
            self.setItem(new_row, 0, CSActivityItem(act['name'], key=key))
            self.setItem(new_row, 1, CSAmount("1.0", key=key))
            self.setItem(new_row, 2, CSActivityItem(act.get('unit', 'Unknown')))

        event.accept()
