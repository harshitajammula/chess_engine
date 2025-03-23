from stockfish import Stockfish
import os
stockfish_installation_path = os.getenv("STOCKFISH_INSTALLATION_PATH")
stockfish_engine = Stockfish(path=stockfish_installation_path)


def stockfish_move(board):
    stockfish_engine.set_fen_position(board.fen())
    move = stockfish_engine.get_best_move()
    return move


def get_stockfish_eval_metric(board):
    stockfish_engine.set_fen_position(board.fen())
    eval_metric = stockfish_engine.get_evaluation()["value"]
    return eval_metric