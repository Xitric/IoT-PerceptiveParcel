from flask import Flask, render_template

app = Flask(__name__,
            static_url_path="",
            static_folder="static",
            template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html", key1="ESP32", key2="Wrover")

if __name__ == '__main__':
    app.run(debug=True)
