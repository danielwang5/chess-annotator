# prompt_engineering.py

def transform_eval_to_rating(eval_value: float) -> float:
    """
    Transform an evaluation value into a rating from 0.0 to 1.0.
    - Very bad moves (< -2.0) get 0.0
    - Perfect moves (> 2.0) get 1.0
    - Values in between are linearly scaled
    """
    # Clip values to [-2.0, 2.0] range
    clipped = max(min(eval_value, 2.0), -2.0)
    # Transform to [0, 1] range
    return (clipped + 2.0) / 4.0

def format_eval_tree(eval_tree: dict, depth: int = 0) -> str:
    """
    Recursively formats the evaluation tree into a Markdown nested bullet list.
    Each move is listed with a bullet point, indented by two spaces per depth level.
    """
    lines = []
    indent = "  " * depth
    for move_san, info in eval_tree.items():
        rating = transform_eval_to_rating(info['score'])
        line = f"{indent}- {move_san}: {rating:.2f}"
        lines.append(line)
        if info["subtree"]:
            lines.append(format_eval_tree(info["subtree"], depth=depth+1))
    return "\n".join(lines)

def create_annotation_prompt(fen: str, current_eval: float, eval_tree: dict, threat_tree: dict, last_move_details: dict = None) -> str:
    """
    Creates a prompt for a single position.
    The prompt includes:
      - Last move details.
      - Current evaluation.
      - The position (FEN).
      - Internal context: Regular evaluation tree and threat tree (in Markdown).
    The final output should be one concise sentence (max ~25 words) focusing on the impact of the last move and ideas.
    (Do not reference raw numbers or tree details in your final output.)
    """
    if last_move_details is None:
        last_move_str = "None (starting position)"
    else:
        last_move_str = (
            f"{last_move_details['move_san']} (a {last_move_details['piece_type']} from "
            f"{last_move_details['from']} to {last_move_details['to']})"
        )
    current_rating = transform_eval_to_rating(current_eval)
    eval_tree_str = format_eval_tree(eval_tree)
    threat_tree_str = format_eval_tree(threat_tree)
    
    details = (
        f"Last move: {last_move_str}\n"
        f"Current position rating: {current_rating:.2f}\n"
        f"Position (FEN): {fen}\n\n"
        "Regular Eval Tree (internal):\n" + eval_tree_str + "\n\n"
        "Threat Tree (internal):\n" + threat_tree_str + "\n\n"
        "Annotation:"
    )
    return details

def generate_conversation_payload(positions_data: list) -> list:
    """
    Given a list of position data dictionaries, generate a full conversation payload.
    The first message is a system message with full instructions.
    Each subsequent message is a user message containing the position details.
    
    Each dictionary in positions_data must have:
      - fen (str)
      - current_eval (float)
      - eval_tree (dict)
      - threat_tree (dict)
      - last_move_details (dict or None)
    """
    # System message with detailed instructions (emphasize brevity)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a chess expert. Your task is to generate a very concise annotation (one sentence, max 25 words) "
                "for a given chess position. You are provided with internal context including the regular evaluation tree "
                "and a threat tree (which represent candidate moves and opponent's threats if the player skipped their move). "
                "Use this context only to inform your analysis, but do not mention raw numbers or tree details in your final output. "
                "Focus solely on the impact of the last move and potential ideas."
            )
        }
    ]
    
    # Each subsequent message contains only the details.
    for pos in positions_data:
        prompt_text = create_annotation_prompt(
            fen=pos["fen"],
            current_eval=pos["current_eval"],
            eval_tree=pos["eval_tree"],
            threat_tree=pos["threat_tree"],
            last_move_details=pos.get("last_move_details")
        )
        messages.append({"role": "user", "content": prompt_text})
    
    return messages

# For testing:
if __name__ == "__main__":
    sample_data = [
        {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "current_eval": 0.25,
            "eval_tree": {
                "e4": {"move": "e2e4", "score": 0.30, "subtree": {}},
                "d4": {"move": "d2d4", "score": 0.31, "subtree": {}},
            },
            "threat_tree": {
                "e5": {"move": "e7e5", "score": 0.50, "subtree": {}},
                "d5": {"move": "d7d5", "score": 0.48, "subtree": {}},
                "Nf6": {"move": "g8f6", "score": 0.47, "subtree": {}},
            },
            "last_move_details": {
                "move_san": "e4",
                "from": "e2",
                "to": "e4",
                "piece_type": "P"
            }
        }
    ]
    conv_payload = generate_conversation_payload(sample_data)
    for i, msg in enumerate(conv_payload):
        print(f"Message {i} ({msg['role']}):\n{msg['content']}\n{'-'*40}\n")
