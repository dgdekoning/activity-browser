# -*- coding: utf-8 -*-
import numpy as np

from .views import ABDataFrameView, view_sync


class LCAResultsTable(ABDataFrameView):
    @view_sync
    def sync(self, df):
        self.dataframe = df


class InventoryTable(ABDataFrameView):
    @view_sync
    def sync(self, df):
        self.dataframe = df
        # sort ignoring case sensitivity
        # self.dataframe = self.dataframe.iloc[self.dataframe["name"].str.lower().argsort()]
        # self.dataframe.reset_index(inplace=True, drop=True)


class ContributionTable(ABDataFrameView):
    def __init__(self, parent):
        super(ContributionTable, self).__init__(parent)
        self.parent = parent

    @view_sync
    def sync(self):
        # df = self.parent.df.replace(np.nan, '', regex=True)
        # df.columns = [wrap_text(k, max_length=20) for k in df.columns]
        # self.dataframe = df
        self.dataframe = self.parent.df.replace(np.nan, '', regex=True)  # replace 'nan' values with emtpy string








