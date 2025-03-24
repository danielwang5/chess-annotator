# tests/test_annotation_generator.py
import os
import chess
import pytest
from src.pgn_parser import parse_pgn_to_tree
from src.stockfish_interface import StockfishAnalyzer
from src.prompt_engineering import create_annotation_prompt, format_eval_tree
from src.chatgpt_interface import get_annotation_from_chatgpt

# Example: test that the prompt is formatted correctly
def test_format_eval_tree():
    sample_tree = {
        "O-O": {"move": "e1g1", "score": 0.2, "subtree": {}},
        "Nc3": {"move": "b1c3", "score": 0.1, "subtree": {}},
    }
    formatted = format_eval_tree(sample_tree)
    assert "- O-O: score 0.2" in formatted
    assert "- Nc3: score 0.1" in formatted

# Test ChatGPT API call (this is more of an integration test; consider mocking the API for unit tests)
@pytest.mark.skip(reason="Requires valid API key and network access")
def test_get_annotation_from_chatgpt():
    prompt = "Test prompt for chess annotation."
    annotation = get_annotation_from_chatgpt(prompt)
    assert isinstance(annotation, str)
    assert len(annotation) > 0

# Test PGN parsing (using a sample PGN file from tests/data if available)
def test_parse_pgn_to_tree(tmp_path):
    sample_pgn = """
[Event "Test Game"]
[Site "?"]
[Date "2025.03.24"]
[Round "?"]
[White "White"]
[Black "Black"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *
"""
    pgn_file = tmp_path / "test.pgn"
    pgn_file.write_text(sample_pgn)
    tree = parse_pgn_to_tree(str(pgn_file))
    # Ensure the tree has at least one move
    assert tree.children
    # Ensure the root board is the starting position
    import chess
    assert tree.board.fen() == chess.Board().fen()
