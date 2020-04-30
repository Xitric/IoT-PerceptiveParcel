from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug.exceptions import NotFound
from repository import db_context
from repository import ontology_context
from mqtt import mqtt_service
from web import package_manager
import json

app = Flask(__name__,
            static_url_path="",
            static_folder="static",
            template_folder="templates")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route(r"/")
def index():
    return render_template("index.html")

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

@app.route("/map/ping")
def ping():
    package_id = request.args.get("packid")
    mqtt_service.ping_package(package_id)
    return redirect(url_for('showMap', packid=package_id))

@app.route("/admin")
def admin():
    package_types = ontology_context.get_package_types()
    return render_template("admin.html", packageTypes=package_types)

@app.route("/admin/newPackage")
def newPackage():
    device_id = request.args.get("deviceId")
    package_type = request.args.get("packageType")
    package_manager.assign_package(device_id, package_type)
    return redirect(url_for('admin'))

@app.errorhandler(404)
def not_found(error: NotFound):
    return render_template('notfound.html', error=error), 404

def start():
    app.run(debug=True)
