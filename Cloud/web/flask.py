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

    humidity_data = [{
        "time": point[0],
        "humidity": point[1],
        "latitude": point[2],
        "longitude": point[3]
    } for point in get_humidities(package_id, route)]
    print(humidity_data)
    print(route_data)

    package_data = {"route": route_data, "humidities": humidity_data}

    return render_template("map.html", route=json.dumps(package_data))


@app.route("/admin")
def showAdmin():
    return render_template("admin.html")


@app.errorhandler(404)
def not_found(error: NotFound):
    return render_template('notfound.html', error=error), 404


# Compute the position of humidity events based on their timestamp, by using the positions of the two coordinates
# which the humidity timestamp is between.
def get_humidities(package_id, route_data):
    humidities = db_context.get_humidities(package_id)
    humidity_points = []
    route = route_data

    for humidity in humidities:
        humidity_time = humidity[0]
        humidity_value = humidity[1]
        lower_point_index = 0
        lower_point = ()
        for i, point in enumerate(route):
            point_time = point[0]
            if point_time <= humidity_time:
                lower_point_index = i
                lower_point = point
            if point_time >= humidity_time:
                percent = percentage_to_lower_bound(humidity_time, lower_point[0], point[0])
                humidity_point = midpoint(lower_point[1], lower_point[2], point[1], point[2], percent)
                humidity_latitude = humidity_point[0]
                humidity_longitude = humidity_point[1]
                humidity_points.append((humidity_time, humidity_value, humidity_latitude, humidity_longitude))
                route = route[lower_point_index:]
                break

    return humidity_points


def percentage_to_lower_bound(event_time, lower_time_bound, upper_time_bound):
    return (event_time - lower_time_bound) / (upper_time_bound - lower_time_bound)


def midpoint(latitude1, longitude1, latitude2, longitude2, lower_percentage):
    latitude = latitude1 + (latitude2 - latitude1) * lower_percentage
    longitude = longitude1 + (longitude2 - longitude1) * lower_percentage
    return latitude, longitude


def start_flask():
    app.run(debug=True)
