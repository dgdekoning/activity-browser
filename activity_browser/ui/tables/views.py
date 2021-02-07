# -*- coding: utf-8 -*-
import os
from functools import wraps
from typing import Optional

from bw2data.filesystem import safe_filename
from PySide2.QtCore import QSize, QSortFilterProxyModel, Qt, Slot
from PySide2.QtWidgets import QFileDialog, QTableView, QTreeView

from ...settings import ab_settings
from .delegates import ViewOnlyDelegate
from .models import PandasModel


class ABDataFrameView(QTableView):
    """ Base class for showing pandas dataframe objects as tables.
    """
    ALL_FILTER = "All Files (*.*)"
    CSV_FILTER = "CSV (*.csv);; All Files (*.*)"
    TSV_FILTER = "TSV (*.tsv);; All Files (*.*)"
    EXCEL_FILTER = "Excel (*.xlsx);; All Files (*.*)"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self.setWordWrap(True)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(22)  # row height
        self.verticalHeader().setVisible(True)
        # Use a custom ViewOnly delegate by default.
        # Can be overridden table-wide or per column in child classes.
        self.setItemDelegate(ViewOnlyDelegate(self))

        self.table_name = 'LCA results'
        self.dataframe = None
        # Initialize attributes which are set during the `sync` step.
        # Creating (and typing) them here allows PyCharm to see them as
        # valid attributes.
        self.model: Optional[PandasModel] = None
        self.proxy_model: Optional[QSortFilterProxyModel] = None

    def get_max_height(self) -> int:
        return (self.verticalHeader().count())*self.verticalHeader().defaultSectionSize() + \
                 self.horizontalHeader().height() + self.horizontalScrollBar().height() + 5

    def sizeHint(self) -> QSize:
        return QSize(self.width(), self.get_max_height())

    def rowCount(self) -> int:
        if getattr(self, "model") is not None:
            return self.model.rowCount()
        return 0

    def custom_view_sizing(self):
        """ Custom table resizing to perform after setting new (proxy) model.
        """
        self.setMaximumHeight(self.get_max_height())

    def to_clipboard(self):
        """ Copy dataframe to clipboard
        """
        self.dataframe.to_clipboard()

    def savefilepath(self, default_file_name: str, file_filter: str=None):
        """ Construct and return default path where data is stored

        Uses the application directory for AB
        """
        safe_name = safe_filename(default_file_name, add_hash=False)
        filepath, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption='Choose location to save lca results',
            dir=os.path.join(ab_settings.data_dir, safe_name),
            filter=file_filter or self.ALL_FILTER,
        )
        return filepath

    def to_csv(self):
        """ Save the dataframe data to a CSV file.
        """
        filepath = self.savefilepath(self.table_name, file_filter=self.CSV_FILTER)
        if filepath:
            if not filepath.endswith('.csv'):
                filepath += '.csv'
            self.dataframe.to_csv(filepath)

    def to_excel(self):
        """ Save the dataframe data to an excel file.
        """
        filepath = self.savefilepath(self.table_name, file_filter=self.EXCEL_FILTER)
        if filepath:
            if not filepath.endswith('.xlsx'):
                filepath += '.xlsx'
            self.dataframe.to_excel(filepath)

    @Slot()
    def keyPressEvent(self, e):
        """ Allow user to copy selected data from the table

        NOTE: by default, the table headers (column names) are also copied.
        """
        if e.modifiers() & Qt.ControlModifier:
            # Should we include headers?
            headers = e.modifiers() & Qt.ShiftModifier
            if e.key() == Qt.Key_C:  # copy
                selection = [self.model.proxy_to_source(p) for p in self.selectedIndexes()]
                rows = [index.row() for index in selection]
                columns = [index.column() for index in selection]
                rows = sorted(set(rows), key=rows.index)
                columns = sorted(set(columns), key=columns.index)
                self.model.to_clipboard(rows, columns, headers)


def tree_model_decorate(sync):
    """ Take and execute the given sync function, then build the view model.
    """
    @wraps(sync)
    def wrapper(self, *args, **kwargs):
        sync(self, *args, **kwargs)
        model = self._select_model()
        self.setModel(model)
        self.custom_view_sizing()
    return wrapper


class ABDictTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUniformRowHeights(True)
        self.data = {}
        self._connect_signals()

    def _connect_signals(self):
        self.expanded.connect(self.custom_view_sizing)
        self.collapsed.connect(self.custom_view_sizing)

    def _select_model(self):
        """ Returns the model to be used in the view.
        """
        raise NotImplementedError

    @Slot()
    def custom_view_sizing(self) -> None:
        """ Resize the first column (usually 'name') whenever an item is
        expanded or collapsed.
        """
        self.resizeColumnToContents(0)
