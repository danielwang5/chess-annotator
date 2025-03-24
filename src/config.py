# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# OpenAI API key for ChatGPT
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Path to Stockfish executable
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/local/bin/stockfish")

# Engine analysis parameters
ENGINE_TIME_LIMIT = 0.1  # seconds per analysis call
ENGINE_DEPTH = 15
ENGINE_MULTIPV = 3

# Analysis tree depth (how many plies to explore in evaluation)
ANALYSIS_PLY_DEPTH = 5
