from flask import Flask, render_template, request

app = Flask(__name__,
            static_url_path="",
            static_folder="static",
            template_folder="templates")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route(r"/")
def index():
    return render_template("index.html", key1="ESP32", key2="Wrover")


#TODO: use packid to show relevant map...
@app.route("/map")
def showMap():
   return render_template("map.html")
   #return '%s' % request.args.get("packid")

@app.route("/admin")
def showAdmin():
    return render_template("admin.html")


if __name__ == '__main__':
    app.run(debug=True)
