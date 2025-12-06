# Neural Network Models

To run the miner, you must download the following neural network weights and place them in this directory (`assets/models/`).

## 1. The High Referee (Required)
**Role:** The absolute source of truth. Judges board states with zero temperature.
*   **File:** `referee.bin.gz`
*   **Source:** [KataGo Training (Latest b18)](https://katagotraining.org/)
*   **Identification:** Look for the strongest available network (e.g., `kata1-b18c384nbt...`). currently using `STR_CONF_RTD...b28`.

## 2. The Chameleon (Required for "Human" play)
**Role:** Simulates human-like intuition and errors across rank levels (10k - 9d).
*   **File:** `human.bin.gz`
*   **Source:** [KataGo Supported Models - HumanSL](https://github.com/lightvector/KataGo/blob/master/docs/SupportedModels.md)
*   **Identification:** Look for `humanv0` (e.g., `b18c384nbt-humanv0.bin.gz`).

## 3. The Veteran (Optional/Variety)
**Role:** Older, lightweight networks that produce "computer-style" blind spots different from modern nets.
*   **File:** `vintage.bin.gz`
*   **Source:** [KataGo Training Archives](https://katagotraining.org/networks/)
*   **Identification:** Look for `g170` (15-block) or `b6c96` (6-block) runs from 2019/2020. They are often `.txt.gz` or `.bin.gz`.
