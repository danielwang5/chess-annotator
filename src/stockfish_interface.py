# stockfish_interface.py (updated get_top_moves with engine restart)

import chess
import chess.engine
from typing import List, Dict, Any
from src.config import STOCKFISH_PATH, ENGINE_TIME_LIMIT, ENGINE_DEPTH, ENGINE_MULTIPV

class StockfishAnalyzer:
    def __init__(self, engine_path: str = STOCKFISH_PATH):
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def close(self):
        self.engine.quit()

    def _analyse_with_retry(self, board: chess.Board, time_limit: float, multipv: int) -> List[Dict[str, Any]]:
        try:
            return self.engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=multipv)
        except chess.engine.EngineTerminatedError as e:
            print("Engine terminated unexpectedly. Restarting engine and retrying analysis...")
            # Restart the engine
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            return self.engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=multipv)

    def get_top_moves(self, board: chess.Board, multipv: int = ENGINE_MULTIPV, time_limit: float = ENGINE_TIME_LIMIT) -> List[Dict[str, Any]]:
        info = self.engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=multipv)
        top_moves = []
        for item in info:
            try:
                pv = item.get("pv", [])
                if not pv:
                    continue
                move = pv[0]
                san_move = board.san(move)
            except Exception as e:
                print(f"exception parsing pv from info: {item.get('pv')}, position: {board.fen()}")
                continue

            score_obj = item.get("score")
            if score_obj is None:
                score = 0.0
            elif score_obj.is_mate():
                try:
                    mate_val = score_obj.mate()  # use the attribute, not a method
                    #print(f"MATEVAL: {mate_val}")
                    score = float("inf") if mate_val > 0 else float("-inf")
                except Exception as e:
                    score = 0.0
            else:
                try:
                    cp_value = score_obj.white().score()  # use the score() method
                    #print(f"CPVALUE: {cp_value}")
                    score = (cp_value / 100.0) if cp_value is not None else 0.0
                except Exception as e:
                    score = 0.0
            top_moves.append({
                "move": move,
                "san": san_move,
                "score": score
            })
        return top_moves


    def build_eval_tree(self, board: chess.Board, ply_depth: int) -> Dict[str, Any]:
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

    def build_threat_tree(self, board: chess.Board, ply_depth: int, player_color: bool) -> Dict[str, Any]:
        """
        Build a threat tree representing the opponent's top moves and evaluations if YOU skipped your move.
        Create a copy of the board, force the turn to be the opponent (not player_color) by updating the FEN,
        and then get the opponent's top moves at depth 1.
        """
        if ply_depth == 0 or board.is_game_over():
            return {}
        threat_board = board.copy()
        # Force turn to opponent regardless of current turn.
        threat_board.turn = not player_color
        fen_parts = threat_board.fen().split()
        fen_parts[1] = "b" if player_color else "w"
        new_fen = " ".join(fen_parts)
        threat_board.set_fen(new_fen)

        top_moves = self.get_top_moves(threat_board)
        if not top_moves:
            top_moves = self.get_top_moves(threat_board, time_limit=ENGINE_TIME_LIMIT * 2)
        tree = {}
        for move_info in top_moves:
            move = move_info["move"]
            try:
                san_str = threat_board.san(move)
            except Exception as e:
                print(f"exception parsing pv from info: {move_info}, position: {threat_board.fen()}")
                continue
            tree[san_str] = {
                "move": move.uci(),
                "score": move_info["score"],
                "subtree": {}
            }
        return tree

# For testing:
if __name__ == "__main__":
    analyzer = StockfishAnalyzer()
    board = chess.Board()  # Starting position
    eval_tree = analyzer.build_eval_tree(board, ply_depth=2)
    threat_tree = analyzer.build_threat_tree(board, ply_depth=1, player_color=True)
    print("Evaluation tree (depth=2):", eval_tree)
    print("Threat tree (depth=1):", threat_tree)
    analyzer.close()
