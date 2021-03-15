import psycopg2
import dash_core_components as dcc
import pandas as pd
import dash
import dash_html_components as html
import dash_table
import pprint
from dash.dependencies import Input, Output

db_connect = psycopg2.connect(user="postgres",
                                         password="root",
                                         host="localhost",
                                         port="5432",
                                         database="wholesale_company",
                                         options="-c search_path=dbo,public")

cursor = db_connect.cursor()
df= pd.read_sql("select goods.id,name,w.good_count as warehouse1,w22.good_count as warehouse2,priority from goods left join warehouse1 w on goods.id = w.good_id left join warehouse2 w22 on goods.id = w22.good_id ",db_connect)

cursor.execute("select goods.id,name,w.good_count as warehouse1,w22.good_count as warehouse2,priority from goods left join warehouse1 w on goods.id = w.good_id left join warehouse2 w22 on goods.id = w22.good_id; ")
dff=cursor.fetchall()
old_data=df.to_dict('records')
app = dash.Dash()

def discrete_background_color_bins(df, n_bins=5, columns='all'):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    df_max = 1
    df_min = 0
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]['seq']['YlGn'][i - 1]
        color = 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return (styles, html.Div(legend, style={'padding': '5px 0 5px 0'}))

(styles, legend) = discrete_background_color_bins(df, columns=['priority'])


app.layout = html.Div([
    legend,
    dcc.Input(id='input-1-state', type='text', value='Montréal'),
    dcc.Input(id='input-2-state', type='text', value='Canada'),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='output-state'),
    dash_table.DataTable(
        data=df.to_dict('records'),
        editable=True,
        sort_action='native',
        id='editing-prune-data',
        selected_rows=[],
        columns=[{'name': i, 'id': i} for i in df.columns],
        style_data_conditional=[styles,
                                {'if': {'state': 'active'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                 'border': '1px solid rgb(0, 116, 217)'}],
        style_cell={
        'textAlign': 'left',
        },


    ),
    html.Div(id='editing-prune-data-output')
])



@app.callback(Output('editing-prune-data-output', 'active_cell'),
              [Input('editing-prune-data', 'data'),
              Input('editing-prune-data', 'active_cell')])

def display_output(rows,active_cell):
    if active_cell:
     active_row=active_cell["row"]
     pruned_rows = []
     i=0
     for row in rows:
        i+=1
        # require that all elements in a row are specified
        # the pruning behavior that you need may be different than this

        if all([cell != '' for cell in row.values()]):

            pruned_rows.append(row)
            if active_cell["column_id"]=="warehouse1":
              if str(old_data[i-1]["warehouse1"])=='nan':
                if i==(active_row):
                 cursor.execute("insert into warehouse1(good_id,good_count) values (%s,%s)",
                           (str(row["id"]), (str(row["warehouse1"]))))
                 db_connect.commit()
              elif str(old_data[i-1]["warehouse1"])!='nan':
                  if i == (active_row):
                      cursor.execute("update warehouse1 set good_count=%s where good_id=%s",
                                   ( (str(row["warehouse1"])),str(row["id"])))
                      db_connect.commit()
            elif active_cell["column_id"]=="warehouse2":
                if str(old_data[i - 1]["warehouse2"]) == 'nan':
                    if i == (active_row):
                        cursor.execute("insert into warehouse1(good_id,good_count) values (%s,%s)",
                                       (str(row["id"]), (str(row["warehouse2"]))))
                        db_connect.commit()
                elif str(old_data[i - 1]["warehouse2"]) != 'nan':
                    if i == (active_row):
                        cursor.execute("update warehouse2 set good_count=%s where good_id=%s",
                                       ((str(row["warehouse2"])), str(row["id"])))
                        db_connect.commit()


     return html.Div([
        html.Div('Raw Data'),
        html.Pre(pprint.pformat(rows)),
        html.Hr(),
        html.Div('Pruned Data'),
        html.Pre(pprint.pformat(pruned_rows)),
        ])


if __name__ == '__main__':
    app.run_server(debug=False)