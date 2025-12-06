"""
Logging configuration for Infinite AI Tsumego Miner

Provides structured logging with timestamps, severity levels, and optional
file output for production mining runs.

Infinite AI Tsumego Miner
Copyright (C) 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import logging
import sys
import os
from datetime import datetime


def setup_logging(
    level=logging.INFO,
    log_to_file=False,
    log_dir="logs",
    log_prefix="miner"
):
    """
    Configure the logging system for the miner.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: If True, also write logs to a file
        log_dir: Directory for log files
        log_prefix: Prefix for log filenames
    
    Returns:
        The configured logger instance
    """
    # Create logger
    logger = logging.getLogger("TsumegoMiner")
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_formatter = logging.Formatter(
        "%(levelname)-8s | %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_dir, f"{log_prefix}_{timestamp}.log")
        
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_filename}")
    
    return logger


def get_logger(name=None):
    """
    Get a logger instance. If name is provided, returns a child logger.
    
    Args:
        name: Optional name for a child logger (e.g., "NetworkBench")
    
    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"TsumegoMiner.{name}")
    return logging.getLogger("TsumegoMiner")


# Convenience functions for common log patterns
class MiningLogger:
    """Structured logging helper for mining operations."""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger()
        self.games_played = 0
        self.puzzles_found = 0
    
    def engine_startup(self, name, model_alias):
        """Log engine initialization."""
        self.logger.info(f"Engine [{name}] initialized with model: {model_alias}")
    
    def match_start(self, black_alias, white_alias, game_num):
        """Log start of a new match."""
        self.logger.debug(f"Game #{game_num}: {black_alias} (B) vs {white_alias} (W)")
    
    def blunder_detected(self, agent_alias, wr_before, wr_after, move):
        """Log blunder detection."""
        drop = (wr_before - wr_after) * 100
        self.logger.warning(
            f"BLUNDER by {agent_alias}: {wr_before:.1%} → {wr_after:.1%} "
            f"(Δ{drop:.0f}%) after move {move}"
        )
    
    def puzzle_saved(self, puzzle_id, filepath):
        """Log puzzle save."""
        self.puzzles_found += 1
        self.logger.info(f"Puzzle #{self.puzzles_found} saved: {puzzle_id} → {filepath}")
    
    def status_update(self, games, puzzles, rate=None):
        """Log periodic status."""
        self.games_played = games
        self.puzzles_found = puzzles
        msg = f"Status: {games} games | {puzzles} puzzles"
        if rate:
            msg += f" | {rate:.1f} puzzles/hour"
        self.logger.info(msg)
    
    def engine_error(self, name, error):
        """Log engine errors."""
        self.logger.error(f"Engine [{name}] error: {error}")
    
    def shutdown(self):
        """Log shutdown."""
        self.logger.info(
            f"Mining session ended. Total: {self.games_played} games, "
            f"{self.puzzles_found} puzzles harvested."
        )
