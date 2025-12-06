# Implementation Plan

## 1. System Overview
**Project:** Infinite AI Tsumego Miner
**Goal:** A headless Python application that uses KataGo to generate, validate, and grade Go puzzles (Tsumego) via adversarial self-play.
**License:** GNU AGPL v3
**Hardware Target:** NVIDIA RTX 4070 (Linux/Windows).

---

## 2. Repository Structure
The project follows a flat, modular architecture to decouple the "Mining" logic from the "Game" logic.

```text
infinite-tsumego-miner/
├── assets/
│   ├── katago/                 # KataGo Binary (v1.15.0+) - Ignored by git
│   └── models/                 # Neural Network weights (.bin.gz) - Ignored by git
├── configs/
│   ├── gen_config.cfg          # "Creative" High-Temp Config
│   ├── referee_config.cfg      # "Strict" Validator Config
│   └── player_human.cfg        # Special Config for HumanSL model
├── output/                     # Generated JSON puzzles land here
├── src/
│   ├── __init__.py
│   ├── miner.py                # Entry Point / MatchOrchestrator
│   ├── network_bench.py        # Agent/Model Management
│   └── katago_wrapper.py       # Subprocess Interface
├── AGENTS.md                   # System Context for AI Agents
├── Implementation_Plan.MD      # This file
├── Approach_and_Principles.MD  # Design Philosophy
├── LICENSE                     # AGPL v3
└── requirements.txt            # Dependencies (numpy, etc.)
````

-----

## 3\. Asset Requirements

The system requires specific external binaries and models to function.

| Asset Type | Specific Version | Internal Path | Purpose |
| :--- | :--- | :--- | :--- |
| **Engine** | KataGo v1.15.0+ (OpenCL/CUDA) | `assets/katago/katago` | Core analysis engine. |
| **Model A** | Latest `b18` (Strongest) | `assets/models/referee.bin.gz` | **The Referee:** strict validation. |
| **Model B** | `b18c384nbt-humanv0` | `assets/models/human.bin.gz` | **The Chameleon:** human-like errors. |
| **Model C** | `g170` (15 or 20 block) | `assets/models/vintage.bin.gz` | **The Veteran:** robotic/flawed style. |

-----

## 4\. Configuration Specifications

### A. The Creative Profile (`gen_config.cfg`)

Used by "The Veteran" and standard players to generate variety.

  * `chosenMoveTemperature`: **1.25** (Encourage sub-optimal, creative play).
  * `maxVisits`: **50** (Simulate intuition; speed).
  * `numSearchThreads`: **6**.

### B. The Human Profile (`player_human.cfg`)

Used by "The Chameleon" (HumanSL).

  * `includePolicy`: **true** (Required for human emulation).
  * `chosenMoveTemperature`: **1.1**.
  * `maxVisits`: **50**.

### C. The Strict Profile (`referee_config.cfg`)

Used by "The High Referee" to validate puzzles.

  * `chosenMoveTemperature`: **0** (Deterministic, best move only).
  * `maxVisits`: **600+** (Deep reading to prove uniqueness).
  * `includeOwnership`: **true** (Generates territory map for UI).
  * `includePolicy`: **true** (Used for difficulty grading).

-----

## 5\. Module Architecture

### `src/katago_wrapper.py`

  * **Responsibility:** Manages the raw `subprocess.Popen` connection to the KataGo binary.
  * **Key Feature:** Must handle the `overrideSettings` JSON field to allow the HumanSL model to switch ranks (18k to 9d) dynamically per query.

### `src/network_bench.py` (The Roster)

  * **Responsibility:** Initializes available models.
  * **Logic:**
      * Scans `assets/models`.
      * Instantiates `KataGoEngine` for each found model.
      * Exposes a `select_matchup()` method to return two agents for a game.

### `src/miner.py` (The Orchestrator)

  * **Responsibility:** The Main Loop.
  * **Algorithm:**
    1.  **Init:** Spin up the Bench (Players) and the Referee.
    2.  **Match:** Pick Agent A (Black) vs Agent B (White).
    3.  **Turn Loop:**
          * **Referee Check:** Query Referee for current Winrate ($W_{pre}$).
          * **Agent Move:** Query Agent for move (High Temp).
          * **Blunder Check:** Query Referee for Winrate after move ($W_{post}$).
          * **Trigger:** IF ($W_{pre} > 0.95$ AND $W_{post} < 0.10$):
              * **STOP:** We found a puzzle.
              * **SAVE:** Dump state to JSON.
              * **RESET:** Start new game.
    4.  **Repeat.**

-----

## 6\. Data Output Schema

The consumer application expects strictly formatted JSON files.

**File:** `output/puzzle_{uuid}.json`

```json
{
  "uuid": "puzzle_12345",
  "puzzle_type": "life_and_death_blunder",
  "generated_by": "The_Chameleon",
  "setup_moves": [["B","C3"], ["W","D3"]...],
  "color_to_play": "B", 
  "solution": {
    "correct_move": "E5",
    "referee_winrate": 0.99,
    "difficulty_metrics": {
       "visits_to_solve": 450,
       "policy_prior": 0.02
    }
  },
  "metadata": {
    "ownership": [0.9, 0.9, -0.9...], 
    "score_lead": 15.5
  }
}
```

## 7\. Licensing

All source files must contain the standard **GNU AGPL v3** header.

````

---

### 2. Approach_and_Principles.MD

This file outlines the "Why" and the "Philosophy" driving the system. It is critical for maintaining the project's direction during development.

```markdown
# Approach and Core Principles

