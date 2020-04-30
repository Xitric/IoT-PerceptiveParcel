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

    event_data = [{
        "time": point[0],
        "measurement": point[1],
        "latitude": point[2],
        "longitude": point[3],
        "event": point[4]
    } for point in get_events(package_id, route)]

    package_data = {"route": route_data, "events": event_data}

    return render_template("map.html", route=json.dumps(package_data))


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


# Compute the position of events based on their timestamp, by using the positions of the two coordinates
# which the event timestamp is between.
def get_events(package_id, route_data):
    events = db_context.get_events(package_id)
    event_points = []
    route = route_data

    for event in events:
        event_time = event[0]
        event_value = event[1]
        event_type = event[2]
        lower_point_index = 0
        lower_point = None
        for i, point in enumerate(route):
            point_time = point[0]
            if point_time <= event_time:
                lower_point_index = i
                lower_point = point
            if point_time >= event_time and lower_point:
                percent = percentage_to_lower_bound(event_time, lower_point[0], point[0])
                event_point = midpoint(lower_point[1], lower_point[2], point[1], point[2], percent)
                event_latitude = event_point[0]
                event_longitude = event_point[1]
                event_points.append((event_time, event_value, event_latitude, event_longitude, event_type))
                route = route[lower_point_index:]
                break

    return event_points


def percentage_to_lower_bound(event_time, lower_time_bound, upper_time_bound):
    return (event_time - lower_time_bound) / (upper_time_bound - lower_time_bound)


def midpoint(latitude1, longitude1, latitude2, longitude2, lower_percentage):
    latitude = latitude1 + (latitude2 - latitude1) * lower_percentage
    longitude = longitude1 + (longitude2 - longitude1) * lower_percentage
    return latitude, longitude

  
def start():
    app.run(debug=True)
