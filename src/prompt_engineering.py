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

def create_annotation_prompt(fen: str, eval_tree: dict) -> str:
    """
    Creates a prompt for ChatGPT using the given FEN and evaluation tree.
    """
    eval_tree_str = format_eval_tree(eval_tree)
    prompt = (
        f"You are a chess expert. Analyze the following position and provide a concise annotation explaining "
        f"the strategic ideas and potential plans.\n\n"
        f"Position (FEN): {fen}\n\n"
        f"Evaluation Tree (top moves for the next moves):\n{eval_tree_str}\n\n"
        f"Annotation (in one sentence if the position is simple, or a full paragraph if the position is rich):"
        f"Also comment on the position based on ideas presented by the candidate moves and corresponding evals "
        f"rather than just listing the things off of the move tree. Think about the ideas, and don't mention the "
        f"evaluation tree contents at all in your response."
    )
    return prompt

# For testing:
if __name__ == "__main__":
    sample_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4"
    sample_tree = {
        "O-O": {"move": "e1g1", "score": 0.2, "subtree": {}},
        "Nc3": {"move": "b1c3", "score": 0.1, "subtree": {}},
    }
    prompt = create_annotation_prompt(sample_fen, sample_tree)
    print(prompt)
