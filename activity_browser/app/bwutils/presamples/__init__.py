# -*- coding: utf-8 -*-
import csv

import pandas as pd
import presamples

from .manager import PresamplesParameterManager


def read_prepared_file_with_header(path: str) -> pd.DataFrame:
    with open(path, "r") as infile:
        reader = csv.reader(infile)
        header = next(reader)
        df = pd.DataFrame(reader, columns=header)
        print(df)
        return df


ppm = PresamplesParameterManager()
