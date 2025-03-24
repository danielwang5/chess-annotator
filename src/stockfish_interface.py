# stockfish_interface.py
import chess
import chess.engine
from typing import List, Dict, Any
from src.config import STOCKFISH_PATH, ENGINE_TIME_LIMIT, ENGINE_DEPTH, ENGINE_MULTIPV

class StockfishAnalyzer:
    def __init__(self, engine_path: str = STOCKFISH_PATH):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def close(self):
        self.engine.quit()

    def get_top_moves(self, board: chess.Board, multipv: int = ENGINE_MULTIPV, time_limit: float = ENGINE_TIME_LIMIT) -> List[Dict[str, Any]]:
        """
        Analyze the given board and return the top moves with evaluations.
        Returns a list of dictionaries with keys: move (chess.Move), san (string), score (float).
        """
        info = self.engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=multipv)
        top_moves = []
        for item in info:
            # Get the first move from the principal variation
            move = item.get("pv")[0] if "pv" in item and len(item["pv"]) > 0 else None
            score_obj = item.get("score")
            if score_obj.is_mate():
                score = float("inf") if score_obj.mate() > 0 else float("-inf")
            else:
                score = score_obj.white().score() / 100.0  # Convert centipawns to pawns
            if move:
                top_moves.append({
                    "move": move,
                    "san": board.san(move),
                    "score": score
                })
        return top_moves

    def build_eval_tree(self, board: chess.Board, ply_depth: int) -> Dict[str, Any]:
        """
        Recursively builds an evaluation tree for the given board.
        For each position, it records the top moves (with evaluation scores) and recurses
        until the specified ply_depth is reached.
        Returns a dictionary representing the tree.
        """
        if ply_depth == 0 or board.is_game_over():
            return {}

        top_moves = self.get_top_moves(board)
        tree = {}
        for move_info in top_moves:
            move = move_info["move"]
            board_copy = board.copy()
            board_copy.push(move)
            subtree = self.build_eval_tree(board_copy, ply_depth - 1)
            tree[board.san(move)] = {
                "move": move.uci(),
                "score": move_info["score"],
                "subtree": subtree
            }
        return tree

# For testing:
if __name__ == "__main__":
    analyzer = StockfishAnalyzer()
    board = chess.Board()
    top_moves = analyzer.get_top_moves(board)
    print("Top moves:", top_moves)
    eval_tree = analyzer.build_eval_tree(board, ply_depth=2)
    print("Evaluation tree (depth=2):", eval_tree)
    analyzer.close()
