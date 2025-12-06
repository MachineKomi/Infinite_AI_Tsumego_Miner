# AGENTS.md

> **SYSTEM CONTEXT: INFINITE TSUMEGO MINER**
> *This file contains the immutable Source of Truth for this repository. All AI agents working here must align with these directives, architectural decisions, and mission parameters.*

## 1. Mission Profile

**Objective:** Construct an autonomous "Mining Rig" that generates infinite, high-quality Go (Weiqi/Baduk) tsumego puzzles.

**End Goal:** These puzzles will power a separate consumer application ("The Game")—a visual novel/dating sim with meta-progression elements.

**Core Philosophy:**

  * **Quantity through Autonomy:** The system runs indefinitely without human intervention.
  * **Quality through Adversity:** Puzzles are born from "blunders" in chaotic, high-temperature self-play games, not random stone placement.
  * **Respect for Intelligence:** We treat our Neural Networks not as tools, but as a "Bench" of elite experts.

---

## 2. Architecture: "The Arena"

The system utilizes a **Dual-Engine** approach to generate and validate puzzles.

### A. The Components

1.  **`MatchOrchestrator` (`src/miner.py`)**: The conductor. Initializes the bench, pairs agents, manages the game loop, and extracts puzzles.
2.  **`NetworkBench` (`src/network_bench.py`)**: A dignified roster of available Neural Agents. Manages model discovery and matchmaking.
3.  **`ModelRegistry` (`src/model_registry.py`)**: Central registry mapping actual filenames to meaningful aliases while preserving network lineage.
4.  **`MiningLogger` (`src/logger.py`)**: Structured logging infrastructure for production runs.

### B. The Referee and Players

| Alias | Role | Architecture | ELO | Description |
|-------|------|--------------|-----|-------------|
| **The_High_Referee** | Referee | b28c512nbt | 14079 | Strongest confidently-rated network. Absolute truth. |
| **The_Chameleon** | Player | b18c384nbt | Variable | Human-SL model. Emulates 18k to 9d. |
| **The_Specialist** | Player | b18c384nbt | N/A | 9x9 finetuned specialist. |
| **The_Titan** | Player | b60c320 | 13504 | Large 60-block network. Very strong. |
| **The_Veteran** | Player | b20c256x2 | 12520 | Classic "g170 era" style. |
| **The_Apprentice** | Player | b6c96 | 9023 | Lightweight SDK-level. |
| **The_Student** | Player | b6c96 | 3330 | DDK-level mistakes. |
| **The_Beginner** | Player | b6c96 | 1530 | Weak DDK-level. |
| **The_Novice** | Player | b6c96 | 484 | Very weak. Many blunders. |

### C. The Pipeline

