from flask import Flask, render_template, request, abort
from werkzeug.exceptions import NotFound
from repository import db_context
import json

app = Flask(__name__,
            static_url_path="",
            static_folder="static",
            template_folder="templates")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route(r"/")
def index():
    return render_template("index.html", key1="ESP32", key2="Wrover")

@app.route("/map")
def showMap():
    package_id = request.args.get("packid")
    route = db_context.get_route(package_id)

    if route is None or len(route) == 0:
        abort(404, description="Unknown package ID")

    route_data = [{
        "time": point[0],
        "latitude": point[1],
        "longitude": point[2],
        "accuracy": point[3]
    } for point in route]

    return render_template("map.html", route=json.dumps(route_data))

@app.route("/admin")
def showAdmin():
    return render_template("admin.html")

@app.errorhandler(404)
def not_found(error: NotFound):
    return render_template('notfound.html', error=error), 404

def start_flask():
    app.run(debug=True)
