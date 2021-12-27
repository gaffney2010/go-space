from flask import Flask, url_for

app = Flask(__name__)

@app.route("/")
def hello_world():
    return """
    <script src="{}"></script>
    <body onload="draw_board()">
        <img id="img_bg" src="{}" width="0px"></image>
        <canvas id="board"></canvas>
    </body>
    """.format(url_for('static', filename='loader.js'), url_for('static', filename="img/bg.png"))
