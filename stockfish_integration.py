from stockfish import Stockfish
import chess

# Define the path to the Stockfish engine exe - replace my path with yours :O
STOCKFISH_PATH = r"C:\Users\ambre\OneDrive\Desktop\chess_engine-master\stockfish\stockfish-windows-x86-64-avx2.exe"

# Initialize the Stockfish engine
stockfish = Stockfish(path=STOCKFISH_PATH)
stockfish.set_depth(12)  # Set default search depth to 12

# Generate a move for Stockfish based on the current board position
def stockfish_move(board: chess.Board) -> chess.Move:
    # Set Stockfish's internal board to match the current board
    fen = board.fen()
    stockfish.set_fen_position(fen)

    # Ask Stockfish for the best move
    move_uci = stockfish.get_best_move()

    # Special debugging for a suspicious move (f8d8) - I only used this to test an illegal move. but actually it was the minmax algoritm.
    if move_uci == "f8d8":
        print(f"[DEBUG] Stockfish suggested f8d8 move. Legal moves: {[m.uci() for m in board.legal_moves]}")
        print(f"[DEBUG] Board state: {board.fen()}")
        print(f"[DEBUG] Piece at f8: {board.piece_at(chess.F8)}")
        print(f"[DEBUG] Piece at d8: {board.piece_at(chess.D8)}")

    # Convert move from UCI notation to a chess.Move object
    move = chess.Move.from_uci(move_uci)

    # If Stockfish suggested an illegal move (shouldn't happen, but we check)
    if move not in board.legal_moves:
        print(f"[WARNING] Stockfish suggested illegal move: {move_uci}")
        
        # Try deeper analysis to find a better move
        stockfish.set_depth(15)
        alternative_moves = stockfish.get_top_moves(5)  # Get top 5 alternative moves

        for alt_move_uci in alternative_moves:
            alt_move = chess.Move.from_uci(alt_move_uci)
            if alt_move in board.legal_moves:
                board_copy = board.copy()
                board_copy.push(alt_move)
                if board_copy.king(chess.WHITE) is not None and board_copy.king(chess.BLACK) is not None:
                    print(f"[INFO] Using alternative Stockfish move: {alt_move_uci}")
                    return alt_move

        # If no alternative Stockfish moves are safe, fallback to any legal move
        legal_moves = list(board.legal_moves)
        for move in legal_moves:
            board_copy = board.copy()
            board_copy.push(move)
            if board_copy.king(chess.WHITE) is not None and board_copy.king(chess.BLACK) is not None:
                print(f"[INFO] Using fallback move: {move.uci()}")
                return move

        # If no safe moves are found, something went wrong
        print("[ERROR] No safe moves available")
        return None

    # Verify if the original move leaves both kings alive
    board_copy = board.copy()
    board_copy.push(move)
    if board_copy.king(chess.WHITE) is None or board_copy.king(chess.BLACK) is None:
        print(f"[WARNING] Original move {move_uci} would result in king capture")
        return stockfish_move(board)  # Recursively try again

    # Return the valid move
    return move

# Get evaluation metric from Stockfish in centipawns or mate score - didnt know what this was until project lol
def get_stockfish_eval_metric(board: chess.Board) -> float:
    # Set Stockfish to current board position
    stockfish.set_fen_position(board.fen())
    ev = stockfish.get_evaluation()

    # If evaluation is in centipawns ('cp'), return the value
    if ev['type'] == 'cp':
        return ev['value']
    # If evaluation is in mate distance, treat it as a large value
    return 10000.0 if ev['value'] > 0 else -10000.0

# Properly close Stockfish connection
def close_connection():
    try:
        stockfish.__del__()  # Try to manually delete the Stockfish object
    except:
        pass  

# Validate board state and check if game has ended
def validate_and_check_end(board: chess.Board) -> bool:
    if board.is_game_over():
        # Report game result and reason
        outcome = board.outcome()
        print(f"[GAME END] {outcome.result()} ({outcome.termination.name})")
        return False
    return True