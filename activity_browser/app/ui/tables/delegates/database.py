# -*- coding: utf-8 -*-
from bw2data import databases
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate


class DatabaseDelegate(QStyledItemDelegate):
    """ Nearly the same as the string delegate, but presents as
    a combobox menu containing the databases of the current project.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        """ Populate the editor with data if editing an existing field.
        """
        value = str(index.data(Qt.DisplayRole))
        editor.clear()
        editor.insertItems(0, databases.list)
        editor.setCurrentIndex(databases.list.index(value))

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel,
                     index: QModelIndex):
        """ Take the editor, read the given value and set it in the model.
        """
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)
