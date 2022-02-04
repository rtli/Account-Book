from datetime import datetime

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Sankey
from pyecharts.globals import ThemeType

import constants
import csv_handler

date = ".".join([str(datetime.now().year), str(datetime.now().month)])


try:
    data = pd.read_csv(
        constants.SPENDING_FILENAME,
        encoding=constants.ENCODING,
        header=None,
    )
    sort = pd.read_csv(
        constants.CLASSIFIER_FILENAME,
        encoding=constants.ENCODING,
        header=None,
    )
except FileNotFoundError:
    csv_handler.init_first_classifier()
    temp = csv_handler.get_last_line()
    data = pd.read_csv(
        constants.SPENDING_FILENAME,
        encoding=constants.ENCODING,
        header=None,
    )
    sort = pd.read_csv(
        constants.CLASSIFIER_FILENAME,
        encoding=constants.ENCODING,
        header=None,
    )
nodes, links = [], []
first_sorted_sum, second_sorted_sum, classifier = {}, {}, {}


def init_classifier():
    for i in sort.values:
        classifier[i[0]] = i[1]


def init_nodes():
    for i in range(2):
        for j in data[i].unique():
            nodes.append({constants.NAME: j})
    for i in sort[1].unique():
        nodes.append({constants.NAME: i})


def construct_layers():
    for i in data.values:
        first_sorted_sum[str(i[1])] = (
            round(i[2], 2)
            if str(i[1]) not in first_sorted_sum
            else first_sorted_sum[str(i[1])] + round(i[2], 2)
        )

    for (key, value) in first_sorted_sum.items():
        second_sorted_sum[classifier[key]] = (
            value
            if classifier[key] not in second_sorted_sum
            else second_sorted_sum[classifier[key]] + value
        )


def construct_nodes():
    for i in data.values:
        links.append(
            {
                constants.SOURCE: i[0],
                constants.TARGET: i[1],
                constants.VALUE: round(i[2], 2),
            },
        )

    for (key, value) in {**first_sorted_sum, **second_sorted_sum}.items():
        links.append(
            {
                constants.SOURCE: key,
                constants.TARGET: classifier[key],
                constants.VALUE: round(value, 2),
            },
        )


def Sankey_graph():
    c = (
        Sankey(
            init_opts=opts.InitOpts(
                width=constants.SANKEY_WIDTH,
                height=constants.SANKEY_WIDTH,
                theme=ThemeType.LIGHT,
                page_title=constants.SANKEY_TITLE,
            ),
        )
        .add(
            "Ledger",
            nodes,
            links,
            linestyle_opt=opts.LineStyleOpts(
                opacity=0.5,
                curve=0.5,
                color=constants.SOURCE,
            ),
            label_opts=opts.LabelOpts(position="right"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="The Ledger",
                subtitle=date,
            ),
        )
    )

    c.render(constants.RESULT_FILENAME)


def main():
    init_classifier()
    init_nodes()
    construct_layers()
    construct_nodes()
    Sankey_graph()


if __name__ == "__main__":
    main()
