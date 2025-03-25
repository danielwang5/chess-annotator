# main.py
import argparse
import os
import asyncio
import chess.pgn
from src.annotation_generator import generate_annotations_for_game
from src.pgn_parser import PGNTreeNode

# --- Monkey-patch asyncio.gather to remove the "loop" keyword argument ---
_original_gather = asyncio.gather
def gather_no_loop(*args, **kwargs):
    kwargs.pop("loop", None)
    return _original_gather(*args, **kwargs)
asyncio.gather = gather_no_loop
# -----------------------------------------------------------------------

def print_mainline_annotations(node: PGNTreeNode, depth: int = 0):
    indent = " " * (depth * 2)
    # Use the stored SAN notation if available (or "Start" for the root).
    move_str = node.move_san if node.move_san else "Start"
    print(f"{indent}{move_str}: {node.annotation}")
    if node.children:
        print_mainline_annotations(node.children[0], depth + 1)

def convert_tree_to_pgn(root: PGNTreeNode) -> str:
    """
    Convert the annotated linear tree back into a PGN string.
    Each move's annotation is added as a comment.
    """
    game = chess.pgn.Game()
    node = game
    current = root
    while current.children:
        child = current.children[0]
        node = node.add_variation(child.move)
        if child.annotation:
            node.comment = child.annotation
        current = child
    exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=True)
    return game.accept(exporter)

def save_annotated_pgn(pgn_string: str, input_pgn_path: str):
    filename = os.path.basename(input_pgn_path)
    output_path = os.path.join("data", "processed", filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pgn_string)
    print(f"Annotated PGN saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Chess Game Annotation Tool (Main Line Only)")
    parser.add_argument("--pgn", type=str, required=True, help="Path to PGN file")
    parser.add_argument("--ply_depth", type=int, default=2, help="Depth of evaluation tree (ply)")
    args = parser.parse_args()
    
    annotated_tree = generate_annotations_for_game(args.pgn, args.ply_depth)
    print("Annotated main line:")
    print_mainline_annotations(annotated_tree)
    
    annotated_pgn = convert_tree_to_pgn(annotated_tree)
    save_annotated_pgn(annotated_pgn, args.pgn)

if __name__ == "__main__":
    main()
