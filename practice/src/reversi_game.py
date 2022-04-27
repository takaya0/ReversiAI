
import tkinter
import tkinter.messagebox

import json
import random


def read_json_file(jsonFileName):
    json_file = open(jsonFileName, 'r')
    return json.load(json_file)


class Reversi():
    '''
        ReversiのGUIアプリ(以下のサイトを参考に作成)
        https://daeudaeu.com/tkinter-othello/

    '''

    def __init__(self, app, configFile):
        self.app = app

        # アプリのコンフィグ
        config = read_json_file(configFile)
        self.config = config

        # オセロのボード
        self.board = None

        # オセロの先攻(黒色)、後攻(白色)を決める
        self.user_color = 'BLACK'
        self.cpu_color = 'WHITE'

        # 名前
        self.user_name = input("ユーザー名を入力してください。")
        self.cpu_name = 'cpu'

        self.canvas = tkinter.Canvas(
            app,
            bg=config['BACKGROUND'],
            width=config['BOARDSIZE'] + 1,
            height=config['BOARDSIZE'] + 1,
            highlightthickness=0
        )

        self.canvas.pack(padx=10, pady=10)

        self.reset()

    def reset(self):
        '''
            オセロの盤面初期化
        '''

        # (8, 8)の盤面リストを作成
        self.board = [[None] * 8 for _ in range(8)]

        # マス目の大きさ
        self.square_size = self.config['BOARDSIZE'] // 64

        # マスを描画
        for y in range(8):
            for x in range(8):
                # 長方形の開始・終了座標を計算
                sx = x * self.square_size
                sy = y * self.square_size
                ex = (x + 1) * self.square_size
                ey = (y + 1) * self.square_size

                # 長方形を描画
                tag_name = 'square_' + str(x) + '_' + str(y)
                self.canvas.create_rectangle(
                    sx, sy,
                    ex, ey,
                    tag=tag_name
                )

        # あなたの石の描画位置を計算
        user_init_pos_1_x = 4
        user_init_pos_1_y = 4
        user_init_pos_2_x = 3
        user_init_pos_2_y = 3
        user_init_pos = (
            (user_init_pos_1_x, user_init_pos_1_y),
            (user_init_pos_2_x, user_init_pos_2_y)
        )

        # 計算した描画位置に石（円）を描画
        for x, y in user_init_pos:
            self.draw_disk(x, y, self.user_color)

        # 対戦相手の石の描画位置を計算
        cpu_init_pos_1_x = 3
        cpu_init_pos_1_y = 4
        cpu_init_pos_2_x = 4
        cpu_init_pos_2_y = 3

        cpu_init_pos = (
            (cpu_init_pos_1_x, cpu_init_pos_1_y),
            (cpu_init_pos_2_x, cpu_init_pos_2_y)
        )

        # 計算した描画位置に石（円）を描画
        for x, y in cpu_init_pos:
            self.draw_disk(x, y, self.cpu_color)

        # 最初に置くことができる石の位置を取得
        legal_places = self.get_legal_places()
        # その位置を盤面に表示
        self.highlight_legal_places(legal_places)

    def draw_disk(self, x, y, color):
        '''(x,y)に色がcolorの石を置く（円を描画する）'''

        # (x,y)のマスの中心座標を計算
        cx = (x + 0.5) * self.square_size
        cy = (y + 0.5) * self.square_size

        # 中心座標から円の開始座標と終了座標を計算
        sx = cx - (self.square_size * 0.8) // 2
        sy = cy - (self.square_size * 0.8) // 2
        ex = cx + (self.square_size * 0.8) // 2
        ey = cy + (self.square_size * 0.8) // 2

        # 円を描画する
        tag_name = 'disk_' + str(x) + '_' + str(y)
        self.canvas.create_oval(
            sx, sy,
            ex, ey,
            fill=color,
            tag=tag_name
        )

        # 描画した円の色を管理リストに記憶させておく
        self.board[y][x] = color
