# -*- coding: utf-8 -*-
from typing import Optional

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QDialog, QGridLayout, QStyledItemDelegate,
                             QDialogButtonBox, QPlainTextEdit, QPushButton,
                             QSizePolicy, QTableView, QWidget)

from ...icons import qicons


class FormulaDialog(QDialog):
    def __init__(self, parent=None, flags=Qt.Window):
        super().__init__(parent=parent, flags=flags)
        self.setWindowTitle("Build a formula")

        # 6 broad by 6 deep.
        grid = QGridLayout(self)
        self.text_field = QPlainTextEdit(self)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred, QSizePolicy.ButtonBox)
        )
        self.parameters = QTableView(self)
        model = QStandardItemModel(self)
        self.parameters.setModel(model)
        self.new_parameter = QPushButton(
            qicons.add, "New parameter", self
        )

        grid.addWidget(self.text_field, 0, 0, 5, 3)
        grid.addWidget(buttons, 5, 0, 1, 3)
        grid.addWidget(self.parameters, 0, 3, 5, 3)
        grid.addWidget(self.new_parameter, 5, 3, 1, 3)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.show()

    def insert_parameters(self, items: list) -> None:
        """ Take the given list of parameter names, amounts and types, insert
        them into the model.
        """
        model = self.parameters.model()
        model.clear()
        model.setHorizontalHeaderLabels(["Name", "Amount", "Type"])
        for x, item in enumerate(items):
            for y, value in enumerate(item):
                model_item = QStandardItem(str(value))
                model_item.setEditable(False)
                model.setItem(x, y, model_item)
        self.parameters.resizeColumnsToContents()

    def set_formula(self, value: str) -> None:
        """ Take the formula and set it to the text_field widget.
        """
        self.text_field.setPlainText(value)

    def get_formula(self) -> Optional[str]:
        """ Look into the text_field, validate formula and return it.
        """
        value = self.text_field.toPlainText()
        return value if value != "" else None


class FormulaDelegate(QStyledItemDelegate):
    """ An extensive delegate to allow users to build and validate formulas

    The delegate spawns a dialog containing:
      - An editable textfield for the formula.
      - A listview containing parameter names that can be used in the formula
      - Ok and Cancel buttons, on Ok, validate the formula before saving

    For hardmode: also allow the user to create a new parameter from WITHIN
    the delegate dialog itself. Requiring us to also include refreshing
    for the parameter list.
    """
    ACCEPTED_TABLES = {"project_parameter", "database_parameter",
                       "activity_parameter", "product", "technosphere",
                       "biosphere"}

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QWidget(parent)
        dialog = FormulaDialog(editor, Qt.Window)
        dialog.setModal(True)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        """ Populate the editor with data if editing an existing field.
        """
        dialog = editor.findChild(FormulaDialog)
        data = index.data(Qt.DisplayRole)
        value = "" if data is None else str(data)

        parent = self.parent()
        # Check which table is asking for a list
        if getattr(parent, "table_name", "") in self.ACCEPTED_TABLES:
            items = parent.get_usable_parameters()
            dialog.insert_parameters(items)
            dialog.set_formula(value)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel,
                     index: QModelIndex):
        """ Take the editor, read the given value and set it in the model
        """
        dialog = editor.findChild(FormulaDialog)
        value = dialog.get_formula()
        if model.data(index, Qt.DisplayRole) == value:
            return
        model.setData(index, value, Qt.EditRole)
