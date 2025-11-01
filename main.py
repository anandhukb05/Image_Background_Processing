from flask import Flask, render_template


app = Flask(__name__)
#Auto-reload templates without restarting the server
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.route("", methods=["POST", "GET"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)