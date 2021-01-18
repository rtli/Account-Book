import pandas as pd
from pyecharts.charts import Page, Sankey
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from datetime import datetime
date = str(datetime.now().year)+"."+str(datetime.now().month)

data = pd.read_csv('spending.csv', encoding='UTF-8', header=None)
sort = pd.read_csv('classifier.csv', encoding='UTF-8', header=None)
nodes, links, first_sorted_sum, second_sorted_sum, classifier = [], [], {}, {}, {}


def init_classifier():
    for i in sort.values:
        classifier[i[0]] = i[1]


def init_nodes():
    for i in range(2):
        for j in data[i].unique():
            nodes.append({'name': j})
    for i in sort[1].unique():
        nodes.append({'name': i})


def construct_layers():
    for i in data.values:
        first_sorted_sum[str(i[1])] = round(i[2], 2) if str(
            i[1]) not in first_sorted_sum else first_sorted_sum[str(i[1])]+round(i[2], 2)

    for (key, value) in first_sorted_sum.items():
        second_sorted_sum[classifier[key]
                          ] = value if classifier[key] not in second_sorted_sum else second_sorted_sum[classifier[key]]+value


def construct_nodes():
    for i in data.values:
        links.append({'source': i[0], 'target': i[1], 'value': round(i[2], 2)})

    for (key, value) in {**first_sorted_sum, **second_sorted_sum}.items():
        links.append(
            {'source': key, 'target': classifier[key], 'value': round(value, 2)})


def Sankey_graph():
    c = (Sankey(init_opts=opts.InitOpts(width="110vw", height="100vh", theme=ThemeType.LIGHT, page_title='Sankey Graph'))
         .add("Ledger", nodes, links, linestyle_opt=opts.LineStyleOpts(opacity=0.5, curve=0.5, color="source"),
              label_opts=opts.LabelOpts(position="right"),).set_global_opts(title_opts=opts.TitleOpts(title="The Ledger", subtitle=date)))

    c.render('result.html')


def main():
    init_classifier()
    init_nodes()
    construct_layers()
    construct_nodes()
    Sankey_graph()

if __name__ == "__main__":
    main()
