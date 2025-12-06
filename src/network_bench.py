"""
NetworkBench: A dignified assembly of neural networks available for consultation.

This module manages the roster of available neural agents (players) and provides
matchmaking functionality for adversarial self-play.

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


def weighted_rank_choice():
    """Select a rank based on weighted distribution."""
    ranks = list(HUMAN_RANK_WEIGHTS.keys())
    weights = list(HUMAN_RANK_WEIGHTS.values())
    return random.choices(ranks, weights=weights, k=1)[0]


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
    
    def get_query_settings(self):
        """
        Returns the JSON overrides for this agent's specific style/rank.
        For HumanSL, randomly selects a rank to create variety.
        """
        if self.is_human_sl:
            chosen_rank = weighted_rank_choice()
            return {"humanSLProfile": chosen_rank}
        return {}
    
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
    
    Manages model discovery, engine initialization, and matchmaking.
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
        Selects two agents from the roster to engage in a match.
        
        Returns:
            Tuple of (black_agent, white_agent)
        """
        if len(self.roster) < 1:
            raise RuntimeError("No agents available in the NetworkBench!")
        
        # If we only have one agent, it plays itself
        p1 = random.choice(self.roster)
        p2 = random.choice(self.roster)
        
        # Record games
        p1.record_game()
        if p1 != p2:
            p2.record_game()
        
        return p1, p2
    
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
    # Test the NetworkBench
    from logger import setup_logging
    import logging
    
    setup_logging(level=logging.DEBUG)
    
    bench = NetworkBench()
    bench.initialize()
    
    print("\n=== Available Agents ===")
    for agent in bench.roster:
        print(f"  {agent}")
    
    print("\n=== Test Matchup ===")
    if bench.roster:
        b, w = bench.select_matchup()
        print(f"  Black: {b.alias}")
        print(f"  White: {w.alias}")
    
    bench.shutdown()
