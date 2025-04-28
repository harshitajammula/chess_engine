import time
import chess
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from pathlib import Path
from stockfish_integration import (
    close_connection,
    stockfish_move,
    get_stockfish_eval_metric,
)
from minmax import find_best_move
from evaluation_metrics import GameMetrics

# Safe Move Push
def safe_push(board: chess.Board, move: chess.Move) -> bool:
    if move in board.legal_moves:
        board.push(move)
        if board.king(chess.WHITE) is None or board.king(chess.BLACK) is None:
            print("[CRITICAL] King disappeared after move. Undoing move.")
            board.pop()
            return False
        return True
    return False

# Check if Kings Are Alive 
def check_kings(board: chess.Board) -> bool:
    if board.king(chess.WHITE) is None:
        print("\n=== Game Over: White King Missing ===")
        print("Result: 0-1 (Black wins)")
        return False
    if board.king(chess.BLACK) is None:
        print("\n=== Game Over: Black King Missing ===")
        print("Result: 1-0 (White wins)")
        return False
    return True

# Correct Board Display 
def print_board(board):
    print(board.unicode(borders=True, invert_color=True))

# Describe a Move Nicely 
def describe_move(board_before, move):
    piece = board_before.piece_at(move.from_square)
    if not piece:
        return "Unknown piece moved."

    piece_name = piece.symbol().upper() if piece.color == chess.WHITE else piece.symbol().lower()
    names = {
        'P': 'Pawn', 'N': 'Knight', 'B': 'Bishop', 'R': 'Rook', 'Q': 'Queen', 'K': 'King',
        'p': 'Pawn', 'n': 'Knight', 'b': 'Bishop', 'r': 'Rook', 'q': 'Queen', 'k': 'King'
    }
    player = "White" if piece.color == chess.WHITE else "Black"
    return f"{player} {names[piece_name]} moves from {chess.square_name(move.from_square)} to {chess.square_name(move.to_square)}"

# Setup Logger 
def setup_logger():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = Path("results") / f"game_log_{ts}.txt"
    log_path.parent.mkdir(exist_ok=True)
    log_file = open(log_path, "w", encoding="utf-8")
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()
    sys.stdout = Tee(sys.stdout, log_file)
    return log_path

# Plotting Metrics (Save quietly )
def plot_game_metrics(csv_file: str):
    df = pd.read_csv(csv_file)

    moves = df["ply"]
    cpl = df["centipawn_loss"]
    smartness = df["step_smartness"]

    plt.figure(figsize=(10, 5))

    plt.plot(moves, cpl, label="Centipawn Loss (CPL)", marker='o')
    plt.plot(moves, smartness, label="Step Smartness", marker='x')

    plt.xlabel("Ply Number (Half-moves)")
    plt.ylabel("Evaluation (Centipawns)")
    plt.title("Game Evaluation Metrics Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_graph = csv_file.replace(".csv", "_graph.png")
    plt.savefig(output_graph)
    # plt.show() not needed  

    print(f"\n=== Metric Graph saved at: {output_graph} ===")

#  Main Game Loop 
def play_game(depth=2):
    metrics = GameMetrics()
    print(f"\n=== Starting Game (White: Minimax-depth={depth} vs Black: Stockfish) ===")
    board = chess.Board()
    move_counter = 0
    max_moves = 500
    move_timeout = 30

    while not board.is_game_over() and move_counter < max_moves:
        print(f"\nMove #{move_counter}")
        print_board(board)
        board_before = board.copy()

        if board.turn:  # White's turn (Minimax)
            eval_before = get_stockfish_eval_metric(board)
            try:
                start = time.time()
                move, score, pruned = find_best_move(board, depth)
                elapsed = time.time() - start

                if elapsed > move_timeout:
                    print(f"Move timeout exceeded ({move_timeout}s). Game ending.")
                    break

                if move is None or not safe_push(board, move):
                    print("White could not make a legal move. Game ending.")
                    break

                if not check_kings(board):
                    break

                eval_after = get_stockfish_eval_metric(board)
                step_smart = eval_after - eval_before

                print(describe_move(board_before, move))
                print(f"White (Minimax) played {move.uci()} (score: {score:+.2f}) in {elapsed:.2f}s")

                metrics.record_ply(
                    board_before,
                    move,
                    step_smartness=step_smart,
                    decision_time=elapsed,
                    pruned_branches=pruned,
                )
            except Exception as e:
                print(f"[ERROR] during White's move: {e}")
                break

        else:  # Black's turn (Stockfish)
            try:
                start = time.time()
                move = stockfish_move(board)
                elapsed = time.time() - start

                if elapsed > move_timeout:
                    print(f"Move timeout exceeded ({move_timeout}s). Game ending.")
                    break

                if move is None or not safe_push(board, move):
                    print("Black could not make a legal move. Game ending.")
                    break

                if not check_kings(board):
                    break

                print(describe_move(board_before, move))
                print(f"Black (Stockfish) played {move.uci()} in {elapsed:.2f}s")
            except Exception as e:
                print(f"[ERROR] during Black's move: {e}")
                break

        move_counter += 1

        if board.is_game_over():
            break

    # Game End
    if board.is_game_over():
        outcome = board.outcome()

        if outcome.termination == chess.Termination.CHECKMATE:
            loser_color = not outcome.winner
            king_square = board.king(loser_color)
            if king_square is not None:
                board.remove_piece_at(king_square)
            winner = "White" if outcome.winner else "Black"
            print(f"\n=== Game Over by Checkmate! Winner: {winner} ===")

        elif outcome.termination == chess.Termination.STALEMATE:
            print("\n=== Game Over by Stalemate! Result: Draw ===")

        elif outcome.termination == chess.Termination.INSUFFICIENT_MATERIAL:
            print("\n=== Game Over by Insufficient Material! Result: Draw ===")

        elif outcome.termination == chess.Termination.SEVENTYFIVE_MOVES:
            print("\n=== Game Over by 75-Move Rule! Result: Draw ===")

        elif outcome.termination == chess.Termination.FIVEFOLD_REPETITION:
            print("\n=== Game Over by Fivefold Repetition! Result: Draw ===")

        else:
            print(f"\n=== Game Over: {outcome.result()} ({outcome.termination.name}) ===")
    else:
        # Game ended unnaturally
        eval_now = get_stockfish_eval_metric(board)
        if eval_now > 0:
            print("\n=== Game Ended Early. White is winning based on evaluation! ===")
        elif eval_now < 0:
            print("\n=== Game Ended Early. Black is winning based on evaluation! ===")
        else:
            print("\n=== Game Ended Early. Game is approximately even. ===")

    print("\n=== Final Board State ===")
    print_board(board)

    # Save Metrics and Plot 
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"results/game_{ts}.csv"
    metrics.to_csv(csv_path)
    plot_game_metrics(csv_path)

    print("\n=== METRIC SUMMARY ===")
    for k, v in metrics.summary_dict().items():
        print(f"{k:>25}: {v}")

    close_connection()

# Main Entry Point
if __name__ == "__main__":
    log_path = setup_logger()
    play_game(depth=2)
    print(f"\n=== Game log saved at: {log_path}")

