import creversi


def main():
    board = creversi.Board()
    move = creversi.move_from_str('d3')
    board.move(move)
    print(board)


if __name__ == '__main__':
    main()
