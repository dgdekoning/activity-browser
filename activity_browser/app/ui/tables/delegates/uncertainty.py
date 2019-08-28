# -*- coding: utf-8 -*-
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate
from stats_arrays import uncertainty_choices


class UncertaintyDelegate(QStyledItemDelegate):
    """ A combobox containing the sorted list of possible uncertainties
    `setModelData` stores the integer id of the selected uncertainty
    distribution.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.choices = {
            u.description: u.id for u in uncertainty_choices.choices
        }

    def createEditor(self, parent, option, index):
        """ Create a list of descriptions of the uncertainties we have.
        Note that the `choices` attribute of uncertainty_choices is already
        sorted by id.
        """
        editor = QComboBox(parent)
        items = sorted(self.choices, key=self.choices.get)
        editor.insertItems(0, items)
        return editor

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        """ Lookup the description text set in the model using the reverse
        dictionary for the uncertainty choices.

        Note that the model presents the integer value as a string (the
        description of the uncertainty distribution), so we cannot simply
        take the value and set the index in that way.
        """
        value = index.data(Qt.DisplayRole)
        editor.setCurrentIndex(self.choices.get(value, 0))

    def setModelData(self, editor: QComboBox, model: QAbstractItemModel,
                     index: QModelIndex):
        """ Read the current index of the combobox and return that to the model.
        """
        value = editor.currentIndex()
        model.setData(index, value, Qt.EditRole)
