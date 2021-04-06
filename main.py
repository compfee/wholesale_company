import pandas as pd
import dash
from connect_sql import Sql
import interface
db=Sql()
df= pd.read_sql("select goods.id,name,w.good_count as warehouse1,w22.good_count as warehouse2,priority from goods left join warehouse1 w on goods.id = w.good_id left join warehouse2 w22 on goods.id = w22.good_id ",db.db_connect)
db.cursor.execute("select goods.id,name,w.good_count as warehouse1,w22.good_count as warehouse2,priority from goods left join warehouse1 w on goods.id = w.good_id left join warehouse2 w22 on goods.id = w22.good_id; ")
dff=db.cursor.fetchall()
old_data=df.to_dict('records')
app = dash.Dash()

interface.inter(db,df,old_data,app)

if __name__ == '__main__':

    app.run_server(debug=False)