import chess
import random

# Evaluates the board position and returns a score
def evaluate_board(board):
    # If white king is missing, black wins- to evaluate for missing king on the board near end game.
    if board.king(chess.WHITE) is None:
        return -10000
    # If black king is missing, white wins - sometimes kings will go missing near end game
    if board.king(chess.BLACK) is None:
        return 10000

    # If the game is a checkmate, score accordingly based on whose turn it is - this part needs to be fixed
    if board.is_checkmate():
        return -10000 if board.turn else 10000

    # Add a slight random factor to evaluation to avoid repetitive games - might need to remove this or the random factor as a whole
    random_factor = random.uniform(0.8, 1.2)

    score = 0
    # Sum up the material value for all pieces on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = {
                chess.PAWN: 100,
                chess.KNIGHT: 320,
                chess.BISHOP: 330,
                chess.ROOK: 500,
                chess.QUEEN: 900,
                chess.KING: 20000  # High value for kings (although we rarely capture them)
            }[piece.piece_type]
            # Add or subtract piece value based on color
            score += value if piece.color else -value

    # Return final evaluation multiplied by random factor
    return score * random_factor

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    # Terminal condition: check if a king is missing
    if board.king(chess.WHITE) is None:
        return -10000
    if board.king(chess.BLACK) is None:
        return 10000

    # Terminal condition: depth 0 or game over
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    # If it's the maximizing player's turn (white)
    if maximizing_player:
        max_eval = float('-inf')
        moves = list(board.legal_moves)
        random.shuffle(moves)  # Add randomness to move order

        for move in moves:
            board_copy = board.copy()
            board_copy.push(move)

            # Skip moves that result in losing your king
            if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
                continue

            eval = minimax(board_copy, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            # Alpha-beta pruning: cutoff branch if no better move possible
            if beta <= alpha:
                break
        return max_eval
    else:  # Minimizing player's turn (black)
        min_eval = float('inf')
        moves = list(board.legal_moves)
        random.shuffle(moves)  # Randomize move order

        for move in moves:
            board_copy = board.copy()
            board_copy.push(move)

            # Skip moves that result in losing your king
            if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
                continue

            eval = minimax(board_copy, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            # Alpha-beta pruning: cutoff branch if no better move possible
            if beta <= alpha:
                break
        return min_eval

# Finds the best move using Minimax and evaluation
def find_best_move(board, depth):
    # If either king is missing, there is no best move
    if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
        return None, 0

    best_move = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    moves = list(board.legal_moves)
    if not moves:
        return None, 0  # No legal moves (checkmate or stalemate)

    random.shuffle(moves)  # Add randomness to move selection
    valid_moves = []
    valid_values = []

    # Evaluate each move
    for move in moves:
        if move not in board.legal_moves:
            continue

        board_copy = board.copy()
        board_copy.push(move)

        # Skip moves that would lose the king 
        if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
            continue

        value = minimax(board_copy, depth - 1, alpha, beta, False)

        valid_moves.append(move)
        valid_values.append(value)

        if value > best_value:
            best_value = value
            best_move = move

    # Fallback in case no best move was found
    if best_move is None and valid_moves:
        best_move = valid_moves[0]
        best_value = valid_values[0]
    elif best_move is None and moves:
        best_move = moves[0]
        best_value = 0

    return best_move, best_value
