# -*- coding: utf-8 -*-
import pandas as pd

from .manager import PresamplesParameterManager


def read_prepared_file_with_header(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


ppm = PresamplesParameterManager()
