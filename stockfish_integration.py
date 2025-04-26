from stockfish import Stockfish
import chess

STOCKFISH_PATH = r"C:\Users\ambre\OneDrive\Desktop\chess_engine-master\stockfish\stockfish-windows-x86-64-avx2.exe"

stockfish = Stockfish(path=STOCKFISH_PATH)
stockfish.set_depth(12)

def stockfish_move(board: chess.Board) -> chess.Move:
    fen = board.fen()
    stockfish.set_fen_position(fen)

    move_uci = stockfish.get_best_move()

    if move_uci == "f8d8":
        print(f"[DEBUG] Stockfish suggested f8d8 move. Legal moves: {[m.uci() for m in board.legal_moves]}")
        print(f"[DEBUG] Board state: {board.fen()}")
        print(f"[DEBUG] Piece at f8: {board.piece_at(chess.F8)}")
        print(f"[DEBUG] Piece at d8: {board.piece_at(chess.D8)}")

    move = chess.Move.from_uci(move_uci)

    if move not in board.legal_moves:
        print(f"[WARNING] Stockfish suggested illegal move: {move_uci}")
        stockfish.set_depth(15)
        alternative_moves = stockfish.get_top_moves(5)

        for alt_move_uci in alternative_moves:
            alt_move = chess.Move.from_uci(alt_move_uci)
            if alt_move in board.legal_moves:
                board_copy = board.copy()
                board_copy.push(alt_move)
                if board_copy.king(chess.WHITE) is not None and board_copy.king(chess.BLACK) is not None:
                    print(f"[INFO] Using alternative Stockfish move: {alt_move_uci}")
                    return alt_move

        legal_moves = list(board.legal_moves)
        for move in legal_moves:
            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.king(chess.WHITE) is not None and board_copy.king(chess.BLACK) is not None:
                print(f"[INFO] Using fallback move: {move.uci()}")
                return move

        print("[ERROR] No safe moves available")
        return None

    board_copy = board.copy()
    board_copy.push(move)
    if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
        print(f"[WARNING] Original move {move_uci} would result in king capture")
        return stockfish_move(board)

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