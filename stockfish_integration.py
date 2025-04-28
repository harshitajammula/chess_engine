import os
from stockfish import Stockfish
import chess

STOCKFISH_PATH = os.getenv("STOCKFISH_INSTALLATION_PATH") # set your path to the stockfish.exe under Environment Variables in both System and User with the name provided in this string
# Initialize the Stockfish engine
stockfish = Stockfish(path=STOCKFISH_PATH)
stockfish.set_depth(2)
# Generate a move for Stockfish based on the current board position
def stockfish_move(board: chess.Board) -> chess.Move | None:
    if board.is_game_over():
        return None
 # Set Stockfish's internal board to match the current board
    fen = board.fen()
    stockfish.set_fen_position(fen)

    move_uci = stockfish.get_best_move()
    if move_uci is None:
        return None

    move = chess.Move.from_uci(move_uci)
 # Special debugging for a suspicious move (f8d8) - I only used this to test an illegal move. but actually it was the minmax algoritm. - No longer needed
    if move not in board.legal_moves:
        print(f"[WARNING] Stockfish suggested illegal move {move_uci}, trying alternatives...")
        stockfish.set_depth(15)
        alternatives = stockfish.get_top_moves(5)
        for alt in alternatives:
            alt_move = chess.Move.from_uci(alt['Move'])
            if alt_move in board.legal_moves:
                print(f"[INFO] Using alternative move {alt['Move']}")
                return alt_move
        print("[ERROR] No legal moves available for Stockfish.")
        return None

    return move

def get_stockfish_eval_metric(board: chess.Board) -> float:
    stockfish.set_fen_position(board.fen())
    ev = stockfish.get_evaluation()
    if ev['type'] == 'cp':
        return ev['value']
    return 10000.0 if ev['value'] > 0 else -10000.0
# Properly close Stockfish connection
def close_connection():
    try:
        stockfish.__del__()
    except:
        pass

def validate_and_check_end(board: chess.Board) -> bool:
    if board.is_game_over():
        outcome = board.outcome()
        print(f"[GAME END] {outcome.result()} ({outcome.termination.name})")
        return False
    return True