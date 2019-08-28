# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyle, QStyledItemDelegate, QStyleOptionButton


class CheckboxDelegate(QStyledItemDelegate):
    """ Presents the value in the column as a checkbox, either ticked (true)
    or not (false).
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):
        """ Paint the cell with a styled option button, showing a checkbox

        See links below for inspiration:
        https://stackoverflow.com/a/11778012
        https://stackoverflow.com/q/15235273
        """
        value = bool(index.data(Qt.DisplayRole))
        button = QStyleOptionButton()
        button.state = QStyle.State_Enabled
        button.state |= QStyle.State_Off if not value else QStyle.State_On
        button.rect = option.rect
        # button.text = "False" if not value else "True"  # This also adds text
        QApplication.style().drawControl(QStyle.CE_CheckBox, button, painter)
