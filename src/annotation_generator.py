# annotation_generator.py
from src.pgn_parser import PGNTreeNode, parse_pgn_to_tree
from src.stockfish_interface import StockfishAnalyzer
from src.prompt_engineering import create_annotation_prompt
from src.chatgpt_interface import get_annotation_from_chatgpt
from tqdm import tqdm

def annotate_main_line(root: PGNTreeNode, analyzer: StockfishAnalyzer, ply_depth: int):
    """
    Annotate the main line (a linear chain of nodes) with ChatGPT annotations,
    displaying a progress bar.
    """
    # Collect all nodes along the main line.
    nodes = []
    current = root
    while current:
        nodes.append(current)
        if current.children:
            current = current.children[0]
        else:
            break
    
    # Annotate each node.
    for node in tqdm(nodes, desc="Annotating moves"):
        fen = node.board.fen()
        eval_tree = analyzer.build_eval_tree(node.board, ply_depth)
        if node.move is None:
            last_move_details = None
        else:
            last_move_details = {
                "move_san": node.move_san,
                "from": node.from_square,
                "to": node.to_square,
                "piece_type": node.piece_type,
            }
        prompt = create_annotation_prompt(fen, eval_tree, last_move_details)
        annotation = get_annotation_from_chatgpt(prompt)
        node.annotation = annotation

def generate_annotations_for_game(pgn_file: str, ply_depth: int) -> PGNTreeNode:
    """
    Parse a PGN file, annotate the main line with commentary,
    and return the annotated tree.
    """
    root = parse_pgn_to_tree(pgn_file)
    analyzer = StockfishAnalyzer()
    annotate_main_line(root, analyzer, ply_depth)
    analyzer.close()
    return root

# For testing:
if __name__ == "__main__":
    tree = generate_annotations_for_game("data/raw/mini.pgn", ply_depth=2)
    print("Root annotation:")
    print(tree.annotation)
    if tree.children:
        print("First move annotation:")
        print(tree.children[0].annotation)
