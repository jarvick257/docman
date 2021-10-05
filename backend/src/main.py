import os
import json
from datetime import datetime
from loguru import logger
import shutil

import dash
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash import html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename

from layout import layout, update_preview_grid, show_document
import utils

server = Flask("Docman")
server.config["MAX_CONTENT_LENGTH"] = 128 * 1024 * 1024  # 128 MB
app = dash.Dash(
    "Docman",
    server=server,
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css",
    ],
)
app.layout = layout


@app.callback(
    Output("results", "data"),
    [
        Input("input_tags", "value"),
        Input("input_text", "value"),
        Input("input_date", "start_date"),
        Input("input_date", "end_date"),
    ],
)
def update_result_store(tags, text, start_date, end_date):
    if tags is not None and tags != "":
        tags = tags.strip().split(" ")
    matches = utils.db_lookup(tags, text, start_date, end_date)
    print("Matches:", list(matches.keys()))
    return matches


@app.callback(
    Output("input_tags", "value"), [Input({"type": "link_tag", "tag": ALL}, "n_clicks")]
)
def replace_tag_on_link(n_clicks):
    if len(dash.callback_context.triggered) != 1:
        raise PreventUpdate
    caller_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if caller_id == "" or n_clicks == [] or n_clicks == [0]:
        raise PreventUpdate
    return json.loads(caller_id)["tag"]


@app.callback(
    [Output("input_date", "start_date"), Output("input_date", "end_date")],
    [Input({"type": "link_date", "date": ALL}, "n_clicks")],
)
def replace_date_on_link(n_clicks):
    if len(dash.callback_context.triggered) != 1:
        raise PreventUpdate
    caller_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if caller_id == "" or n_clicks == [] or n_clicks == [0]:
        raise PreventUpdate
    return json.loads(caller_id)["date"], json.loads(caller_id)["date"]


@app.callback(Output("previews", "children"), [Input("results", "data")])
def update_previews(results):
    return update_preview_grid(list(results.values()))


@app.callback(
    Output("selection", "data"),
    [
        Input({"type": "preview", "_id": ALL, "row": ALL}, "n_clicks"),
        Input("results", "data"),
    ],
    [State("selection", "data")],
)
def update_selection(n_clicks, results, current_selection):
    if len(dash.callback_context.triggered) != 1:
        raise PreventUpdate
    caller_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if caller_id == "" or n_clicks == [] or n_clicks == [0]:
        raise PreventUpdate
    if caller_id == "results":
        # clear selection on new results
        return None
    caller_id = json.loads(caller_id)
    item_id = caller_id["_id"]
    item_row = caller_id["row"]
    if current_selection is not None and current_selection["_id"] == item_id:
        # Clicked selected again -> unselect current
        return None
    print(f"Selected {item_id} in row {item_row}")
    selection = results[item_id]
    selection["row"] = item_row
    return selection


@app.callback(
    [
        Output({"type": "hidden_doc", "row": ALL}, "is_open"),
        Output({"type": "hidden_doc", "row": ALL}, "children"),
    ],
    [Input("selection", "data")],
    [State({"type": "hidden_doc", "row": ALL}, "is_open")],
)
def update_doc_view(selection, current_collapses):
    is_open = [False] * len(current_collapses)
    children = [[]] * len(current_collapses)
    if selection is None:
        # close all
        return is_open, children
    item_id = selection["_id"]
    item_row = selection["row"]
    print(f"Selected {item_id} in row {item_row}")
    is_open[item_row] = True
    children[item_row] = show_document(selection)
    return is_open, children


@server.route("/thumb/<image>")
def serve_thumbnail(image):
    print(f"Requested thumb {image}")
    path, image = utils.get_thumbnail(image)
    # return "Document not found!", 404
    return send_from_directory(path, image)


@server.route("/pdf/<document>")
def serve_pdf(document):
    if not os.path.isfile(utils.archive(document)):
        return "Document not found!", 404
    return send_from_directory(utils.archive(), document)


@server.route("/add", methods=["POST"])
def on_add():
    pdf = request.files.get("pdf")
    if pdf is None:
        return "No pdf transmitted!", 400
    tmp_path = "/tmp/newdoc.pdf"
    pdf.save(tmp_path)
    # Extract data
    title, time, tags, text, filename = utils.read_pdfa(tmp_path)
    # Save to final path
    path = utils.archive(filename)
    if os.path.isfile(path):
        logger.error(f"Can't add pdf {path} because it already exists!")
        return "Document already exists!", 409
    logger.info(f"Saving pdf to {path}")
    shutil.move(tmp_path, path)
    # Register doc in db
    return utils.db_add(filename, title, time, tags, text)


@server.route("/update/<_id>", methods=["POST"])
def on_update(_id):
    pdf = request.files.get("pdf")
    if pdf is None:
        return "No pdf transmitted!", 400
    tmp_path = "/tmp/newdoc.pdf"
    pdf.save(tmp_path)
    # Extract data
    title, time, tags, text, filename = utils.read_pdfa(tmp_path)

    # Remove old files and db entry
    txt, code = utils.db_delete(_id)
    if code != 201:
        return txt, code

    # Save to final path
    path = utils.archive(filename)
    if os.path.isfile(path):
        logger.error(f"Can't add pdf {path} because it already exists!")
        return "Document already exists!", 409
    logger.info(f"Saving pdf to {path}")
    shutil.move(tmp_path, path)
    # Register doc in db
    return utils.db_add(filename, title, time, tags, text, _id)


@server.route("/remove", methods=["POST"])
def on_remove():
    query = request.get_json()
    for _id in query["ids"]:
        txt, code = utils.db_delete(_id)
        if code != 201:
            return txt, code
    return "OK", 201


@server.route("/query", methods=["GET"])
def on_query():
    query = request.get_json()
    matches = utils.db_lookup(
        _id=query.get("id", None),
        tags=query.get("tags", None),
        text=query.get("text", None),
        date_from=query.get("date_from", None),
        date_until=query.get("date_until", None),
    )
    if query.get("n_results", -1) > 0:
        # limit matches to first n_results keys
        keys = list(matches.keys())[: int(query["n_results"])]
        matches = {k: matches[k] for k in keys}
    return jsonify(matches)


if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        port=int(os.environ.get("DOCMAN_PORT", "80")),
        debug=os.environ.get("DOCMAN_DEBUG", "FALSE") == "TRUE",
    )
