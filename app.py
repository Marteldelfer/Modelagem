from dash import Dash, Input, Output, html

import sidebar as sidebar
from graficos import painel

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard DW"

app.layout = html.Div([
    sidebar.layout(),
    html.Div([
        html.H3("Dashboard"),
        painel.layout()
    ], className="content"),
])

sidebar.register_callbacks(app)
painel.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
