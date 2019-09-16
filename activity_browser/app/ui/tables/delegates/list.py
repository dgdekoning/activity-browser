# -*- coding: utf-8 -*-
from itertools import zip_longest
from typing import List

from PyQt5 import QtCore, QtGui, QtWidgets


class OrderedListInputDialog(QtWidgets.QDialog):
    """ Mostly cobbled together from: https://stackoverflow.com/a/41310284
    and https://stackoverflow.com/q/26936585
    """
    def __init__(self, parent=None, flags=QtCore.Qt.Window):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle("Select and order items")

        form = QtWidgets.QFormLayout(self)
        self.list_view = QtWidgets.QListView(self)
        self.list_view.setDragDropMode(QtWidgets.QListView.InternalMove)
        form.addRow(self.list_view)
        model = QtGui.QStandardItemModel(self.list_view)
        self.list_view.setModel(model)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
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
            item = QtGui.QStandardItem(i)
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


class ListDelegate(QtWidgets.QStyledItemDelegate):
    """ For managing and validating entered string values
    https://stackoverflow.com/a/40275439
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QWidget(parent)
        dialog = OrderedListInputDialog(editor, QtCore.Qt.Window)

        # Check which table is asking for a list
        if hasattr(parent, "table_name") and parent.table_name == "activity_parameter":
            items = parent.get_activity_groups()
            unchecked_items = dialog.add_items_value(items)
            dialog.set_items(unchecked_items)

        return editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex):
        """ Populate the editor with data if editing an existing field.
        """
        dialog = editor.findChild(OrderedListInputDialog)
        value = index.data(QtCore.Qt.DisplayRole)
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

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex):
        """ Take the editor, read the given value and set it in the model
        """
        dialog = editor.findChild(OrderedListInputDialog)
        value = ", ".join(map(lambda i: str(i), dialog.items_selected()))
        model.setData(index, value, QtCore.Qt.EditRole)