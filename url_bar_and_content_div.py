import dash_html_components as html
from dash.dependencies import Input, Output, State
import psycopg2
import dash_core_components as dcc
import pandas as pd
import dash
import dash_html_components as html
import dash_table
import pprint
from dash.dependencies import Input, Output, State
from connect_sql import Sql
import dash_auth
import plotly
import login
import flask


url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])