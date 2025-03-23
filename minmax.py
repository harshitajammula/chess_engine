import multiprocessing

import chess
import math


def evaluate_board(board):
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 320,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 10000  # King is invaluable
    }

    piece_square_tables = {
        chess.PAWN: [
            0, 5, 5, 0, 5, 10, 50, 0,
            0, 10, -5, 0, 5, 10, 50, 0,
            0, 10, -10, 20, 30, 40, 50, 0,
            0, 10, -10, 25, 35, 45, 50, 0,
            0, 10, -10, 25, 35, 45, 50, 0,
            0, 10, -10, 20, 30, 40, 50, 0,
            0, 10, -5, 0, 5, 10, 50, 0,
            0, 5, 5, 0, 5, 10, 50, 0
        ],
        chess.KNIGHT: [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ]
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            position_bonus = piece_square_tables.get(piece.piece_type, [0] * 64)[square]
            if piece.color == chess.WHITE:
                score += value + position_bonus
            else:
                score -= value + position_bonus

    # Mobility Score
    score += len(list(board.legal_moves)) * 0.1

    # Penalize Repetition
    if board.is_repetition(2):
        score -= 10

    return score


def minimax(board, depth, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    if maximizing_player:
        max_eval = -math.inf
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            return max_eval, best_move
    else:
        min_eval = math.inf
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            return min_eval, best_move


# def find_best_move(board, depth):
#     best_move = None
#     max_eval = -math.inf
#     for move in board.legal_moves:
#         board.push(move)
#         eval = minimax(board, depth - 1, False)
#         board.pop()
#         if eval > max_eval:
#             max_eval = eval
#             best_move = move
#     return best_move, max_eval



def minimax_alpha_beta(board, depth, maximizing_player, alpha, beta):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    if maximizing_player:
        max_eval = -math.inf
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax_alpha_beta(board, depth - 1, False, alpha, beta)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax_alpha_beta(board, depth - 1, True, alpha, beta)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move


def alpha_beta_worker(board_fen, move, depth):
    board = chess.Board(board_fen)  # Create a new board from FEN to avoid shared state
    board.push(move)
    score, _ = minimax_alpha_beta(board, depth - 1, False, -math.inf, math.inf)
    return move, score


def vanilla_worker(board_fen, move, depth):
    board = chess.Board(board_fen)  # Create a new board from FEN to avoid shared state
    board.push(move)
    score, _ = minimax(board, depth - 1, False)
    return move, score


def find_best_move_parallel(board, depth):
    legal_moves = list(board.legal_moves)
    num_workers = min(len(legal_moves), multiprocessing.cpu_count())  # Use available CPU cores

    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.starmap(
            alpha_beta_worker, [(board.fen(), move, depth) for move in legal_moves]
        )

    best_move_score = max(results, key=lambda x: x[1])  # Pick the move with the highest score
    return best_move_score[0], best_move_score[1]