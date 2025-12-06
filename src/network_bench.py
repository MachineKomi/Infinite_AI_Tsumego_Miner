"""
NetworkBench: A dignified assembly of neural networks available for consultation.

This module manages the roster of available neural agents (players) and provides
matchmaking functionality with randomized strength/style parameters.

Infinite AI Tsumego Miner
Copyright (C) 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import os
import random
from katago_wrapper import KataGoEngine
from model_registry import (
    MODEL_REGISTRY,
    get_model_info,
    get_alias,
    scan_models_directory,
    find_player_models,
    VALID_HUMAN_SL_PROFILES,
)
from logger import get_logger

# =============================================================================
# PATHS
# =============================================================================

if os.name == 'nt':
    KATAGO_BIN = "./assets/katago/katago.exe"
else:
    KATAGO_BIN = "./assets/katago/katago"

MODELS_DIR = "./assets/models"

# =============================================================================
# STYLE RANDOMIZATION PARAMETERS
# These ranges define the "personality variance" for each match
# =============================================================================

# Temperature controls how "creative" vs "optimal" the agent plays
# Higher = more variety/mistakes, Lower = more accurate
TEMPERATURE_RANGE = {
    "conservative": (0.8, 1.0),   # Play more accurately
    "balanced": (1.0, 1.15),      # Normal creative play
    "creative": (1.15, 1.3),      # Very exploratory
    "chaotic": (1.3, 1.5),        # Maximum variety
}

# Visit count affects reading depth (and thus strength)
# Lower visits = more intuitive/weaker, Higher = stronger
VISITS_RANGE = {
    "intuitive": (20, 40),        # Quick intuition, many mistakes
    "casual": (40, 80),           # Light reading
    "thoughtful": (80, 150),      # Moderate analysis
    "deep": (150, 300),           # Deep reading (slower)
}

# Weighted distributions for random selection
TEMPERATURE_WEIGHTS = {
    "conservative": 10,
    "balanced": 40,
    "creative": 35,
    "chaotic": 15,
}

VISITS_WEIGHTS = {
    "intuitive": 25,
    "casual": 40,
    "thoughtful": 25,
    "deep": 10,
}

# =============================================================================
# HUMAN SL RANK DISTRIBUTION
# Weighted distribution for human rank emulation
# =============================================================================

HUMAN_RANK_WEIGHTS = {
    # SDK ranks - common, produce good mistakes
    "rank_10k": 15,
    "rank_8k": 15,
    "rank_5k": 20,
    "rank_3k": 15,
    "rank_1k": 10,
    # Dan ranks - rarer, more subtle mistakes
    "rank_1d": 8,
    "rank_2d": 6,
    "rank_3d": 5,
    "rank_4d": 3,
    "rank_5d": 2,
    "rank_6d": 1,
}


def weighted_choice(options_dict):
    """Select from a weighted dictionary."""
    options = list(options_dict.keys())
    weights = list(options_dict.values())
    return random.choices(options, weights=weights, k=1)[0]


def weighted_rank_choice():
    """Select a rank based on weighted distribution."""
    return weighted_choice(HUMAN_RANK_WEIGHTS)


def random_temperature():
    """Select a random temperature from weighted style categories."""
    style = weighted_choice(TEMPERATURE_WEIGHTS)
    low, high = TEMPERATURE_RANGE[style]
    temp = random.uniform(low, high)
    return round(temp, 2), style


def random_visits():
    """Select a random visit count from weighted depth categories."""
    depth = weighted_choice(VISITS_WEIGHTS)
    low, high = VISITS_RANGE[depth]
    visits = random.randint(low, high)
    return visits, depth


# =============================================================================
# PERSONALITY PROFILE
# =============================================================================

class PersonalityProfile:
    """
    Represents the randomized "mood" of an agent for a particular game.
    Generated fresh for each match to create variety.
    """
    
    def __init__(self, agent_alias, is_human_sl=False):
        self.agent_alias = agent_alias
        self.is_human_sl = is_human_sl
        
        # Randomize temperature
        self.temperature, self.temp_style = random_temperature()
        
        # Randomize visits
        self.max_visits, self.depth_style = random_visits()
        
        # HumanSL rank (only used for HumanSL models)
        self.human_rank = weighted_rank_choice() if is_human_sl else None
    
    def to_override_settings(self):
        """
        Convert this profile to KataGo override settings.
        """
        settings = {
            "chosenMoveTemperature": self.temperature,
            "maxVisits": self.max_visits,
        }
        
        if self.is_human_sl and self.human_rank:
            settings["humanSLProfile"] = self.human_rank
        
        return settings
    
    def describe(self):
        """Human-readable description of this personality."""
        parts = [f"temp={self.temperature} ({self.temp_style})",
                 f"visits={self.max_visits} ({self.depth_style})"]
        if self.human_rank:
            parts.append(f"rank={self.human_rank}")
        return ", ".join(parts)
    
    def __repr__(self):
        return f"<Personality {self.agent_alias}: {self.describe()}>"


# =============================================================================
# NEURAL AGENT CLASS
# =============================================================================

class NeuralAgent:
    """
    Represents a single neural network "personality" available for games.
    """
    
    def __init__(self, alias, engine, model_info, is_human_sl=False):
        self.alias = alias
        self.name = alias  # For backward compatibility
        self.engine = engine
        self.model_info = model_info
        self.is_human_sl = is_human_sl
        self.games_played = 0
        self.blunders_made = 0
        
        # Current personality (generated per-match)
        self.current_personality = None
    
    def generate_personality(self):
        """
        Generate a fresh randomized personality for a new match.
        Call this at the start of each game.
        """
        self.current_personality = PersonalityProfile(
            self.alias,
            is_human_sl=self.is_human_sl
        )
        return self.current_personality
    
    def get_query_settings(self):
        """
        Returns the JSON overrides for this agent's current personality.
        If no personality is set, generates one.
        """
        if self.current_personality is None:
            self.generate_personality()
        
        return self.current_personality.to_override_settings()
    
    def record_blunder(self):
        """Record that this agent made a blunder."""
        self.blunders_made += 1
    
    def record_game(self):
        """Record that this agent played a game."""
        self.games_played += 1
    
    def __repr__(self):
        elo = self.model_info.get("elo", "N/A")
        return f"<NeuralAgent '{self.alias}' (ELO: {elo})>"


# =============================================================================
# NETWORK BENCH CLASS
# =============================================================================

class NetworkBench:
    """
    A dignified assembly of neural networks available for consultation.
    
    Manages model discovery, engine initialization, and matchmaking
    with randomized strength/style parameters.
    """
    
    def __init__(self, models_dir=MODELS_DIR, katago_bin=KATAGO_BIN):
        self.models_dir = models_dir
        self.katago_bin = katago_bin
        self.engines = {}  # Key: alias, Value: KataGoEngine instance
        self.roster = []   # List of NeuralAgent objects
        self.logger = get_logger("NetworkBench")
    
    def initialize(self):
        """
        Scan the models directory and initialize available player agents.
        """
        self.logger.info(">>> Awakening the Machine Spirits...")
        
        if not os.path.exists(self.katago_bin):
            self.logger.error(f"KataGo binary not found at: {self.katago_bin}")
            raise FileNotFoundError(f"KataGo binary not found: {self.katago_bin}")
        
        # Scan for available models
        available_models = scan_models_directory(self.models_dir)
        
        if not available_models:
            self.logger.warning(f"No models found in {self.models_dir}")
            return
        
        # Initialize each player model (skip referee - that's handled separately)
        for model in available_models:
            if model.get("role") == "referee":
                continue  # Referee is initialized by MatchOrchestrator
            
            filepath = model["filepath"]
            alias = model.get("alias", model["filename"])
            is_human_sl = model.get("is_human_sl", False)
            
            # Choose appropriate config
            if is_human_sl:
                config = "configs/player_human.cfg"
            else:
                config = "configs/gen_config.cfg"
            
            try:
                engine = KataGoEngine(
                    self.katago_bin,
                    config,
                    filepath,
                    name=alias
                )
                
                self.engines[alias] = engine
                agent = NeuralAgent(alias, engine, model, is_human_sl=is_human_sl)
                self.roster.append(agent)
                
                elo_str = f"ELO {model.get('elo')}" if model.get('elo') else "Specialized"
                self.logger.info(f"  + {alias:20} | {elo_str} | {model['architecture']}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {alias}: {e}")
        
        self.logger.info(f">>> NetworkBench ready: {len(self.roster)} agents online")
    
    def select_matchup(self):
        """
        Selects two agents from the roster and generates fresh personalities.
        
        This implements the "arena" concept:
        1. Randomly select Black and White players from the roster
        2. Generate randomized strength/style for each player
        
        Returns:
            Tuple of (black_agent, white_agent)
        """
        if len(self.roster) < 1:
            raise RuntimeError("No agents available in the NetworkBench!")
        
        # Randomly select players
        black = random.choice(self.roster)
        white = random.choice(self.roster)
        
        # Generate fresh personalities for this match
        black_personality = black.generate_personality()
        white_personality = white.generate_personality()
        
        # Log the matchup with personalities
        self.logger.debug(
            f"Matchup: {black.alias} (B) vs {white.alias} (W)"
        )
        self.logger.debug(f"  Black: {black_personality.describe()}")
        self.logger.debug(f"  White: {white_personality.describe()}")
        
        # Record games
        black.record_game()
        if black != white:
            white.record_game()
        
        return black, white
    
    def get_agent_by_alias(self, alias):
        """Get a specific agent by alias."""
        for agent in self.roster:
            if agent.alias == alias:
                return agent
        return None
    
    def get_available_aliases(self):
        """Return list of all available agent aliases."""
        return [agent.alias for agent in self.roster]
    
    def get_stats(self):
        """Get statistics about all agents."""
        return {
            agent.alias: {
                "games": agent.games_played,
                "blunders": agent.blunders_made,
                "elo": agent.model_info.get("elo"),
            }
            for agent in self.roster
        }
    
    def shutdown(self):
        """Gracefully shut down all engines."""
        self.logger.info("Shutting down NetworkBench engines...")
        for alias, engine in self.engines.items():
            try:
                engine.close()
                self.logger.debug(f"  - {alias}: closed")
            except Exception as e:
                self.logger.error(f"  - {alias}: error during shutdown: {e}")


if __name__ == "__main__":
    # Test the NetworkBench with personality generation
    from logger import setup_logging
    import logging
    
    setup_logging(level=logging.DEBUG)
    
    print("=== Personality Profile Test ===")
    for _ in range(5):
        profile = PersonalityProfile("TestAgent", is_human_sl=True)
        print(f"  {profile.describe()}")
        print(f"    -> {profile.to_override_settings()}")
    
    print("\n=== NetworkBench Test ===")
    bench = NetworkBench()
    bench.initialize()
    
    if bench.roster:
        print(f"\n=== Test Matchups ===")
        for i in range(3):
            b, w = bench.select_matchup()
            print(f"  Game {i+1}: {b.alias} vs {w.alias}")
            print(f"    Black: {b.current_personality.describe()}")
            print(f"    White: {w.current_personality.describe()}")
    
    bench.shutdown()
