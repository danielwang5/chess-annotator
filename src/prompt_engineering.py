# prompt_engineering.py

def transform_eval_to_rating(eval_value: float, prev_eval: float = 0.0, is_white: bool = True) -> float:
    """
    Transform an evaluation value into a rating from 0.0 to 1.0.
    The rating is based on the improvement/deterioration of the position after the move.
    
    Args:
        eval_value: The evaluation after the move
        prev_eval: The evaluation before the move (default 0.0 for starting position)
        is_white: Whether the move was made by White (True) or Black (False)
    
    Returns:
        A rating from 0.0 to 1.0 where:
        - 0.0 represents a terrible move that significantly worsens the position
        - 0.5 represents a move that maintains the position's evaluation
        - 1.0 represents a perfect move that significantly improves the position
    """
    # For Black, we need to invert the evaluation difference
    # because positive eval is good for White, bad for Black
    eval_diff = eval_value - prev_eval
    if not is_white:
        eval_diff = -eval_diff
    
    # Clip the difference to [-2.0, 2.0] range
    clipped = max(min(eval_diff, 2.0), -2.0)
    # Transform to [0, 1] range
    return (clipped + 2.0) / 4.0

def format_eval_tree(eval_tree: dict, depth: int = 0, prev_eval: float = 0.0, is_white: bool = True) -> str:
    """
    Recursively formats the evaluation tree into a Markdown nested bullet list.
    Each move is listed with a bullet point, indented by two spaces per depth level.
    """
    lines = []
    indent = "  " * depth
    for move_san, info in eval_tree.items():
        rating = transform_eval_to_rating(info['score'], prev_eval, is_white)
        line = f"{indent}- {move_san}: {rating:.2f}"
        lines.append(line)
        if info["subtree"]:
            lines.append(format_eval_tree(info["subtree"], depth=depth+1, prev_eval=info['score'], is_white=not is_white))
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
        current_rating = 0.5  # Starting position is neutral
        is_white = True
    else:
        last_move_str = (
            f"{last_move_details['move_san']} (a {last_move_details['piece_type']} from "
            f"{last_move_details['from']} to {last_move_details['to']})"
        )
        prev_eval = last_move_details.get('prev_eval', 0.0)
        is_white = last_move_details.get('is_white', True)
        current_rating = transform_eval_to_rating(current_eval, prev_eval, is_white)
    
    eval_tree_str = format_eval_tree(eval_tree, is_white=True)  # Start with White's moves
    threat_tree_str = format_eval_tree(threat_tree, is_white=False)  # Threats are from Black
    
    details = (
        "IMPORTANT: Respond with exactly ONE sentence (max 25 words) focusing on the impact of the last move. "
        "Do not mention numbers, tree details, or reference the evaluation trees - they are only for internal guidance.\n\n"
        f"Last move: {last_move_str}\n"
        f"Current position rating: {current_rating:.2f}\n"
        f"Position (FEN): {fen}\n\n"
        "Regular Eval Tree (internal guidance only):\n"
        "Each move's rating shows how much it improves (1.0) or worsens (0.0) the position:\n"
        f"{eval_tree_str}\n\n"
        "Threat Tree (internal guidance only):\n"
        "Shows opponent's potential moves if you skip your turn:\n"
        f"{threat_tree_str}\n\n"
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
                "The evaluation values are transformed to a 0-1 scale where:\n"
                "- 0.0 represents a terrible move (worse than -2.0)\n"
                "- 0.5 represents an equal position (0.0)\n"
                "- 1.0 represents a perfect move (better than +2.0)\n\n"
                "IMPORTANT FORMATTING RULES:\n"
                "1. Your response must be exactly ONE sentence\n"
                "2. Maximum 25 words\n"
                "3. Do not mention raw numbers or tree details\n"
                "4. Focus on the impact of the last move and potential ideas\n"
                "5. The evaluation trees are for internal guidance only - never reference them in your output\n\n"
                "GOOD EXAMPLES:\n"
                "- 'White's e4 creates a strong center and opens lines for development.'\n"
                "- 'Black's knight retreat allows White to gain space in the center.'\n"
                "- 'The bishop exchange weakens Black's kingside structure.'\n\n"
                "BAD EXAMPLES:\n"
                "- 'The position is equal with a rating of 0.5.' (mentions numbers)\n"
                "- 'White has several good moves including e4, d4, and Nf3.' (too general)\n"
                "- 'Black's position is worse because of the threat tree showing Qh4.' (mentions internal details)\n"
                "- 'The evaluation tree suggests White is better.' (references internal guidance)\n\n"
                "Use the evaluation trees only to inform your analysis, but keep your response brief and focused on the key strategic point."
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
