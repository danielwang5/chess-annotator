# prompt_engineering.py

def format_eval_tree(eval_tree: dict, depth: int = 0) -> str:
    """
    Recursively formats the evaluation tree into a Markdown nested bullet list.
    Each move is listed with a bullet point, indented by two spaces per depth level.
    """
    lines = []
    indent = "  " * depth
    for move_san, info in eval_tree.items():
        line = f"{indent}- {move_san}: {info['score']}"
        lines.append(line)
        if info["subtree"]:
            subtree_str = format_eval_tree(info["subtree"], depth=depth+1)
            lines.append(subtree_str)
    return "\n".join(lines)


def create_annotation_prompt(fen: str, eval_tree: dict, threat_tree: dict, last_move_details: dict = None) -> str:
    """
    In one sentence, provide a concise annotation of the position focusing on the impact of the last move.
    Use the internal context (Regular Eval Tree and Threat Tree) for your analysis but do not reference them directly.
    """
    if last_move_details is None:
        last_move_str = "None (starting position)"
    else:
        last_move_str = (f"{last_move_details['move_san']} (a {last_move_details['piece_type']} from "
                         f"{last_move_details['from']} to {last_move_details['to']})")
    
    eval_tree_str = format_eval_tree(eval_tree)
    threat_tree_str = format_eval_tree(threat_tree)
    
    prompt = (
        "You are a chess expert. In one sentence, provide a very concise annotation of the position, focusing on the impact of the last move. "
        "Use the internal analysis (Regular Eval Tree and Threat Tree) to guide your response but do not mention raw numbers or trees. \n\n"
        f"Last move: {last_move_str}\n"
        f"FEN: {fen}\n\n"
        "Regular Eval Tree (internal):\n" + eval_tree_str + "\n\n"
        "Threat Tree (internal):\n" + threat_tree_str + "\n\n"
        "Annotation:"
    )
    return prompt

# For testing:
if __name__ == "__main__":
    sample_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    sample_eval_tree = {
        "e4": {"move": "e2e4", "score": 0.30, "subtree": {}},
        "d4": {"move": "d2d4", "score": 0.31, "subtree": {}},
    }
    sample_threat_tree = {
        "e5": {"move": "e7e5", "score": 0.50, "subtree": {}},
        "d5": {"move": "d7d5", "score": 0.48, "subtree": {}},
        "Nf6": {"move": "g8f6", "score": 0.47, "subtree": {}},
    }
    last_move_details = {
        "move_san": "e4",
        "from": "e2",
        "to": "e4",
        "piece_type": "P"
    }
    print(create_annotation_prompt(sample_fen, sample_eval_tree, sample_threat_tree, last_move_details))
