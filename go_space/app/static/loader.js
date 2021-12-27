var canvas = document.getElementById("board");
var ctx = canvas.getContext("2d");
canvas.width = 731;
canvas.height = 731;

var background = document.getElementById("img_bg");

function draw_board() {
    var canvas = document.getElementById("board");
    var ctx = canvas.getContext("2d");
    canvas.width = 450;
    canvas.height = 450;

    var background = document.getElementById("img_bg");

    ctx.drawImage(background, 0, 0);   
}
