import os
from stockfish import Stockfish
import chess

STOCKFISH_PATH = os.getenv("STOCKFISH_INSTALLATION_PATH")

stockfish = Stockfish(path=STOCKFISH_PATH)
stockfish.set_depth(12)

def stockfish_move(board: chess.Board) -> chess.Move | None:
    if board.is_game_over():
        return None

    fen = board.fen()
    stockfish.set_fen_position(fen)

    move_uci = stockfish.get_best_move()
    if move_uci is None:
        return None

    move = chess.Move.from_uci(move_uci)

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