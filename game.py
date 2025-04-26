import logging
import time
import chess
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime
import traceback
#you will see me using a lot of debug stuff, will change before we turn the project in
# Import functions from stockfish_integration and minmax
from stockfish_integration import (
    close_connection,
    stockfish_move,
    get_stockfish_eval_metric,
    validate_and_check_end
)
from minmax import find_best_move

# Create a directory for results if you do not have one
if not os.path.exists('results'):
    os.makedirs('results')

# Safely applies a move to the chess board after checking legality and basic chess rules - note some chess rules still need work
def safe_push(board: chess.Board, move: chess.Move) -> bool:
    # debug print out for legal moves 
    if move.uci() == "f8d8":
        print(f"[DEBUG] Attempting f8d8 move. Legal moves: {[m.uci() for m in board.legal_moves]}")
        print(f"[DEBUG] Board state: {board.fen()}")
        print(f"[DEBUG] Piece at f8: {board.piece_at(chess.F8)}")
        print(f"[DEBUG] Piece at d8: {board.piece_at(chess.D8)}")

    # Check if the move is legal - still needs work
    if move not in board.legal_moves:
        print(f"[ERROR] Illegal move attempt: {move.uci()}")
        return False

    # Check if there is a piece at the source square 
    source_piece = board.piece_at(move.from_square)
    if source_piece is None:
        print(f"[ERROR] No piece at source square: {move.uci()}")
        return False

    # Check if the piece belongs to the current player
    if source_piece.color != board.turn:
        print(f"[ERROR] Wrong piece color: {move.uci()}")
        return False

    # Get coordinates for movement analysis
    from_file = chess.square_file(move.from_square)
    from_rank = chess.square_rank(move.from_square)
    to_file = chess.square_file(move.to_square)
    to_rank = chess.square_rank(move.to_square)
    file_distance = abs(from_file - to_file)
    rank_distance = abs(from_rank - to_rank)
    piece_type = source_piece.piece_type

    # Validate movement rules for each piece type
    if piece_type == chess.PAWN:
        # Pawns cannot move more than 1 square horizontally, or 2 squares forward (only from starting position)
        if file_distance > 1 or (rank_distance > 2 or (rank_distance == 2 and not ((from_rank == 1 and board.turn) or (from_rank == 6 and not board.turn)))):
            return False
    elif piece_type == chess.KNIGHT:
        # Knights must move in an L-shape
        if not ((file_distance == 2 and rank_distance == 1) or (file_distance == 1 and rank_distance == 2)):
            return False
    elif piece_type == chess.KING:
        # King can only move 1 square, except for castling
        if move.from_square == chess.E1 and move.to_square in [chess.C1, chess.G1]:
            pass  # Allow white castling
        elif move.from_square == chess.E8 and move.to_square in [chess.C8, chess.G8]:
            pass  # Allow black castling
        elif file_distance > 1 or rank_distance > 1:
            return False

    # Prevent capturing a king directly (should end via checkmate)
    target = board.piece_at(move.to_square)
    if target and target.piece_type == chess.KING:
        return False

    # Backup board state in case of an illegal move after push
    prev_state = board.fen()
    board.push(move)

    # If after move, either king is missing, undo move
    if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
        board.set_fen(prev_state)
        return False

    return True

# Function to check if both kings still exist on the board
def check_kings(board):
    if board.king(chess.WHITE) is None:
        print("\n=== Game Over ===")
        print("Result: 0-1 (Black wins - White king captured)")
        return False
    if board.king(chess.BLACK) is None:
        print("\n=== Game Over ===")
        print("Result: 1-0 (White wins - Black king captured)")
        return False
    return True

# Main function to play a full game between Minimax (white) and Stockfish (black)
def play_game(depth=2):
    print(f"\n=== Starting Game (White: Minimax-depth={depth} vs Black: Stockfish) ===")
    board = chess.Board()  # Initialize new board
    move_counter = 0  # Track number of moves

    while not board.is_game_over():
        # Ensure both kings are alive
        if not check_kings(board):
            break

        move_counter += 1
        print(f"\nMove #{move_counter}")
        print(board.unicode(borders=True))  # Print board in readable format

        if board.turn:  # White's turn (Minimax)
            eval = get_stockfish_eval_metric(board)  # Get position evaluation
            print(f"Position evaluation: {eval:+.2f} centipawns")
            start_time = time.time()
            move, score = find_best_move(board, depth)  # Find best move using minimax
            end_time = time.time()
            print(f"White (Minimax) plays: {move.uci()} (score: {score:+.2f}) in {end_time - start_time:.2f} seconds")
            if not safe_push(board, move):
                continue  # Skip turn if illegal move
        else:  # Black's turn (Stockfish)
            start_time = time.time()
            move = stockfish_move(board)  # Get move from Stockfish
            end_time = time.time()
            print(f"Black (Stockfish) plays: {move.uci()} in {end_time - start_time:.2f} seconds")
            if not safe_push(board, move):
                continue  # Skip turn if illegal move

    # After the game ends, report the result
    if board.is_game_over():
        print("\n=== Game Over ===")
        print(f"Result: {board.outcome().result()}")
        result = board.outcome().result()
        if result == "1-0":
            print("White (Minimax) wins!")
        elif result == "0-1":
            print("Black (Stockfish) wins!")
        else:
            print("Game drawn!")
    print(f"Total moves: {move_counter}")

# Entry point of the script
def main():
    print("Chess Engine Test: Minimax (White) vs Stockfish (Black)")
    print("=====================================")
    depth = 2  # Set search depth for minimax - still needs work
    print(f"\nRunning test game at depth {depth}...")
    play_game(depth)
    close_connection()  # Close Stockfish connection 

# Run the main function if this script is executed directly
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Catch any fatal error, print it, this is only really used for debug.
        print(f"Fatal error: {e}")
    finally:
        # Always ensure connection is closed
        close_connection()
