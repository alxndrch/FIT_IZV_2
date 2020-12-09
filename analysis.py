#!/usr/bin/env python3.8
# coding=utf-8

from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os


# Ukol 1: nacteni dat
def get_dataframe(filename: str = "accidents.pkl.gz",
                  verbose: bool = False) -> pd.DataFrame:

    if not os.path.exists(filename):
        return None  # pokud zadany soubor neexistuje

    # nactany dataframe z pickle
    df = pd.read_pickle(filename, compression="gzip")

    MB = 1_048_576  # 1024**2, pro prevod na MB

    # sloupce, ktere budou mit typ category
    category_col = ["p36", "p6", "p7", "p8", "p9", "p10", "p11", "p15", "p16",
                    "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24",
                    "p27", "p28", "p39", "p44", "p45a", "p48a", "p49", "p50a",
                    "p50b", "p51", "p55a", "p57", "p58", "q", "t", "p5a"]

    if verbose:
        print(f"orig_size={df.memory_usage(deep=True).sum() / MB:.1f} MB")

    for c in category_col:  # zmena typu na category pro sloupce z category_col
        df[c] = df[c].astype("category")

    df["p2a"] = df["p2a"].astype("datetime64")  # zmena series na typ pro datum
    df = df.rename(columns={"p2a": "date"})  # zmena nazvu sloupce

    if verbose:
        print(f"new_size={df.memory_usage(deep=True).sum() / MB:.1f} MB")

    return df


# Ukol 2: následky nehod v jednotlivých regionech
def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    pass


# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    pass


# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", True)
    # plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    # plot_damage(df, "02_priciny.png", True)
    # plot_surface(df, "03_stav.png", True)
