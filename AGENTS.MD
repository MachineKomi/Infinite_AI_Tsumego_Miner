# AGENTS.md

> **SYSTEM CONTEXT: INFINITE TSUMEGO MINER**
> *This file contains the immutable Source of Truth for this repository. All AI agents working here must align with these directives, architectural decisions, and mission parameters.*

## 1\. Mission Profile

**Objective:** Construct an autonomous "Mining Rig" that generates infinite, high-quality Go (Weiqi/Baduk) tsumego puzzles.
**End Goal:** These puzzles will power a separate consumer application ("The Game")—a visual novel/dating sim with meta-progression elements.
**Core Philosophy:**

  * **Quantity through Autonomy:** The system runs indefinitely without human intervention.
  * **Quality through Adversity:** Puzzles are born from "blunders" in chaotic, high-temperature self-play games, not random stone placement.
  * **Respect for Intelligence:** We treat our Neural Networks not as tools, but as a "Bench" of elite experts.

## 2\. Architecture: "The Arena"

The system utilizes a **Dual-Engine** approach to generate and validate puzzles.

### A. The Components

1.  **`MatchOrchestrator` (`src/miner.py`)**: The conductor. It initializes the bench, pairs agents, and manages the game loop.
2.  **`NetworkBench` (`src/network_bench.py`)**: A dignified roster of available Neural Agents (The Chameleon, The Veteran, etc.). It manages the "personalities" of the players.
3.  **The High Referee (`STR_CONF_...b28`)**: The absolute source of truth. It does not play; it only analyzes. It uses high playouts (600+) and zero temperature to judge the "truth" of a board state.
4.  **The Players**:
    *   **The Chameleon (`humanv0`)**: Human-style intuition.
    *   **The Veteran (`kata1-b6c96`)**: Lower Elo (484-3330) lightweight networks for variability.
    *   **The Titan (`b60` / `b20`)**: Stronger sparring partners.

### B. The Pipeline

1.  **Matchmaking:** Two agents are selected from the `NetworkBench`.
2.  **Simulation:** They play a 9x9 game.
3.  **Blunder Detection (The "Delta"):**
      * Before every move, the **Referee** judges the winrate ($W_{pre}$).
      * The **Player** makes a move.
      * The **Referee** judges the new winrate ($W_{post}$).
      * **Trigger:** If ($W_{pre} > 95\%$) AND ($W_{post} < 10\%$), a **Puzzle** is detected.
4.  **Extraction:** The game pauses. The state *before* the blunder is saved. The puzzle is: "Revert the blunder and find the winning path."

## 3\. Technical Implementation

### File Structure

```text
Infinite_AI_Tsumego_Miner/
├── assets/
│   ├── katago/                 # Binary (ignored by git)
│   └── models/                 # .bin.gz weights (ignored by git)
├── configs/
│   ├── gen_config.cfg          # Player config (High Temp, Fast)
│   ├── referee_config.cfg      # Referee config (Strict, Ownership=True)
│   └── player_human.cfg        # Special config for HumanSL model
├── output/                     # Generated JSON puzzles
├── src/
│   ├── miner.py                # Main loop (MatchOrchestrator)
│   ├── network_bench.py        # Model management
│   └── katago_wrapper.py       # Subprocess Interface
└── AGENTS.md                   # This file
```

### Key Python Classes

  * **`KataGoEngine`**: Wrapper around `subprocess.Popen`. Handles JSON communication via `stdin`/`stdout`. **Crucial:** Must handle `overrideSettings` for the HumanSL model.
  * **`NetworkBench`**: Factory that produces `NeuralAgent` instances.
  * **`MatchOrchestrator`**: The main loop. Handles the "Referee Check" logic.

## 4\. Data Specification (Output)

Puzzles are saved as **JSON** files in `output/`. The consuming Game App expects this exact schema.

```json
{
  "uuid": "puzzle_8s8d9f",
  "puzzle_type": "life_and_death_blunder",
  "generated_by": "The_Chameleon",
  "setup_moves": [ ["B", "C3"], ["W", "D4"] ... ], // Sequence to reach state
  "color_to_play": "B",
  "solution": {
    "correct_move": "E5",
    "referee_winrate": 0.99,
    "difficulty_metrics": {
       "visits_to_solve": 450, // Higher = Harder
       "policy_prior": 0.02    // Lower = Harder (Blind spot)
    }
  },
  "metadata": {
    "ownership": [ ... ], // Flattened 81-float array for Territory UI
    "score_lead": 15.5
  }
}
```

## 5\. Configuration Reference

### The Players (`gen_config.cfg` / `player_human.cfg`)

  * `chosenMoveTemperature`: **1.1 to 1.25** (Essential for variety/blunders).
  * `maxVisits`: **50** (Fast, intuitive play).
  * `includePolicy`: **true** (Required for HumanSL).

### The Referee (`referee_config.cfg`)

  * `chosenMoveTemperature`: **0** (Deterministic).
  * `maxVisits`: **600+** (Deep verification).
  * `includeOwnership`: **true** (Required for UI visualization).

## 6\. Current Operational Status

  * **Repo:** Bootstrapped.
  * **Phase:** Alpha Mining.
  * **Next Priority:** Run the miner, generate the first 100 puzzles, and verify the "Blunder Threshold" (currently set to 0.85 delta).

## 7\. LICENSE - GNU Affero General Public License v3.0

### Next Steps: Applying the License to our Code

To be fully compliant, the AGPL requires us to add a notice to the start of each source file (e.g., `src/miner.py`, `src/network_bench.py`).

Add this header to the top of our Python files:

```python
"""
Infinite AI Tsumego Miner
Copyright (C) 2025 [Your Name]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
```

-----

> *End of Context. All agents proceed with these specifications.*