from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template(
        "index.html",
        script_path=url_for("static", filename="loader.js"),
        img_bg=url_for("static", filename="img/bg.png"),
        img_black=url_for("static", filename="img/B_stone.png"),
        img_white=url_for("static", filename="img/W_stone.png"),
    )
