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
        info = self.engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=multipv)
        top_moves = []
        for item in info:
            try:
                pv = item.get("pv", [])
                if not pv or len(pv) == 0:
                    continue
                move = pv[0]
                # Attempt to parse the move SAN
                san_move = board.san(move)
            except Exception as e:
                print(f"exception parsing pv from info: {item.get('pv')}, position at root: {board.fen()}")
                continue  # Skip this candidate if there's an error

            score_obj = item.get("score")
            if score_obj.is_mate():
                score = float("inf") if score_obj.mate() > 0 else float("-inf")
            else:
                score = score_obj.white().score() / 100.0  # Convert centipawns to pawns
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

    # stockfish_interface.py (updated build_threat_tree)

    def build_threat_tree(self, board: chess.Board, ply_depth: int, player_color: bool) -> Dict[str, Any]:
        """
        Build a threat tree representing the opponent's top moves and evaluations if YOU skipped your move.
        In the current position (it’s your move), simulate skipping your move by creating a copy of the board,
        forcing the turn to be that of the opponent (i.e. not player_color), and manually updating the FEN.
        Then, retrieve the opponent's top moves at depth 1. The temporary board copy is discarded afterward.
        """
        if ply_depth == 0 or board.is_game_over():
            return {}
        # Create a copy of the board.
        threat_board = board.copy()
        # Force the turn to be the opponent.
        threat_board.turn = not player_color
        # Manually update the FEN to reflect the forced turn.
        fen_parts = threat_board.fen().split()
        # If player's color is True (White), then opponent is Black ("b"); if player's color is False (Black), then opponent is White ("w").
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
    board = chess.Board()  # Starting position.
    eval_tree = analyzer.build_eval_tree(board, ply_depth=2)
    # Assume player's color is White (True).
    threat_tree = analyzer.build_threat_tree(board, ply_depth=1, player_color=True)
    print("Evaluation tree (depth=2):", eval_tree)
    print("Threat tree (depth=1):", threat_tree)
    analyzer.close()
