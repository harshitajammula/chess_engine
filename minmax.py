import chess
import random
import math

# Global prune counter 
_PRUNE_COUNTER = 0

# Evaluation Function
def evaluate_board(board):
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 320,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 10000
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

    return score

# Move Ordering to Improve Alpha-Beta
def order_moves(board, moves):
    move_scores = []
    for move in moves:
        score = 0
        if board.is_capture(move):
            score += 1000
        move_scores.append((move, score))
    move_scores.sort(key=lambda x: x[1], reverse=True)
    return [move for move, _ in move_scores]

# Minimax with Alpha-Beta Pruning and Survival Check
def minimax(board, depth, alpha, beta, maximizing_player, stats):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float('-inf')
        moves = order_moves(board, list(board.legal_moves))

        for move in moves:
            board.push(move)

            # Check after move: kings must survive
            if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
                board.pop()
                continue

            eval = minimax(board, depth - 1, alpha, beta, False, stats)
            board.pop()

            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                stats["pruned"] += 1
                break

        return max_eval
    else:
        min_eval = float('inf')
        moves = order_moves(board, list(board.legal_moves))

        for move in moves:
            board.push(move)

            # Check after move: kings must survive
            if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
                board.pop()
                continue

            eval = minimax(board, depth - 1, alpha, beta, True, stats)
            board.pop()

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                stats["pruned"] += 1
                break

        return min_eval

# Best Move Finder with Randomness
def find_best_move(board: chess.Board, depth: int):
    if board.is_game_over():
        return None, 0, 0

    if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
        return None, 0, 0

    stats = {"pruned": 0}
    best_moves = []
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    moves = order_moves(board, list(board.legal_moves))
    if not moves:
        return None, 0, 0

    for move in moves:
        board.push(move)

        # Check after move: kings must survive
        if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
            board.pop()
            continue

        value = minimax(board, depth - 1, alpha, beta, False, stats)
        board.pop()

        if value > best_value:
            best_value = value
            best_moves = [move]
        elif value == best_value:
            best_moves.append(move)

    if not best_moves:
        return None, 0, stats["pruned"]

    # Pick randomly among all equally best moves
    best_move = random.choice(best_moves)

    return best_move, best_value, stats["pruned"]
