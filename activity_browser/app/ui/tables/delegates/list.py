# -*- coding: utf-8 -*-
from itertools import zip_longest
from typing import List

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QListView,
                             QStyledItemDelegate, QWidget)


class OrderedListInputDialog(QDialog):
    """ Mostly cobbled together from: https://stackoverflow.com/a/41310284
    and https://stackoverflow.com/q/26936585
    """
    def __init__(self, parent=None, flags=Qt.Window):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle("Select and order items")

        form = QFormLayout(self)
        self.list_view = QListView(self)
        self.list_view.setDragDropMode(QListView.InternalMove)
        form.addRow(self.list_view)
        model = QStandardItemModel(self.list_view)
        self.list_view.setModel(model)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.show()

    @staticmethod
    def add_items_value(items: list, value: bool=False) -> List[tuple]:
        """ Helper method, takes a list of items and adds given bool value,
        returning a list of tuples.
        """
        return [
            (i, b) for i, b in zip_longest(items, [], fillvalue=value)
        ]

    def set_items(self, items: List[tuple]):
        model = self.list_view.model()
        model.clear()
        for i, checked in items:
            item = QStandardItem(i)
            item.setCheckable(True)
            item.setCheckState(checked)
            model.appendRow(item)
        self.list_view.setModel(model)

    def items_selected(self) -> list:
        model = self.list_view.model()
        selected = []
        for item in [model.item(i) for i in range(model.rowCount())]:
            if item.checkState():
                selected.append(item.text())
        return selected


class ListDelegate(QStyledItemDelegate):
    """ For managing and validating entered string values
    https://stackoverflow.com/a/40275439
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QWidget(parent)
        dialog = OrderedListInputDialog(editor, Qt.Window)
        dialog.setModal(True)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        """ Populate the editor with data if editing an existing field.
        """
        dialog = editor.findChild(OrderedListInputDialog)
        value = index.data(Qt.DisplayRole)
        if value:
            value_list = [i.lstrip() for i in value.split(",")]
        else:
            value_list = []

        parent = self.parent()
        if hasattr(parent, "table_name") and parent.table_name == "activity_parameter":
            groups = parent.get_activity_groups(value_list)
            unchecked = dialog.add_items_value(groups)
            checked = dialog.add_items_value(value_list, True)
            dialog.set_items(checked + unchecked)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        """ Take the editor, read the given value and set it in the model
        """
        dialog = editor.findChild(OrderedListInputDialog)
        value = ", ".join(map(lambda i: str(i), dialog.items_selected()))
        model.setData(index, value, Qt.EditRole)
