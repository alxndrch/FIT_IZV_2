#!/usr/bin/env python3.8
# coding=utf-8

# TODO: pridat sloupce pro category typ
# TODO: osetrit ukladani grafu, co delat kdyz soubor existuje?
# TODO: opravit cut interval pro p53

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
    category_col = ["p36", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p15",
                    "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23",
                    "p24", "p27", "p28", "p39", "p44", "p45a", "p48a", "p49",
                    "p50a", "p50b", "p51", "p55a", "p57", "p58", "q", "t",
                    "p5a"]

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
    palette = "blend:#2c3e50,#2980b9"  # vlastni barvna paleta grafu

    # ----- Agregace dat -----

    df = df.groupby(by="region").agg({"p13a": "sum",  # a)
                                      "p13b": "sum",  # b)
                                      "p13c": "sum",  # c)
                                      "p1": "count"   # d)
                                      }).reset_index()

    df = df.sort_values("p1", ascending=False)  # serazeni podle poctu nehod

    # ----- Vytvareni grafu -----

    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=paper_a4,
                             constrained_layout=True)

    fig.suptitle("Následky nehod v jednotlivých regionech", fontsize=14)
    fig.canvas.set_window_title("Následky nehod v jednotlivých regionech")

    ax1, ax2, ax3, ax4 = axes

    # a)počet lidí, kteří zemřeli při nehodě (​p13a​)
    sns.barplot(data=df, x="region", y="p13a", ax=ax1, palette=palette)
    # b)počet lidí, kteří byli těžce zranění (​p13b​)
    sns.barplot(data=df, x="region", y="p13b", ax=ax2, palette=palette)
    # c)počet lidí, kteří byli lehce zranění (​p13c​)
    sns.barplot(data=df, x="region", y="p13c", ax=ax3, palette=palette)
    # d)celkový počet nehod v daném kraji
    sns.barplot(data=df, x="region", y="p1", ax=ax4, palette=palette)

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

    regions = ["PHA", "JHM", "VYS", "ZLK"]  # vybrane kraje

    paper_a4 = (11.69, 8.27)  # rozmery formatu A4

    # priciny nehod, ciselna reprezentace
    p12_bins = [100, 200, 300, 400, 500, 600, 615]
    # skody na vozidlech, ciselna reprezentace
    p53_bins = [0, 50, 200, 500, 1000, np.inf]
    # priciny nehod
    p12_labels = ["Nezaviněnná řidičem", "Nepřiměřená rychlost jízdy",
                  "Nesprávné předjíždění", "Nedání přednosti v jízdě",
                  "Nesprávný způsob jízdy", "Technická závada vozidla"]
    # skody na vozidlech, intervaly
    p53_labels = ["< 50", "50 - 200", "200 - 500", "500 - 1 000", "> 1 000"]

    # ----- Agregace dat -----

    # vyber pozadovych radku a sloupcu
    # sloupce p1 pro agregaci dat (count)
    df = df.loc[df["region"].isin(regions), ["p1", "p12", "p53", "region"]]
    df["p53"] = df["p53"].div(10)
    # rozdelene priciny nehody
    df["p12"] = pd.cut(df["p12"], bins=p12_bins, labels=p12_labels,
                       include_lowest=True)
    # rozdeleni skody na vozidlech
    df["p53"] = pd.cut(df["p53"], bins=p53_bins, labels=p53_labels,
                       include_lowest=True)

    df = df.groupby(by=["region", "p53", "p12"]).agg({"p1": "count"}).reset_index()
    df = df.set_index(["region"])

    # ----- Vytvareni grafu -----

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=paper_a4)

    fig.suptitle("Příčina nehody a škoda", fontsize=14)
    fig.canvas.set_window_title("Příčina nehody a škoda")

    (ax1, ax2), (ax3, ax4) = axes

    # region: Praha
    sns.barplot(data=df.loc[("PHA")], ax=ax1, x="p53", y="p1", hue="p12")
    ## region: Jihomoravky kraj
    sns.barplot(data=df.loc[("JHM")], ax=ax2, x="p53", y="p1", hue="p12")
    ## region: Vysocina
    sns.barplot(data=df.loc[("VYS")], ax=ax3, x="p53", y="p1", hue="p12")
    ## region: Zlinsky kraj
    sns.barplot(data=df.loc[("ZLK")], ax=ax4, x="p53", y="p1", hue="p12")

    # nadpisy grafu
    titles = ["Praha", "Jihomoravský kraj", "Vysočina", "Zlínský kraj"]

    # nastaveni grafu
    for ax, title in zip([ax1, ax2, ax3, ax4], titles):
        _set_ax(ax, "Škoda [tisíc Kč]", "Počet nehod", title, yscale="log")

    plt.legend(title="Legenda",  loc=(1.04,0.9))
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)

    # ----- Vystup -----

    # ulozeni grafu
    if fig_location is not None:
        plt.savefig(fig_location)

    # zobrazeni grafu
    if show_figure:
        plt.show()


# Ukol 4: povrch vozovky
def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):

    regions = ["PHA", "JHM", "VYS", "ZLK"]  # vybrane kraje
    paper_a4 = (11.69, 8.27)  # rozmery formatu A4
    palette = "blend:#2980b9,#2c3e50"  # vlastni barvna paleta grafu


# pomocna funkce pro vykreslovani grafu
def _set_ax(ax, xlabel, ylabel, title, yscale="linear"):
    ax.legend().remove()
    ax.set_yscale(yscale)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_ylim(bottom=1)
    ax.grid(which="major", axis="y", color="gray", linewidth=0.4)
    ax.grid(b=False, which="major", axis="x")


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", True)
    #plot_conseq(df, fig_location="01_nasledky.png", show_figure=True)
    #plot_damage(df, "02_priciny.png", True)
    plot_surface(df, "03_stav.png", True)
