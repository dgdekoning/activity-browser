# -*- coding: utf-8 -*-
from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot

from .delegates import *
from .models import (
    BaseExchangeModel, ProductExchangeModel, TechnosphereExchangeModel,
    BiosphereExchangeModel, DownstreamExchangeModel,
)
from .views import ABDataFrameView
from ..icons import qicons
from ...signals import signals


class BaseExchangeTable(ABDataFrameView):
    MODEL = BaseExchangeModel
    # Signal used to correctly control `DetailsGroupBox`
    updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setSizePolicy(QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Maximum)
        )

        self.delete_exchange_action = QtWidgets.QAction(
            qicons.delete, "Delete exchange(s)", None
        )
        self.remove_formula_action = QtWidgets.QAction(
            qicons.delete, "Clear formula(s)", None
        )
        self.modify_uncertainty_action = QtWidgets.QAction(
            qicons.edit, "Modify uncertainty", None
        )
        self.remove_uncertainty_action = QtWidgets.QAction(
            qicons.delete, "Remove uncertainty/-ies", None
        )

        self.key = getattr(parent, "key", None)
        self.model = self.MODEL(self.key, self)
        self.downstream = False
        self._connect_signals()

    def _connect_signals(self):
        self.delete_exchange_action.triggered.connect(self.delete_exchanges)
        self.remove_formula_action.triggered.connect(self.remove_formula)
        self.modify_uncertainty_action.triggered.connect(self.modify_uncertainty)
        self.remove_uncertainty_action.triggered.connect(self.remove_uncertainty)

    def custom_view_sizing(self) -> None:
        """ Ensure the `exchange` column is hidden whenever the table is shown.
        """
        super().custom_view_sizing()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setColumnHidden(self.model.exchange_column, True)

    def sync(self, exchanges=None):
        """ Build the table using either new or stored exchanges iterable.
        """
        self.model.sync(exchanges)
        self.custom_view_sizing()

    def open_activities(self) -> None:
        """ Take the selected indexes and attempt to open activity tabs.
        """
        for proxy in self.selectedIndexes():
            act = self.model.get_key(proxy)
            signals.open_activity_tab.emit(act)
            signals.add_activity_to_history.emit(act)

    @Slot(name="deleteExchanges")
    def delete_exchanges(self) -> None:
        """ Remove all of the selected exchanges from the activity.
        """
        self.model.delete_exchanges(self.selectedIndexes())

    @Slot(name="removeFormulas")
    def remove_formula(self) -> None:
        """ Remove the formulas for all of the selected exchanges.

        This will also check if the exchange has `original_amount` and
        attempt to overwrite the `amount` with that value after removing the
        `formula` field.
        """
        self.model.remove_formula(self.selectedIndexes())

    @Slot(name="modifyExchangeUncertainty")
    def modify_uncertainty(self) -> None:
        """Need to know both keys to select the correct exchange to update"""
        self.model.modify_uncertainty(self.currentIndex())

    @Slot(name="unsetExchangeUncertainty")
    def remove_uncertainty(self) -> None:
        self.model.remove_uncertainty(self.selectedIndexes())

    def contextMenuEvent(self, a0) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction(self.delete_exchange_action)
        menu.addAction(self.remove_formula_action)
        menu.exec_(a0.globalPos())

    def dragMoveEvent(self, event) -> None:
        """ For some reason, this method existing is required for allowing
        dropEvent to occur _everywhere_ in the table.
        """
        pass

    def dropEvent(self, event):
        source_table = event.source()
        keys = [source_table.get_key(i) for i in source_table.selectedIndexes()]
        event.accept()
        signals.exchanges_add.emit(keys, self.key)

    def get_usable_parameters(self):
        return self.model.get_usable_parameters()

    def get_interpreter(self):
        return self.model.get_interpreter()


class ProductExchangeTable(BaseExchangeTable):
    MODEL = ProductExchangeModel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(0, FloatDelegate(self))
        self.setItemDelegateForColumn(1, StringDelegate(self))
        self.setItemDelegateForColumn(2, StringDelegate(self))
        self.setItemDelegateForColumn(3, FormulaDelegate(self))
        self.setDragDropMode(QtWidgets.QTableView.DragDrop)
        self.table_name = "product"

    def contextMenuEvent(self, a0) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction(self.remove_formula_action)
        menu.exec_(a0.globalPos())

    def dragEnterEvent(self, event):
        """ Accept exchanges from a technosphere database table, and the
        technosphere exchanges table.
        """
        source = event.source()
        if (getattr(source, "table_name", "") == "technosphere" or
                getattr(source, "technosphere", False) is True):
            event.accept()


