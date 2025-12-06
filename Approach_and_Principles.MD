# Approach and Core Principles

> **"We do not build the puzzles; we mine them from the chaos of high-temperature logic."**

## 1. Mission Statement
We are building an autonomous **"Mining Rig"** for Go puzzles. Unlike traditional methods that rely on hand-crafting or random stone placement, we derive infinite, high-quality tsumego from the **natural tactical collapses** (blunders) that occur in adversarial AI self-play.

## 2. Core Philosophy

### A. Quantity through Autonomy
The system is designed to run headless and indefinitely. It requires no human input once configured. It is a factory that turns electricity and GPU cycles into educational content.

### B. Quality through Adversity (The Blunder Hypothesis)
* **Observation:** Perfectly played games result in "settled" shapes that are boring for Tsumego.
* **Hypothesis:** Interesting puzzles exist specifically in the delta between a "Weak Move" and a "Perfect Response."
* **Method:** We force strong AIs to play "drunkenly" (High Temperature). When they blunder, we freeze time. The puzzle is to find the move the AI *should* have played to punish that mistake.

### C. Respect for the Bench (The "Machine Spirits")
We do not treat Neural Networks as interchangeable tools. We treat them as a **NetworkBench**—a roster of elite experts with distinct personalities and blind spots.
* **The High Referee (Latest b18):** The cold, hard source of truth. It never plays; it only judges.
* **The Chameleon (HumanSL):** A flexible actor capable of emulating human errors (18k to 9d).
* **The Veteran (g170):** Older architectures with distinct "computer-style" blind spots.

*Terminology used in code reflects this respect (`MatchOrchestrator`, `Summoning`, `NetworkBench`).*

---

## 3. The Methodology

### Why 9x9?
We generate primarily on **9x9 boards** (or active crops of larger boards).
1.  **Density:** 9x9 forces immediate contact fighting. There is no "running away" to a distant center.
2.  **Efficiency:** Games finish in <60 moves, maximizing puzzle throughput.
3.  **Relevance:** A 9x9 board naturally simulates a "Life & Death" problem in the corner of a 19x19 board.

### The "Dual-Engine" Architecture
We strictly separate **Generation** from **Validation**.
* **The Generators (The Players):** Configured for creativity, speed, and fallibility (`temp=1.25`, `visits=50`).
* **The Validator (The Referee):** Configured for absolute rigor (`temp=0`, `visits=600+`).
* **Reasoning:** If a player validates its own moves, it creates "hallucinated" puzzles where the solution only works because the AI has a blind spot. The Referee ensures objective truth.

---

## 4. Difficulty Grading & Metrics
We do not rely on arbitrary human ranks. We use empirical metrics derived from the Referee's neural topography.

### A. The "Blind Spot" Factor (Policy Prior)
How obvious is the move to a trained intuition?
* **High Policy (e.g., > 80%):** The move is "shape." Even a beginner sees it. -> **Easy/Medium**.
* **Low Policy (e.g., < 2%):** The move is ugly or counter-intuitive. -> **Hard (Tesugi)**.

### B. The "Depth" Factor (Visits to Solve)
How much calculation is required to verify the move works?
* **Instant Solve (< 50 visits):** The result is clear immediately.
* **Deep Read (> 500 visits):** The engine initially thinks the move fails, but changes its mind after deep reading. -> **Very Hard (Dan Level)**.

**Grading Formula:**
$$Difficulty \propto \frac{\text{Visits to Solve}}{\text{Policy Probability}}$$

---

## 5. Output Standards
The output is not just an SGF. It is a rich data object designed for an interactive frontend.
* **The "Why":** The Winrate Delta (e.g., "This move caused a 90% drop in win probability").
* **The "What If":** Pre-calculated responses to incorrect moves (Policy Tree).
* **The Visuals:** Territory ownership maps included in metadata to help players visualize dead/alive stones without playing it out.