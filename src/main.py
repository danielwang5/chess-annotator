# main.py
import argparse
from src.annotation_generator import generate_annotations_for_game
from src.pgn_parser import PGNTreeNode

def print_mainline_annotations(node: PGNTreeNode, depth: int = 0):
    indent = " " * (depth * 2)
    # If this is the root node, there’s no move notation
    move_str = node.board.san(node.move) if node.move else "Start"
    print(f"{indent}{move_str}: {node.annotation}")
    # Since the PGN is linear, only one child is expected (the main line)
    if node.children:
        print_mainline_annotations(node.children[0], depth + 1)

def main():
    parser = argparse.ArgumentParser(description="Chess Game Annotation Tool (Main Line Only)")
    parser.add_argument("--pgn", type=str, required=True, help="Path to PGN file")
    parser.add_argument("--ply_depth", type=int, default=2, help="Depth of evaluation tree (ply)")
    args = parser.parse_args()
    
    annotated_tree = generate_annotations_for_game(args.pgn, args.ply_depth)
    print("Annotated main line:")
    print_mainline_annotations(annotated_tree)

if __name__ == "__main__":
    main()