1.  **Matchmaking:** Two agents are selected from the `NetworkBench`.
2.  **Simulation:** They play a 9x9 game with high temperature (creative/error-prone).
3.  **Blunder Detection (The "Delta"):**
    * Before every move, the **Referee** evaluates the position (winrate from current player's perspective).
    * The **Player** makes a move.
    * The **Referee** evaluates the new position.
    * **Trigger:** If winrate drops from >90% to <15%, a **Puzzle** is detected.
4.  **Extraction:** The game state *before* the blunder is saved. The puzzle is: "Find the correct move."
5.  **Deduplication:** Position hash prevents duplicate puzzles.
6.  **Export:** JSON + SGF files saved to `output/`.

### D. Arena Randomization ("Personality Profiles")

Each match generates **fresh randomized parameters** for both Black and White players, creating maximum variety:

| Parameter | Range | Weighted Categories |
|-----------|-------|---------------------|
| **Temperature** | 0.8 - 1.5 | Conservative (10%), Balanced (40%), Creative (35%), Chaotic (15%) |
| **Max Visits** | 20 - 300 | Intuitive (25%), Casual (40%), Thoughtful (25%), Deep (10%) |
| **HumanSL Rank** | 18k - 6d | SDK-weighted distribution (10k most common) |

This means the same network can play at different "strength levels" across matches, and the puzzle output tracks which settings produced each blunder via `generator_settings`.

---

## 3. Technical Implementation

### File Structure

```text
Infinite_AI_Tsumego_Miner/
├── assets/
│   ├── katago/                 # Binary + DLLs (gitignored)
│   │   └── README.md           # Setup instructions
│   └── models/                 # .bin.gz weights (gitignored)
│       └── README.md           # Model documentation
├── configs/
│   ├── gen_config.cfg          # Player config (High Temp, Fast)
│   ├── referee_config.cfg      # Referee config (Zero Temp, Deep)
│   └── player_human.cfg        # Special config for HumanSL
├── output/                     # Generated puzzles (JSON + SGF)
├── logs/                       # Log files (when --log-file enabled)
├── src/
│   ├── __init__.py
│   ├── miner.py                # Main loop (MatchOrchestrator)
│   ├── network_bench.py        # Model management
│   ├── katago_wrapper.py       # Subprocess interface
│   ├── model_registry.py       # Filename → Alias mapping
│   └── logger.py               # Logging infrastructure
├── AGENTS.md                   # This file
├── README.MD                   # Project overview
├── SETUP_WINDOWS.md            # Windows setup guide
└── requirements.txt            # Python dependencies
```

### Key Python Classes

  * **`KataGoEngine`**: Wrapper around `subprocess.Popen`. Handles JSON communication via `stdin`/`stdout`. Supports `overrideSettings` for HumanSL.
  * **`NetworkBench`**: Factory that discovers models and produces `NeuralAgent` instances.
  * **`NeuralAgent`**: Represents a single neural personality with tracked statistics.
  * **`MatchOrchestrator`**: The main loop. Handles blunder detection, puzzle extraction, and deduplication.

---

## 4. Data Specification (Output)

Puzzles are saved as **JSON** files in `output/`. The consuming Game App expects this schema.

### Enhanced Schema (v2)

```json
{
  "uuid": "a1b2c3d4",
  "timestamp": "2025-12-06T15:30:00Z",
  "generated_by": "The_Chameleon",
  "puzzle_type": "life_and_death_blunder",
  "board_size": 9,
  
  "setup_moves": [["B", "C3"], ["W", "D4"], ...],
  "color_to_play": "B",
  
  "blunder": {
    "move": "E5",
    "winrate_before": 0.95,
    "winrate_after": 0.08,
    "delta": 0.87
  },
  
  "solution": {
    "correct_move": "F6",
    "referee_winrate": 0.99,
    "referee_visits": 600,
    "policy_prior": 0.02,
    "difficulty_metrics": {
      "visits_to_solve": 600,
      "policy_prior": 0.02
    }
  },
  
  "analysis": {
    "policy_distribution": [
      {"move": "F6", "policy": 0.02, "winrate": 0.99, "visits": 450},
      {"move": "G5", "policy": 0.15, "winrate": 0.85, "visits": 100}
    ],
    "wrong_move_refutation": [
      {"response": "H3", "winrate": 0.95}
    ]
  },
  
  "metadata": {
    "ownership": [...],
    "score_lead": 15.5,
    "position_hash": "a1b2c3d4e5f6"
  }
}
```

---

## 5. Configuration Reference

### The Players (`gen_config.cfg` / `player_human.cfg`)

  * `chosenMoveTemperature`: **1.1 to 1.25** (Essential for variety/blunders).
  * `maxVisits`: **50** (Fast, intuitive play).
  * `includePolicy`: **true** (Required for HumanSL).

### The Referee (`referee_config.cfg`)

  * `chosenMoveTemperature`: **0** (Deterministic).
  * `maxVisits`: **600+** (Deep verification).
  * `includeOwnership`: **true** (Required for UI visualization).

### Blunder Detection Thresholds

  * **Before:** Current player winrate must be > 90%
  * **After:** Current player winrate must drop to < 15%
  * These values are defined in `miner.py` constants.

---

## 6. CLI Usage

```bash
# Standard mining run
python src/miner.py

# Test connectivity without mining
python src/miner.py --dry-run

# Enable file logging
python src/miner.py --log-file

# Debug mode (verbose output)
python src/miner.py --debug
```

---

## 7. Current Operational Status

  * **Repo:** Bootstrapped with comprehensive infrastructure.
  * **Phase:** Ready for Alpha Mining.
  * **Models:** 11 neural networks registered in the bench.
  * **Next Priority:** Run `--dry-run` to verify setup, then begin puzzle generation.

---

## 8. License

This project is licensed under the **GNU Affero General Public License v3 (AGPLv3)**.

All source files include the AGPL header as required.

-----

> *End of Context. All agents proceed with these specifications.*