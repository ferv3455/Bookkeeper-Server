import io
import json

from matplotlib import pyplot as plt
import mysql.connector
import pandas as pd
from pandas.plotting import table
import numpy as np


with open("/var/www/Bookkeeper-Server/mysql.json", "r", encoding="utf-8") as fin:
    p = json.load(fin)
connection = mysql.connector.connect(**p)
cursor = connection.cursor()

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax.get_figure(), ax


def lookup(args):
    if not args:
        # get all data sorted by date
        query = "SELECT * FROM accounts ORDER BY date, accountid;"
        result = pd.read_sql(query, connection)
        buf = io.BytesIO()
        fig, ax = render_mpl_table(result, header_columns=0, col_width=2.0)
        fig.savefig(buf, format='jpg')
        return buf

    plt.figure()
    plt.plot([1, 2])
    plt.title("test")

    # Save image
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg')
    return buf


def graph(args):
    plt.figure()
    plt.plot([1, 2])
    plt.title("test")

    # Save image
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg')
    return buf


def insert(args):
    '''
    args: 
        [date(str, 2022-12-13), content(str), price(float), 
        person(str), form(str), place(str), type(str)]
    '''
    command = f"INSERT INTO accounts " \
        f"(date, content, price, person, form, place, type)" \
        f"VALUES ('{args[0]}', '{args[1]}', {args[2]}, '{args[3]}', " \
        f"'{args[4]}', '{args[5]}', '{args[6]}');"
    try:
        cursor.execute(command)
        connection.commit()
        return True
    except:
        return False
