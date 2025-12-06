import os
import random
from katago_wrapper import KataGoEngine

# Paths (Adjust if on Windows)
KATAGO_BIN = "./assets/katago/katago" 
MODEL_HUMAN = "./assets/models/human.bin.gz"
MODEL_VINTAGE = "./assets/models/vintage.bin.gz"

class NeuralAgent:
    def __init__(self, name, engine, is_human_sl=False):
        self.name = name
        self.engine = engine
        self.is_human_sl = is_human_sl

    def get_query_settings(self):
        """Returns the JSON overrides for this agent's specific style/rank."""
        if self.is_human_sl:
            # Randomly pick a rank for this specific move to create variety
            ranks = ["rank_10k", "rank_5k", "rank_1k", "rank_1d", "rank_4d"]
            chosen_rank = random.choice(ranks)
            return {"humanSLProfile": chosen_rank}
        return {}

class NetworkBench:
    """
    A dignified assembly of neural networks available for consultation.
    """
    def __init__(self):
        self.engines = {} # Key: model_type, Value: KataGoEngine instance
        self.roster = []  # List of NeuralAgent objects

    def initialize(self):
        print(">>> Awakening the Machine Spirits...")
        
        # 1. The Chameleon (HumanSL)
        if os.path.exists(MODEL_HUMAN):
            human_engine = KataGoEngine(
                KATAGO_BIN, "configs/player_human.cfg", MODEL_HUMAN, name="HumanSL_Engine"
            )
            self.engines['human_sl'] = human_engine
            # We register this single engine as an agent
            self.roster.append(NeuralAgent("The_Chameleon", human_engine, is_human_sl=True))
            print(" - HumanSL Model: Online")
        else:
            print(f" ! Warning: Human model not found at {MODEL_HUMAN}")

        # 2. The Veteran (Vintage/Standard)
        # Using the vintage model if available, otherwise fall back to a standard one
        if os.path.exists(MODEL_VINTAGE):
            vintage_engine = KataGoEngine(
                KATAGO_BIN, "configs/gen_config.cfg", MODEL_VINTAGE, name="Vintage_Engine"
            )
            self.engines['vintage'] = vintage_engine
            self.roster.append(NeuralAgent("The_Veteran", vintage_engine))
            print(" - Vintage Model: Online")

    def select_matchup(self):
        """Selects two agents from the roster to engage in a match."""
        if len(self.roster) < 1:
            raise RuntimeError("No agents available in the NetworkBench!")
        
        # If we only have one agent, it plays itself
        p1 = random.choice(self.roster)
        p2 = random.choice(self.roster)
        return p1, p2

    def shutdown(self):
        for name, engine in self.engines.items():
            engine.close()
