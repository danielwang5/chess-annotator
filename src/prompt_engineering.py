# prompt_engineering.py

def format_eval_tree(eval_tree: dict, indent: int = 0) -> str:
    """
    Recursively formats the evaluation tree into a human-readable string.
    """
    lines = []
    indent_str = " " * indent
    for move_san, info in eval_tree.items():
        line = f"{indent_str}- {move_san}: score {info['score']}"
        lines.append(line)
        if info["subtree"]:
            subtree_str = format_eval_tree(info["subtree"], indent=indent+2)
            lines.append(subtree_str)
    return "\n".join(lines)

def create_annotation_prompt(fen: str, eval_tree: dict, last_move_details: dict = None) -> str:
    """
    Creates a prompt for ChatGPT including the last move details.
    If last_move_details is provided, it should be a dict with keys:
    'move_san', 'from', 'to', and 'piece_type'.
    The prompt now instructs the model to be concise (using partial sentences if needed).
    """
    if last_move_details is None:
        last_move_str = "None (starting position)"
    else:
        last_move_str = (
            f"{last_move_details['move_san']} (a {last_move_details['piece_type']} "
            f"from {last_move_details['from']} to {last_move_details['to']})"
        )
    
    eval_tree_str = format_eval_tree(eval_tree)
    prompt = (
        f"You are a chess expert. Focus your analysis on the last move played, which is {last_move_str}. "
        "Provide a concise annotation, using partial sentences if needed, that explains the strategic impact "
        "and potential plans arising from the move.\n\n"
        f"Position (FEN): {fen}\n\n"
        f"Evaluation Tree (top moves for the next moves):\n{eval_tree_str}\n\n"
        "Annotation (concise):"
    )
    return prompt

# For testing:
if __name__ == "__main__":
    sample_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    sample_tree = {
        "e4": {"move": "e2e4", "score": 0.3, "subtree": {}},
        "d4": {"move": "d2d4", "score": 0.1, "subtree": {}},
    }
    last_move_details = {
        "move_san": "e4",
        "from": "e2",
        "to": "e4",
        "piece_type": "P"
    }
    prompt = create_annotation_prompt(sample_fen, sample_tree, last_move_details=last_move_details)
    print(prompt)
