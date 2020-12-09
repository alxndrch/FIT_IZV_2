#!/usr/bin/env python3.8
# coding=utf-8

# TODO: pridat sloupce pro category typ
# TODO: osetrit ukladani grafu, co delat kdyz soubor existuje?
# TODO: prijit na lepsi zpusob jak udelat plot

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

    paper_a4 = (8.27, 11.69)  # rozmery formatu A4
    palette = "blend:#2980b9,#2c3e50"  # vlastni barvna paleta grafu

    # ----- Agregace dat -----

    df = df.groupby(by="region").agg({"p13a": "sum",  # a)
                                      "p13b": "sum",  # b)
                                      "p13c": "sum",  # c)
                                      "p1": "count"   # d)
                                      }).reset_index()

    df = df.sort_values("p1", ascending=False)  # serazeni podle poctu nehod

    # ----- Vytvareni grafu -----

    sns.set_palette(sns.color_palette("Paired"))

    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=paper_a4,
                             constrained_layout=True)

    fig.suptitle("Následky nehod v jednotlivých regionech", fontsize=14)
    fig.canvas.set_window_title("Následky nehod v jednotlivých regionech")

    (ax1, ax2, ax3, ax4) = axes

    # a)počet lidí, kteří zemřeli při nehodě (​p13a​)
    ax1 = sns.barplot(data=df, x="region", y="p13a", ax=ax1, palette=palette)
    # b)počet lidí, kteří byli těžce zranění (​p13b​)
    ax2 = sns.barplot(data=df, x="region", y="p13b", ax=ax2, palette=palette)
    # c)počet lidí, kteří byli lehce zranění (​p13c​)
    ax3 = sns.barplot(data=df, x="region", y="p13c", ax=ax3, palette=palette)
    # d)celkový počet nehod v daném kraji
    ax4 = sns.barplot(data=df, x="region", y="p1", ax=ax4, palette=palette)

    # nadpisy grafu
    titles = ["Počet lidí, kteří zemřeli při nehodě",  # a)
              "Počet lidí, kteří byli těžce zranění",  # b)
              "Počet lidí, kteří byli lehce zranění",  # c)
              "Celkový počet nehod v daném kraji"]     # d)

    # popis osy y
    labels_y = ["Počet zemřelých",        # a)
                "Počet těžce zraněných",  # b)
                "Počet lehce zraněných",  # c)
                "Počet nehod"]            # d)

    # nastaveni grafu
    for ax, title, label in zip(axes, titles, labels_y):
        _set_ax(ax, "Regiony", label, title)

    # ----- Vystup -----

    # ulozeni grafu
    if fig_location is not None:
        plt.savefig(fig_location)

    # zobrazeni grafu
    if show_figure:
        plt.show()


# Ukol3: příčina nehody a škoda
def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    pass


# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass


# pomocna funkce pro vykreslovani grafu
def _set_ax(ax, xlabel, ylabel, title):
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(which="major", axis="y", color="gray", linewidth=0.4)
    ax.grid(b=False, which="major", axis="x")


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", True)
    plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    # plot_damage(df, "02_priciny.png", True)
    # plot_surface(df, "03_stav.png", True)
