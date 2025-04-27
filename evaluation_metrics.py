from dataclasses import dataclass, asdict
import csv
from pathlib import Path
import chess

@dataclass
class PlyMetrics:
    ply: int                 # ½-move number
    our_move: str            # engine move in UCI
    sf_move: str             # Stockfish best move in UCI
    same_move: bool          # did we match Stockfish?
    centipawn_loss: int      # CPL (our - best)
    step_smartness: int  # Δ-eval for *our* colour
    decision_time: float  # seconds spent thinking
    pruned_branches: int  # α-β cut-offs in our search

class GameMetrics:
    def __init__(self):
        self.data: list[PlyMetrics] = []
        self.result_value: float | None = None  # 1 / 0.5 / 0

    #per-ply bookkeeping
    def record_ply(self,
                   board_before: chess.Board,
                   our_move: chess.Move,
                   step_smartness: float,
                   decision_time: float,
                   pruned_branches: int,):
        from stockfish_integration import stockfish_move, get_stockfish_eval_metric

        ply_no = board_before.fullmove_number * 2 - (0 if board_before.turn else 1)

        # Stockfish’s choice & evaluation
        sf_move_obj = stockfish_move(board_before)
        sf_move_uci = sf_move_obj.uci()
        sf_board = board_before.copy()
        sf_board.push(sf_move_obj)
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
            centipawn_loss=cpl,
            step_smartness=step_smartness,
            decision_time=decision_time,
            pruned_branches=pruned_branches,
        ))

    # summary at game end
    def summary_dict(self):
        total = len(self.data) or 1
        return {
            "plys": total,
            "match_rate": sum(d.same_move for d in self.data) / total,
            "avg_cpl": sum(d.centipawn_loss for d in self.data) / total,
            "avg_step_smartness": sum(d.step_smartness for d in self.data) / total,
            "step_improvement_ratio": sum(d.step_smartness > 0 for d in self.data) / total,
            "avg_decision_time": sum(d.decision_time for d in self.data) / total,
            "total_pruned": sum(d.pruned_branches for d in self.data),
            "win_loss_ratio": self.result_value,  # 1 / 0.5 / 0
        }

    # optional CSV
    def to_csv(self, out_file: str | Path):
        out = Path(out_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=PlyMetrics.__annotations__.keys())
            writer.writeheader()
            for row in self.data:
                writer.writerow(asdict(row))