## 1. Mission Statement
We are building an autonomous **"Mining Rig"** for Go puzzles. Unlike traditional methods that rely on hand-crafting or random stone placement, we derive puzzles from the **natural tactical collapses** (blunders) that occur in high-temperature AI self-play.

## 2. Core Philosophy

### A. Quantity through Autonomy
The system is designed to run headless and indefinitely. It requires no human input once configured. It is a factory that turns electricity into educational content.

### B. Quality through Adversity (The Blunder Hypothesis)
* **Observation:** Perfectly played games result in "settled" shapes that are boring for Tsumego.
* **Hypothesis:** Interesting puzzles exist in the delta between a "Weak Move" and a "Perfect Response."
* **Method:** We force strong AIs to play "drunkenly" (High Temperature). When they blunder, we freeze time. The puzzle is to find the move the AI *should* have played.

### C. Respect for the Bench
We do not treat Neural Networks as interchangeable scripts. We treat them as a **NetworkBench**—a roster of elite experts with distinct personalities.
* **The Referee:** The cold, hard source of truth.
* **The Chameleon:** A human emulator capable of varied mistakes.
* **The Veteran:** Older architectures (g170) with different blind spots.
* *Note:* Code terminology reflects this respect (`MatchOrchestrator`, `NetworkBench`, `Summoning`).

---

## 3. The Methodology

### Why 9x9?
We generate primarily on **9x9 boards** (active/cropped).
1.  **Density:** 9x9 forces immediate contact fighting. There is no "running away" to a distant center.
2.  **Efficiency:** Games finish in <60 moves.
3.  **Relevance:** A 9x9 board naturally simulates a "Life & Death" problem in the corner of a 19x19 board.

### The "Two-Engine" Architecture
We strictly separate **Generation** from **Validation**.
* **The Generators (Players):** Must be creative, fast, and fallible.
* **The Validator (Referee):** Must be slow, deterministic, and accurate.
* *Why?* If the player validates its own moves, it creates "hallucinated" puzzles where the solution only works because the AI creates a blind spot for itself. The Referee ensures objective truth.

---

## 4. Difficulty Grading
We do not rely on arbitrary human ranks (e.g., "Hard"). We use empirical metrics derived from the Referee:
1.  **The "Blind Spot" Factor (Policy Prior):**
    * If the Policy Network gives the correct move 80% probability → **Easy**.
    * If the Policy Network gives the correct move 2% probability → **Tesugi/Hard**.
2.  **The "Depth" Factor (Visits):**
    * If KataGo solves it in 10 visits → **Easy**.
    * If KataGo needs 500 visits to see the win → **Dan Level**.

**Formula:**
$$Difficulty \approx \frac{Visits\_to\_Solve}{Policy\_Probability}$$

---

## 5. Output Goals
The output is not just an SGF. It is a rich data object containing:
* **The "Why":** Why is the move correct? (Winrate delta).
* **The "What If":** Pre-calculated responses to wrong moves (Policy Tree).
* **The Visuals:** Territory ownership maps to help players visualize dead/alive stones.
````