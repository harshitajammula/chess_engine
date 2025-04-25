# evaluation_metrics.py
from dataclasses import dataclass, asdict
import csv
from pathlib import Path

@dataclass
class PlyMetrics:
    ply: int                 # ½-move number
    our_move: str            # engine move in UCI
    sf_move: str             # Stockfish best move in UCI
    same_move: bool          # did we match Stockfish?
    centipawn_loss: int      # CPL (our - best)

class GameMetrics:
    def __init__(self):
        self.data: list[PlyMetrics] = []

    # ---------- per-ply bookkeeping ----------
    def record_ply(self, board_before,  # chess.Board before *either* move
                   our_move):
        from stockfish_integration import stockfish_move, get_stockfish_eval_metric

        ply_no = board_before.fullmove_number * 2 - (0 if board_before.turn else 1)

        # Stockfish’s choice & evaluation
        sf_move_uci = stockfish_move(board_before)
        sf_board = board_before.copy()
        sf_board.push(chess.Move.from_uci(sf_move_uci))
        sf_eval_after = get_stockfish_eval_metric(sf_board)

        # Engine eval after its own move (board_before already has our_move pushed later)
        tmp = board_before.copy()
        tmp.push(our_move)
        our_eval_after = get_stockfish_eval_metric(tmp)

        cpl = abs(sf_eval_after - our_eval_after)       # centipawn loss
        self.data.append(PlyMetrics(
            ply=ply_no,
            our_move=our_move.uci(),
            sf_move=sf_move_uci,
            same_move=(our_move.uci() == sf_move_uci),
            centipawn_loss=cpl
        ))

    # ---------- summary at game end ----------
    def summary_dict(self):
        total = len(self.data)
        return {
            "plys": total,
            "match_rate": sum(d.same_move for d in self.data) / total if total else 0,
            "avg_cpl": sum(d.centipawn_loss for d in self.data) / total if total else 0
        }

    # ---------- optional CSV export ----------
    def to_csv(self, out_path: str | Path):
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=PlyMetrics.__annotations__.keys())
            writer.writeheader()
            for d in self.data:
                writer.writerow(asdict(d))