class TechnosphereExchangeTable(BaseExchangeTable):
    MODEL = TechnosphereExchangeModel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(0, FloatDelegate(self))
        self.setItemDelegateForColumn(1, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(2, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(3, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(4, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(5, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(6, ViewOnlyUncertaintyDelegate(self))
        self.setItemDelegateForColumn(7, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(8, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(9, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(10, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(11, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(12, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(13, FormulaDelegate(self))
        self.setDragDropMode(QtWidgets.QTableView.DragDrop)
        self.table_name = "technosphere"

    def custom_view_sizing(self) -> None:
        """ Ensure the `exchange` column is hidden whenever the table is shown.
        """
        super().custom_view_sizing()
        self.show_uncertainty()

    def show_uncertainty(self, show: bool = False) -> None:
        """Show or hide the uncertainty columns, 'Uncertainty Type' is always shown.
        """
        cols = self.model.columns
        self.setColumnHidden(cols.index("Uncertainty"), not show)
        self.setColumnHidden(cols.index("pedigree"), not show)
        for c in self.model.UNCERTAINTY:
            self.setColumnHidden(cols.index(c), not show)

    def contextMenuEvent(self, a0) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction(qicons.right, "Open activities", self.open_activities)
        menu.addAction(self.modify_uncertainty_action)
        menu.addSeparator()
        menu.addAction(self.delete_exchange_action)
        menu.addAction(self.remove_formula_action)
        menu.addAction(self.remove_uncertainty_action)
        menu.exec_(a0.globalPos())

    def dragEnterEvent(self, event):
        """ Accept exchanges from a technosphere database table, and the
        downstream exchanges table.
        """
        source = event.source()
        if (getattr(source, "table_name", "") == "downstream" or
                hasattr(source, "technosphere")):
            event.accept()


class BiosphereExchangeTable(BaseExchangeTable):
    MODEL = BiosphereExchangeModel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(0, FloatDelegate(self))
        self.setItemDelegateForColumn(1, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(2, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(3, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(4, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(5, ViewOnlyUncertaintyDelegate(self))
        self.setItemDelegateForColumn(6, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(7, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(8, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(9, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(10, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(11, ViewOnlyFloatDelegate(self))
        self.setItemDelegateForColumn(12, FormulaDelegate(self))
        self.table_name = "biosphere"
        self.setDragDropMode(QtWidgets.QTableView.DropOnly)

    def custom_view_sizing(self) -> None:
        super().custom_view_sizing()
        self.show_uncertainty()

    def show_uncertainty(self, show: bool = False) -> None:
        """Show or hide the uncertainty columns, 'Uncertainty Type' is always shown.
        """
        cols = self.model.columns
        self.setColumnHidden(cols.index("Uncertainty"), not show)
        self.setColumnHidden(cols.index("pedigree"), not show)
        for c in self.model.UNCERTAINTY:
            self.setColumnHidden(cols.index(c), not show)

    def contextMenuEvent(self, a0) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction(self.modify_uncertainty_action)
        menu.addSeparator()
        menu.addAction(self.delete_exchange_action)
        menu.addAction(self.remove_formula_action)
        menu.addAction(self.remove_uncertainty_action)
        menu.exec_(a0.globalPos())

    def dragEnterEvent(self, event):
        """ Only accept exchanges from a technosphere database table
        """
        if hasattr(event.source(), "technosphere"):
            event.accept()


class DownstreamExchangeTable(BaseExchangeTable):
    """ Downstream table class is very similar to technosphere table, just more
    restricted.
    """
    MODEL = DownstreamExchangeModel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(0, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(1, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(2, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(3, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(4, ViewOnlyDelegate(self))
        self.setItemDelegateForColumn(5, ViewOnlyDelegate(self))
        self.setDragDropMode(QtWidgets.QTableView.DragOnly)

        self.downstream = True
        self.table_name = "downstream"

    def contextMenuEvent(self, a0) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction(qicons.right, "Open activities", self.open_activities)
        menu.exec_(a0.globalPos())
