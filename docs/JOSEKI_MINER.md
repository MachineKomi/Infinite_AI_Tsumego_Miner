# Joseki Mining Feature

The **Joseki Miner** is a specialized module within the Infinite AI Tsumego Miner project. While the main miner focuses on finding tactical blunders (Tsumego), the Joseki Miner maps out valid opening sequences (Joseki) in the corner.

## 🎯 Goal
To generate comprehensive "Joseki Trees" for standard corner openings (e.g., 4-4, 3-4). These trees include **ALL** valid moves within a specific tolerance, allowing users to practice against a wide variety of AI-approved responses, not just the single "best" move.

## ⚙️ How It Works

The miner explores the game tree recursively starting from a defined position (e.g., Black at 4-4).

### 1. The Scope
- **Board Size:** 19x19 (Standard).
- **Focus Area:** Top-Right 9x9 Corner.
- **Tenuki Filter:** Any move played outside the Top-Right 9x9 quadrant is considered "Tenuki" (playing elsewhere). The miner notes it as a valid option but does not explore that branch further.

### 2. Validity Tolerance
Unlike standard play where an AI picks the *best* move, the Joseki Miner collects *all* moves that are "good enough." A move is valid if:
- **Winrate Drop:** <= 5% (0.05) compared to the best move.
- **Score Loss:** <= 2.0 points compared to the best move.
- **Visits:** The move must have at least 50 visits to ensure the evaluation is stable.

### 3. Output
The miner produces a JSON file for each starting position containing the full move tree.

**File Path:** `output/joseki/{opening_name}.json`

**JSON Structure:**
```json
{
  "name": "4-4 Point (Hoshi)",
  "root_moves": [["B", "Q16"]],
  "tree": {
    "move": "Q16",
    "winrate": 0.48,
    "score": 0.0,
    "children": [
      {
        "move": "R14",  // Knight's approach
        "winrate": 0.47,
        "score": -0.2,
        "children": [...]
      },
      {
        "move": "F3",   // Tenuki (outside 9x9)
        "winrate": 0.47,
        "score": -0.2,
        "children": []  // Terminated
      }
    ]
  }
}
```

## 🚀 Usage

### Prerequisites
You must have a strong KataGo model (e.g., "The High Referee") installed in `assets/models/`.

### Running the Miner
To mine all defined starting positions:

```bash
python src/joseki_miner.py
```

To enable debug logging:

```bash
python src/joseki_miner.py --debug
```

### Adding New Openings
Edit `src/joseki_definitions.py` to add new starting positions:

```python
STARTING_POSITIONS = [
    {
        "name": "New Opening",
        "moves": [["B", "Q16"], ["W", "R14"]],
        "description": "..."
    },
    ...
]
```
