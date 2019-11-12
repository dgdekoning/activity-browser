# -*- coding: utf-8 -*-
import pandas as pd

from .manager import PresamplesParameterManager, process_brightway_parameters


def load_scenarios_from_file(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def save_scenarios_to_file(data: pd.DataFrame, path: str) -> None:
    data.to_csv(path_or_buf=path)