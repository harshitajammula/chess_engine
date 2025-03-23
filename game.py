import random
import matplotlib.pyplot as plt

from chess import Move
import chess.engine
from stockfish_integration import close_connection, stockfish_move, get_stockfish_eval_metric
from minmax import find_best_move_parallel
board = chess.Board()
import logging


def get_user_move():
    # move = input("enter move in UCI format. eg a2a4")
    # user_move = Move.from_uci(move)
    user_move = random.choice(list(board.legal_moves))
    if user_move in board.legal_moves:
        return user_move
    else:
        print("invalid move. try again")
    return get_user_move()


# print("Welcome to the chess game!")
# user_color_choice = input("Who would you like to play. W/B")
# if user_color_choice == "W":
#     user_turn = chess.WHITE
# else:
#     user_turn = chess.BLACK
#
# while not board.outcome():
#     if board.turn == user_turn:
#         user_move = get_user_move()
#         board.push(user_move)
#         print(f"User move is {user_move.uci()}")
#     print(board.unicode(borders=True))
#     if board.turn != user_turn:
#         move = get_stockfish_move(board)
#         board.push(move)
#         print(f"Stockfish move is {move.uci()}")
#     print(board.unicode(borders=True))

# outcome: chess.Outcome = board.outcome()
# print(outcome.result())
def save_graph(depth, step_metrics):
    plt.plot(step_metrics, color="blue", label="Step_score_factor")
    plt.xlabel("Steps")
    plt.ylabel("Smart_score")
    plt.legend()
    plt.title(f"step_smartness_{depth}_depth")
    plt.savefig(f"results/step_smartness_{depth}_depth_ab.png", dpi=300, bbox_inches='tight')  # Saves as a high-quality PNG
    plt.close()


def play_game(depth):
    logging.basicConfig(
        filename=f"results/{depth}_ab.log",  # Log file name
        level=logging.INFO,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"  # Ensure Unicode support
    )
    board = chess.Board()
    minmax_score = 0
    model_move_scores = []
    while not board.is_game_over():
        logging.info("----------------------------------------------------")
        if board.turn == chess.WHITE:
            logging.info("Player White\n")
            smart_move_score_before = get_stockfish_eval_metric(board)
            move, move_score = find_best_move_parallel(board, depth)
            board.push(move)
            minmax_score += move_score
            smart_move_score_after = get_stockfish_eval_metric(board)
            model_move_scores.append(smart_move_score_after - smart_move_score_before)
        else:
            logging.info("Player Black\n")
            stockfish_model_move = stockfish_move(board)
            board.push(chess.Move.from_uci(stockfish_model_move))
        logging.info(board.unicode(borders=True))

    logging.info("Game over!")
    logging.info(f"Result: {board.outcome().result()}")
    logging.info(f"Total steps played: {len(model_move_scores)}")
    save_graph(depth, model_move_scores)

if __name__ == '__main__':
    for depth in range(1, 6):
        play_game(depth)
    close_connection()