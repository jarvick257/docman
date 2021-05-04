import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


def _input_tag():
    return (
        dbc.InputGroup(
            children=[
                dbc.InputGroupAddon(
                    "Tags",
                    addon_type="prepend",
                    style=dict(height="100%"),
                ),
                dbc.Input(id="input_tags", style=dict(height="100%")),
            ],
            style=dict(height="100%"),
        ),
    )


def _input_text():
    return dbc.InputGroup(
        children=[
            dbc.InputGroupAddon(
                "Text",
                addon_type="prepend",
                style=dict(height="100%"),
            ),
            dbc.Input(id="input_text", style=dict(height="100%")),
        ],
        style=dict(height="100%"),
    )


def _input_date():
    return dbc.InputGroup(
        [
            dbc.InputGroupAddon("Date", addon_type="prepend"),
            dcc.DatePickerRange(
                id="input_date",
                clearable=True,
                display_format="YYYY-M-D",
                style={
                    "flex": "1 1 auto",
                    "width": "1%",
                    "display": "flex",
                },
            ),
        ]
    )


def _title_row():
    return dbc.Row([html.H1("Docman")])


def _input_row():
    return dbc.Row(
        dbc.Card(
            dbc.Row(
                [
                    dbc.Col(_input_tag(), width=4),
                    dbc.Col(_input_text(), width=4, style=dict(height="100%")),
                    dbc.Col(_input_date(), width=4),
                ]
            ),
            style=dict(width="100%", border="0px"),
        )
    )


def _output_row():
    return dbc.Row(id="previews", style={"margin-top": "1em"})
    # dbc.Card( dbc.Row( [ dbc.Col( dbc.ListGroup( id="result_list", children=[],), width=4,), dbc.Col( html.Div(id="result_viewer"), width=8,), ]), style=dict(width="100%", margin="1em 0 0 0", border="0px"),))


def _preview_row(matches: list, row: int, n_cols: int):
    if matches == []:
        return []
    thumbnails = []
    for match in matches:
        url = f"/thumb/{match['pdf']}".rsplit(".", 1)[0] + ".jpg"
        prev_id = {"type": "preview", "_id": match["_id"], "row": row}
        thumbnails.append(
            dbc.Col(
                html.Img(src=url, id=prev_id, n_clicks=0, style={"width": "100%"}),
                width=12 // n_cols,
            )
        )
    thumbnails = dbc.Row(thumbnails, style={"width": "100%"})
    hidden_doc = dbc.Row(
        dbc.Col(dbc.Collapse(id={"type": "hidden_doc", "row": row}, is_open=False)),
        style={"width": "100%", "margin-bottom": "1em", "margin-top": "1em"},
    )
    return [thumbnails, hidden_doc]


def update_preview_grid(matches: list):
    n_cols = 4
    max_rows = 5
    row = 0
    grid = []
    while matches[row * n_cols :] != []:
        grid += _preview_row(matches[row * n_cols : (row + 1) * n_cols], row, n_cols)
        row += 1
        if row == max_rows:
            break
    return grid


def show_document(match: dict):
    url = f"/pdf/{match['pdf']}"
    iframe = html.Iframe(src=url, style={"width": "100%", "height": "100%"})
    text = [
        html.H3(match["title"].replace("_", " ")),
        html.H4(
            html.A(
                match["date"],
                id={"type": "link_date", "date": match["date"]},
                href="#",
                n_clicks=0,
                style={"text-decoration": "none", "color": "inherit"},
            )
        ),
        html.P(
            [
                dbc.Badge(
                    tag,
                    id={"type": "link_tag", "tag": tag},
                    href="#",
                    n_clicks=0,
                    color="primary",
                    className="mr-1",
                )
                for tag in match["tags"]
            ]
        ),
        html.P(match["ocr"]),
    ]
    return dbc.Row([dbc.Col(text, width=4), dbc.Col(iframe)])


layout = html.Div(
    dbc.Container(
        [
            dcc.Store("results", data={}),
            dcc.Store("selection", data=None),
            _title_row(),
            _input_row(),
            _output_row(),
        ]
    )
)
