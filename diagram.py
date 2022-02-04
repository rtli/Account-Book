from datetime import datetime

import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Sankey
from pyecharts.globals import ThemeType

import constants
import csv_handler


def read_csv():
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
    return data, sort


def init_classifier(sort):
    classifier = {}
    for line in sort.values:
        classifier[line[0]] = line[1]
    return classifier


def init_nodes(data, sort):
    nodes = []
    for i in range(2):
        for j in data[i].unique():
            nodes.append({constants.NAME: j})
    for i in sort[1].unique():
        nodes.append({constants.NAME: i})
    return nodes


def construct_first_sorted_sum(data):
    first_sorted_sum = {}
    for i in data.values:
        first_sorted_sum[str(i[1])] = (
            round(i[2], 2)
            if str(i[1]) not in first_sorted_sum
            else first_sorted_sum[str(i[1])] + round(i[2], 2)
        )
    return first_sorted_sum


def construct_second_sorted_sum(classifier: dict, first_sorted_sum: dict):
    second_sorted_sum = {}
    for (key, value) in first_sorted_sum.items():
        second_sorted_sum[classifier[key]] = (
            value
            if classifier[key] not in second_sorted_sum
            else second_sorted_sum[classifier[key]] + value
        )
    return second_sorted_sum


def construct_layers(data, classifier):
    first_sorted_sum = construct_first_sorted_sum(data)
    second_sorted_sum = construct_second_sorted_sum(classifier, first_sorted_sum)
    return first_sorted_sum, second_sorted_sum


def construct_nodes(
    data,
    classifier: dict,
    first_sorted_sum: dict,
    second_sorted_sum: dict,
):
    links = []
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
    return links


def generate_sankey_graph(
    nodes: dict,
    links: dict,
):
    date = ".".join([str(datetime.now().year), str(datetime.now().month)])
    sankey_graph = (
        Sankey(
            init_opts=opts.InitOpts(
                width=constants.SANKEY_WIDTH,
                height=constants.SANKEY_WIDTH,
                theme=ThemeType.LIGHT,
                page_title=constants.SANKEY_TITLE,
            ),
        )
        .add(
            constants.LEDGER,
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
                title=constants.LEDGER,
                subtitle=date,
            ),
        )
    )

    sankey_graph.render(constants.RESULT_FILENAME)


def generate_diagram():
    data, sort = read_csv()
    classifier = init_classifier(sort)
    nodes = init_nodes(data, sort)
    first_sorted_sum, second_sorted_sum = construct_layers(data, classifier)
    links = construct_nodes(data, classifier, first_sorted_sum, second_sorted_sum)
    generate_sankey_graph(nodes, links)
    return True
