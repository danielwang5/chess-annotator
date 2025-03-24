# Chess Annotation Project

This project builds a chess annotation tool that:
- Parses PGN files into a branching tree of chess positions (using FEN).
- Uses Stockfish to generate a mini evaluation tree (top moves and evaluations) for each position.
- Leverages ChatGPT to generate human-readable annotations from the current position and engine evaluations.

## Project Structure

chess_annotation_project/
├── data/
│ ├── raw/ # Raw PGN files 
│ └── processed/ # Processed/enriched PGNs with engine evaluations 
├── docs/ # Documentation and prompt examples 
├── src/ # Source code (PGN parsing, engine interfacing, ChatGPT integration) 
├── tests/ # Unit tests for modules 
├── .env # Environment variables (API keys, paths, etc.) 
├── requirements.txt # Python dependencies 
└── README.md # This file

## Setup

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file with the appropriate values.

## Running the Project
To run the annotation pipeline:
```bash
python src/main.py --pgn data/raw/sample.pgn --ply_depth 2
```

## Testing
Run tests with:
```bash
pytest tests/
```

## Documentation
Check the `docs/` folder for additional design notes and prompt engineering examples.