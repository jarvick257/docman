import os
import json

import dash
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate

from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename

from layout import layout, update_preview_grid, show_document
from utils import db_lookup, db_add, archive, get_thumbnail

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
    matches = db_lookup(tags, text, start_date, end_date)
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
    print("replace_date_link", n_clicks)
    print("replace_date_link", caller_id)
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
    print("CallerID: ", caller_id)
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
    path, image = get_thumbnail(image)
    # return "Document not found!", 404
    return send_from_directory(path, image)


@server.route("/scan/<image>")
def serve_scan(image):
    path = os.path.join(archive(), ".scans")
    if not os.path.isfile(os.path.join(path, image)):
        return "Documnet not found!", 404
    return send_from_directory(path, image)


@server.route("/pdf/<document>")
def serve_pdf(document):
    if not os.path.isfile(os.path.join(archive(), document)):
        return "Document not found!", 404
    return send_from_directory(archive(), document)


@server.route("/add", methods=["POST"])
def on_upload():
    scans = request.files.getlist("scan")
    pdf = request.files.get("pdf")
    post = request.files.get("post")
    if pdf is None or post is None:
        return "Need at least post and pdf file!", 400

    # Check if post is correct json file
    post_path = secure_filename(post.filename)
    post.save(post_path)
    try:
        with open(post_path, "r") as fp:
            post = json.load(fp)
        os.remove(post_path)
    except:
        os.remove(post_path)
        return "Errors in submitted post file", 400
    return db_add(post, pdf, scans)


@server.route("/query", methods=["GET"])
def on_query():
    query = request.get_json()
    matches = db_lookup(
        _id=query.get("id", None),
        tags=query.get("tags", None),
        text=query.get("text", None),
        date_from=query.get("date_from", None),
        date_until=query.get("date_until", None),
    )
    if query.get("n_results", -1) > 0:
        # limit matches to first n_results keys
        keys = list(matches.keys())[: int(query["n_results"])]
        print(keys)
        matches = {k: matches[k] for k in keys}
    if query.get("id_only", False):
        return jsonify(list(matches.keys()))
    return jsonify(matches)


if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        port=int(os.environ.get("DOCMAN_PORT", "80")),
        debug=os.environ.get("DOCMAN_DEBUG", "FALSE") == "TRUE",
    )
