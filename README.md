# Chess Annotation Project

This project builds a chess annotation tool that:
- Parses PGN files into a branching tree of chess positions (using FEN)
- Uses Stockfish to generate a mini evaluation tree (top moves and evaluations) for each position
- Leverages ChatGPT to generate human-readable annotations from the current position and engine evaluations

## Project Structure

chess_annotation_project/
├── data/
│   ├── raw/ # Raw PGN files 
│   └── processed/ # Processed/enriched PGNs with engine evaluations 
├── docs/ # Documentation and prompt examples 
├── src/ # Source code (PGN parsing, engine interfacing, ChatGPT integration) 
├── tests/ # Unit tests for modules 
├── .env # Environment variables (API keys, paths, etc.) 
├── requirements.txt # Python dependencies 
└── README.md # This file

## Features

- **Smart Evaluation Handling**: 
  - Transforms raw engine evaluations into a 0-1 scale
  - Considers move impact relative to previous position
  - Takes into account player color when interpreting evaluations

- **Natural Commentary**:
  - Generates human-readable annotations in a commentator style
  - References standard moves and patterns when relevant
  - Explains why moves work or don't work in specific positions
  - Focuses on strategic ideas rather than raw evaluations

- **Analysis Trees**:
  - Regular evaluation tree shows top candidate moves for next N turns
  - Threat tree shows opponent's potential moves if you skip your turn
  - Each move's rating (0.0-1.0) indicates its impact on the position

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
4. Set up your `.env` file with:
   ```
   OPENAI_API_KEY=your_api_key_here
   STOCKFISH_PATH=path_to_stockfish_executable
   ```

## Running the Project

To run the annotation pipeline:
```bash
python -m src.main --pgn data/raw/sample.pgn --ply_depth 3
```

Parameters:
- `--pgn`: Path to input PGN file
- `--ply_depth`: Depth of evaluation tree (how many moves to look ahead)

## Testing

Run tests with:
```bash
pytest tests/
```

## Documentation

Check the `docs/` folder for additional design notes and prompt engineering examples.

## Example Annotations

The system generates concise, insightful annotations that:
- Focus on strategic impact and ideas
- Reference standard moves when relevant
- Explain why moves work or don't work in specific positions
- Avoid technical details and raw evaluations

Example outputs:
- "White keeps a considerable edge in view of his better central control and Black's unstable central knight."
- "In this case, the standard 16.Ne5 does not work since the d4-pawn is hanging."
- "This is an important alternative, such a position has already been examined with an extra Bc1-d2 and with the a-pawns still on their initial squares."