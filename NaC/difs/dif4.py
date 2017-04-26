import numpy as np
import operator


def check_win(board, player):
    np_board = np.array([0 if x == -player else x for x in board])
    np_board.resize(3, 3)
    return (
        all(np_board.diagonal()) or
        all(np.fliplr(np_board).diagonal()) or
        any(np_board.all(axis=0)) or
        any(np_board.all(axis=1))
    )


def minimax(board, next_move, ai_player):
    if not any(board):
        return np.random.randint(9)

    if check_win(board, ai_player):
        return None, np.inf
    elif check_win(board, -ai_player):
        return None, -np.inf
    elif 0 not in board:
        return None, 0

    moves = []
    for i in range(len(board)):
        if board[i] == 0:
            board[i] = next_move
            score = minimax(board, -next_move, ai_player)[1]
            moves.append((i, score))
            board[i] = 0

    if next_move == ai_player:
        return max(moves, key=operator.itemgetter(1))
    else:
        return min(moves, key=operator.itemgetter(1))

if __name__ == '__main__':
    a = [1, -1, -1,
         -1, 1, 0,
         1, 0, -1]
    print(minimax(a, 1, 1))
