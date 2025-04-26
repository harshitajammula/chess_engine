import chess
import random

def evaluate_board(board):
    if board.king(chess.WHITE) is None:
        return -10000
    if board.king(chess.BLACK) is None:
        return 10000

    if board.is_checkmate():
        return -10000 if board.turn else 10000

    random_factor = random.uniform(0.8, 1.2)

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = {
                chess.PAWN: 100,
                chess.KNIGHT: 320,
                chess.BISHOP: 330,
                chess.ROOK: 500,
                chess.QUEEN: 900,
                chess.KING: 20000
            }[piece.piece_type]
            score += value if piece.color else -value

    return score * random_factor

def minimax(board, depth, alpha, beta, maximizing_player):
    if board.king(chess.WHITE) is None:
        return -10000
    if board.king(chess.BLACK) is None:
        return 10000

    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float('-inf')
        moves = list(board.legal_moves)
        random.shuffle(moves)

        for move in moves:
            board_copy = board.copy()
            board_copy.push(move)

            if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
                continue

            eval = minimax(board_copy, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        moves = list(board.legal_moves)
        random.shuffle(moves)

        for move in moves:
            board_copy = board.copy()
            board_copy.push(move)

            if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
                continue

            eval = minimax(board_copy, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth):
    if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
        return None, 0

    best_move = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    moves = list(board.legal_moves)
    if not moves:
        return None, 0

    random.shuffle(moves)
    valid_moves = []
    valid_values = []

    for move in moves:
        if move not in board.legal_moves:
            continue

        board_copy = board.copy()
        board_copy.push(move)

        if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
            continue

        value = minimax(board_copy, depth - 1, alpha, beta, False)

        valid_moves.append(move)
        valid_values.append(value)

        if value > best_value:
            best_value = value
            best_move = move

    if best_move is None and valid_moves:
        best_move = valid_moves[0]
        best_value = valid_values[0]
    elif best_move is None and moves:
        best_move = moves[0]
        best_value = 0

    return best_move, best_value