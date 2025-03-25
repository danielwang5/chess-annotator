# annotation_generator.py
from src.pgn_parser import PGNTreeNode, parse_pgn_to_tree
from src.stockfish_interface import StockfishAnalyzer
from src.prompt_engineering import create_annotation_prompt
from src.chatgpt_interface import get_annotation_with_timeout
from tqdm import tqdm

def annotate_main_line(root: PGNTreeNode, analyzer: StockfishAnalyzer, ply_depth: int):
    nodes = []
    current = root
    while current:
        nodes.append(current)
        if current.children:
            current = current.children[0]
        else:
            break

    player_color = root.player_color

    for node in tqdm(nodes, desc="Annotating moves"):
        fen = node.board.fen()
        eval_tree = analyzer.build_eval_tree(node.board, ply_depth)
        threat_tree = analyzer.build_threat_tree(node.board, 1, player_color)
        current_eval = analyzer.get_current_eval(node.board)
        if node.move is None:
            last_move_details = None
        else:
            last_move_details = {
                "move_san": node.move_san,
                "from": node.from_square,
                "to": node.to_square,
                "piece_type": node.piece_type,
            }
        prompt = create_annotation_prompt(fen, current_eval, eval_tree, threat_tree, last_move_details)
        annotation = get_annotation_with_timeout(prompt, timeout=60)
        node.annotation = annotation

def generate_annotations_for_game(pgn_file: str, ply_depth: int) -> PGNTreeNode:
    root = parse_pgn_to_tree(pgn_file)
    analyzer = StockfishAnalyzer()
    annotate_main_line(root, analyzer, ply_depth)
    analyzer.close()
    return root

# For testing:
if __name__ == "__main__":
    tree = generate_annotations_for_game("data/raw/mini.pgn", ply_depth=3)
    print("Root annotation:")
    print(tree.annotation)
    if tree.children:
        print("First move annotation:")
        print(tree.children[0].annotation)
