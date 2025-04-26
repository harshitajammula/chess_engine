import logging
import time
import chess
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime
import traceback

from stockfish_integration import (
    close_connection,
    stockfish_move,
    get_stockfish_eval_metric,
    validate_and_check_end
)
from minmax import find_best_move

if not os.path.exists('results'):
    os.makedirs('results')

def safe_push(board: chess.Board, move: chess.Move) -> bool:
    if move.uci() == "f8d8":
        print(f"[DEBUG] Attempting f8d8 move. Legal moves: {[m.uci() for m in board.legal_moves]}")
        print(f"[DEBUG] Board state: {board.fen()}")
        print(f"[DEBUG] Piece at f8: {board.piece_at(chess.F8)}")
        print(f"[DEBUG] Piece at d8: {board.piece_at(chess.D8)}")

    if move not in board.legal_moves:
        print(f"[ERROR] Illegal move attempt: {move.uci()}")
        return False

    source_piece = board.piece_at(move.from_square)
    if source_piece is None:
        print(f"[ERROR] No piece at source square: {move.uci()}")
        return False

    if source_piece.color != board.turn:
        print(f"[ERROR] Wrong piece color: {move.uci()}")
        return False

    from_file = chess.square_file(move.from_square)
    from_rank = chess.square_rank(move.from_square)
    to_file = chess.square_file(move.to_square)
    to_rank = chess.square_rank(move.to_square)

    file_distance = abs(from_file - to_file)
    rank_distance = abs(from_rank - to_rank)
    piece_type = source_piece.piece_type

    if piece_type == chess.PAWN:
        if file_distance > 1 or (rank_distance > 2 or (rank_distance == 2 and not ((from_rank == 1 and board.turn) or (from_rank == 6 and not board.turn)))):
            return False
    elif piece_type == chess.KNIGHT:
        if not ((file_distance == 2 and rank_distance == 1) or (file_distance == 1 and rank_distance == 2)):
            return False
    elif piece_type == chess.KING:
        if move.from_square == chess.E1 and move.to_square in [chess.C1, chess.G1]:
            pass
        elif move.from_square == chess.E8 and move.to_square in [chess.C8, chess.G8]:
            pass
        elif file_distance > 1 or rank_distance > 1:
            return False

    target = board.piece_at(move.to_square)
    if target and target.piece_type == chess.KING:
        return False

    prev_state = board.fen()
    board.push(move)

    if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
        board.set_fen(prev_state)
        return False

    return True

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

def play_game(depth=2):
    print(f"\n=== Starting Game (White: Minimax-depth={depth} vs Black: Stockfish) ===")
    board = chess.Board()
    move_counter = 0

    while not board.is_game_over():
        if not check_kings(board):
            break

        move_counter += 1
        print(f"\nMove #{move_counter}")
        print(board.unicode(borders=True))

        if board.turn:
            eval = get_stockfish_eval_metric(board)
            print(f"Position evaluation: {eval:+.2f} centipawns")
            start_time = time.time()
            move, score = find_best_move(board, depth)
            end_time = time.time()
            print(f"White (Minimax) plays: {move.uci()} (score: {score:+.2f}) in {end_time - start_time:.2f} seconds")
            if not safe_push(board, move):
                continue
        else:
            start_time = time.time()
            move = stockfish_move(board)
            end_time = time.time()
            print(f"Black (Stockfish) plays: {move.uci()} in {end_time - start_time:.2f} seconds")
            if not safe_push(board, move):
                continue

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

def main():
    print("Chess Engine Test: Minimax (White) vs Stockfish (Black)")
    print("=====================================")
    depth = 2
    print(f"\nRunning test game at depth {depth}...")
    play_game(depth)
    close_connection()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        close_connection()
