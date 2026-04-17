import math
import random
from core.board import COLS, ROWS, is_valid_column, get_next_open_row, drop_piece, board_full
from core.rule_checker import check_winner

AI_PLAYER = 2
HUMAN_PLAYER = 1
EMPTY = 0

def get_valid_locations(board):
    return [col for col in range(COLS) if is_valid_column(board, col)]

def copy_board(board):
    return [row[:] for row in board]

def evaluate_window(window, piece):
    score = 0
    opp_piece = HUMAN_PLAYER if piece == AI_PLAYER else AI_PLAYER

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 4

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 8

    return score

def score_position(board, piece):
    score = 0

    # ưu tiên cột giữa
    center_col = COLS // 2
    center_array = [board[r][center_col] for r in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 6

    # ngang
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # dọc
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # chéo xuống phải
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # chéo lên phải
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return (
        check_winner(board, HUMAN_PLAYER) or
        check_winner(board, AI_PLAYER) or
        board_full(board)
    )

def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if check_winner(board, AI_PLAYER):
                return None, 1000000
            elif check_winner(board, HUMAN_PLAYER):
                return None, -1000000
            else:
                return None, 0
        else:
            return None, score_position(board, AI_PLAYER)

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = copy_board(board)
            drop_piece(temp_board, row, col, AI_PLAYER)

            _, new_score = minimax(temp_board, depth - 1, alpha, beta, False)

            if new_score > value:
                value = new_score
                best_col = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return best_col, value

    else:
        value = math.inf
        best_col = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = copy_board(board)
            drop_piece(temp_board, row, col, HUMAN_PLAYER)

            _, new_score = minimax(temp_board, depth - 1, alpha, beta, True)

            if new_score < value:
                value = new_score
                best_col = col

            beta = min(beta, value)
            if alpha >= beta:
                break

        return best_col, value

def get_ai_move(board, difficulty="easy"):
    if difficulty == "easy":
        depth = 2
    elif difficulty == "medium":
        depth = 4
    else:
        depth = 5

    col, _ = minimax(board, depth, -math.inf, math.inf, True)
    return col