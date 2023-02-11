// Global variables for good programming
var canvas, ctx;
var background, white_stone, black_stone;

const WHITE = 0;
const BLACK = 1;

function draw_stone(row, col, player) {
    // 0-indexed
    const SIDE = 15;
    const row_0 = 5;
    const col_0 = 5;
    const d_row = 20;
    const d_col = 20;

    row_st = row_0 + row * d_row;
    row_en = row_st + SIDE;
    col_st = col_0 + col * d_col;
    col_en = col_st + SIDE;
    if (player == BLACK) {
        stone_img = black_stone;
    } else {
        stone_img = white_stone;
    }
    ctx.drawImage(stone_img, col_st, row_st, col_en, row_en);
}

function init() {
    canvas = document.getElementById("board");
    ctx = canvas.getContext("2d");
    canvas.width = 450;
    canvas.height = 450;

    background = document.getElementById("img_bg");
    black_stone = document.getElementById("img_black");
    white_stone = document.getElementById("img_white");
}

function draw_board() {
    ctx.drawImage(background, 0, 0, 450, 450);
    draw_stone(0, 0, BLACK);
    draw_stone(0, 1, BLACK);
    draw_stone(0, 2, BLACK);
    draw_stone(0, 3, BLACK);
    draw_stone(0, 4, BLACK);
    draw_stone(0, 5, BLACK);
    draw_stone(0, 6, BLACK);
    draw_stone(0, 7, BLACK);
    draw_stone(0, 8, BLACK);
}
