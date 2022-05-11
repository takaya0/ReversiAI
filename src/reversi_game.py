
import tkinter
import tkinter.messagebox

import json
import torch

import sys
import time

from players import DQN_Player

config_file_path = 'game_config.json'

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def read_json_file(jsonFileName):
    json_file = open(jsonFileName, 'r')
    return json.load(json_file)


class Reversi():
    '''
        ReversiのGUIアプリ(以下のサイトを参考に作成)
        https://daeudaeu.com/tkinter-othello/

    '''

    def __init__(self, app, configFile, model_file):
        self.app = app

        # アプリのコンフィグ
        config = read_json_file(configFile)
        self.config = config

        # オセロのボード
        self.board = None

        # オセロの先攻(黒色)、後攻(白色)を決める
        self.user_color = 'black'
        self.cpu_color = 'white'

        # ユーザー名を入力
        self.user_name = input("ユーザー名を入力してください。\n")

        self.cpu_name = self.config["CPU_NAME"]

        # ターンプレイヤー
        self.turn_player = self.user_name

        self.color = {
            self.user_name: self.user_color,
            self.cpu_name: self.cpu_color
        }

        self.model_file = model_file

        self.canvas = tkinter.Canvas(
            app,
            bg='green',
            width=self.config['BOARD_SIZE'] + 1,
            height=self.config['BOARD_SIZE'] + 1,
            highlightthickness=0
        )

        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind('<ButtonPress>', self.click)

        self.reset()

    def reset(self):
        '''
            オセロの盤面初期化
        '''

        # (8, 8)の盤面リストを作成
        self.board = [[None] * 8 for _ in range(8)]

        # マス目の大きさ
        self.square_size = self.config['BOARD_SIZE'] // 8

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

    def get_legal_places(self):

        leagal_palaces = []

        for y in range(8):
            for x in range(8):
                if self.is_placable(x, y):
                    leagal_palaces.append((x, y))

        return leagal_palaces

    def is_placable(self, x, y):
        # (x, y)に石が置けるのかを判定

        turn_player = self.turn_player
        other = self.cpu_name if turn_player == self.user_name else self.user_name

        if self.board[y][x] is not None:
            return False

        for j in range(-1, 2):
            for i in range(-1, 2):

                if i == 0 and j == 0:
                    continue

                # ボード外は判定しない
                if x + i < 0 or x + i >= 8 or y + j < 0 or y + j >= 8:
                    continue

                if self.board[y + j][x + i] != self.color[other]:
                    continue

                for s in range(2, 8):
                    if x + i * s >= 0 and x + i * s < 8 and y + j * s >= 0 and y + j * s < 8:
                        if self.board[y + j * s][x + i * s] is None:
                            break

                        if self.board[y + j * s][x + i * s] == self.color[turn_player]:
                            return True

        return False

    def highlight_legal_places(self, leagal_palaces):

        if len(leagal_palaces) == 0:
            raise "No legal places"

        for y in range(8):
            for x in range(8):
                tag_name = 'square_' + str(x) + '_' + str(y)

                if (x, y) in leagal_palaces:
                    self.canvas.itemconfig(
                        tag_name,
                        fill='yellow'
                    )
                else:
                    self.canvas.itemconfig(
                        tag_name,
                        fill='green'
                    )

    def highlight_assisted_select(self, x, y):
        tag_name = 'square_' + str(x) + '_' + str(y)

        self.canvas.itemconfig(
            tag_name,
            fill='pink'
        )

    def click(self, event):

        if self.turn_player == self.cpu_name:
            return

        x = event.x // self.square_size
        y = event.y // self.square_size

        if self.is_placable(x, y):
            self.place(x, y, self.color[self.turn_player])

    def place(self, x, y, color):

        self.reverse_pieces(x, y)

        self.draw_disk(x, y, color)

        before_turn_player = self.turn_player
        self.change_turn_player()
        if before_turn_player == self.turn_player:
            other = self.cpu_name if self.turn_player == self.user_name else self.user_name

            print(other + "のターンはスキップされました.")

        else:

            if self.turn_player is None:
                # ゲーム終了
                self.show_result()

                time.sleep(5)
                sys.exit()
                return

        legal_places = self.get_legal_places()
        self.highlight_legal_places(legal_places)

        if self.turn_player == self.user_name:
            if self.config['AI_ASSIST']:
                x, y = self.get_assisted_ai_select(self.model_file)
                self.highlight_assisted_select(x, y)

        if self.turn_player == self.cpu_name:
            self.app.after(1000, self.cpu)

    def show_result(self):
        black_stone_num = 0
        white_stone_num = 0

        for y in range(8):
            for x in range(8):
                if self.board[y][x] == self.user_color:
                    black_stone_num += 1
                elif self.board[y][x] == self.cpu_color:
                    white_stone_num += 1

        result_message = "黒石 : " + \
            str(black_stone_num) + ", 白石 : " + str(white_stone_num) + "\n"
        if black_stone_num > white_stone_num:
            result_message += self.user_name + "の勝利"
        elif black_stone_num < white_stone_num:
            result_message += self.cpu_name + "の勝利"
        else:
            result_message += "引き分け"

        tkinter.messagebox.showinfo("結果", result_message)

    def cpu(self):
        x, y = self.get_ai_select(self.model_file)

        self.place(x, y, self.cpu_color)

    def reverse_pieces(self, x, y):

        if self.board[y][x] is not None:
            return

        turn_player = self.turn_player
        other = self.cpu_name if turn_player == self.user_name else self.user_name

        for j in range(-1, 2):
            for i in range(-1, 2):

                if i == 0 and j == 0:
                    continue

                # ボード外は判定しない
                if x + i < 0 or x + i >= 8 or y + j < 0 or y + j >= 8:
                    continue

                if self.board[y + j][x + i] != self.color[other]:
                    continue

                for s in range(2, 8):
                    if x + i * s >= 0 and x + i * s < 8 and y + j * s >= 0 and y + j * s < 8:
                        if self.board[y + j * s][x + i * s] is None:
                            break

                        if self.board[y + j * s][x + i * s] == self.color[turn_player]:

                            for n in range(1, s):
                                self.board[y + j * n][x + i *
                                                      n] = self.color[turn_player]
                                tag_name = 'disk_' + \
                                    str(x + i * n) + '_' + str(y + j * n)
                                self.canvas.itemconfig(
                                    tag_name,
                                    fill=self.color[turn_player]
                                )

                            break

    def change_turn_player(self):

        turn_player = self.turn_player

        next_turn_player = self.cpu_name if turn_player == self.user_name else self.user_name

        self.turn_player = next_turn_player
        if len(self.get_legal_places()) == 0:
            self.turn_player = turn_player

            if len(self.get_legal_places()) == 0:
                self.turn_player = None

    def board2ai_state_legal_places(self):
        black_state = []
        white_state = []

        for y in range(8):
            row = []
            for x in range(8):
                if self.board[y][x] == self.user_color:
                    row.append(1.0)
                else:
                    row.append(0.0)
            black_state.append(row)

        for y in range(8):
            row = []
            for x in range(8):
                if self.board[y][x] == self.cpu_color:
                    row.append(1.0)
                else:
                    row.append(0.0)
            white_state.append(row)

        state = torch.tensor([[black_state, white_state]]).to(device)

        legal_moves = [8 * x + y for x, y in self.get_legal_places()]

        return state, legal_moves

    def get_ai_select(self, model_file):
        player = DQN_Player(model_file)
        state, legal_places = self.board2ai_state_legal_places()

        select = player.select_place(state, legal_places)

        x = select//8
        y = select % 8
        return x, y

    def get_assisted_ai_select(self, model_file):
        x, y = self.get_ai_select(model_file)
        return x, y


def main():
    app = tkinter.Tk()
    app.title('Reversi')
    ReversiGame = Reversi(app, config_file_path, 'models/dqn_model_2.pt')
    app.mainloop()


if __name__ == '__main__':
    main()
