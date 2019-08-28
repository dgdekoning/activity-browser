# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractItemModel, QLocale, QModelIndex, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QLineEdit, QStyledItemDelegate


class FloatDelegate(QStyledItemDelegate):
    """ For managing and validating entered float values.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        locale = QLocale(QLocale.English)
        locale.setNumberOptions(QLocale.RejectGroupSeparator)
        validator = QDoubleValidator()
        validator.setLocale(locale)
        editor.setValidator(validator)
        return editor

    def setEditorData(self, editor: QLineEdit, index: QModelIndex):
        """ Populate the editor with data if editing an existing field.
        """
        data = index.data(Qt.DisplayRole)
        value = float(data) if data else 0
        editor.setText(str(value))

    def setModelData(self, editor: QLineEdit, model: QAbstractItemModel,
                     index: QModelIndex):
        """ Take the editor, read the given value and set it in the model
        """
        try:
            value = float(editor.text())
            model.setData(index, value, Qt.EditRole)
        except ValueError:
            pass
