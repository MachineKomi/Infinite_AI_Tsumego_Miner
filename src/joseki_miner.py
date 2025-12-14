"""
Joseki Miner

Explores and maps out valid Joseki sequences for 9x9 corner views.
"""

import os
import json
import time
import argparse
from datetime import datetime
from copy import deepcopy

from katago_wrapper import KataGoEngine
from joseki_definitions import STARTING_POSITIONS
from logger import setup_logging, get_logger

# =============================================================================
# CONSTANTS
# =============================================================================

if os.name == 'nt':
    KATAGO_BIN = "./assets/katago/katago.exe"
else:
    KATAGO_BIN = "./assets/katago/katago"

# We need a strong model for analysis
MODELS_DIR = "./assets/models"
OUTPUT_DIR = "output/joseki"

# Mining Parameters
BOARD_SIZE = 19
CORNER_SIZE = 9  # We only care about moves within this distance of the corner
WINRATE_TOLERANCE = 0.05  # Moves within 5% of best move are valid
SCORE_TOLERANCE = 2.0     # Moves within 2 points of best move are valid
MIN_VISITS = 50           # Minimum visits to consider a move "read" enough
MAX_DEPTH = 30            # Maximum depth of the tree to prevent infinite loops

# Top-Right Corner Definition (19x19)
# We define the "9x9 view" as the top-right 9x9 quadrant.
# X: 10-18 (K-T), Y: 0-8 (19-11)
# Note: KataGo coordinates are 0-indexed.
# If we assume standard orientation (A1 top-left or bottom-left? KataGo is usually A1 bottom-left).
# Let's rely on the coordinate strings for checking.
# Columns: A B C D E F G H J K L M N O P Q R S T (0-18)
# Rows: 1-19
# Top-Right is Q16 area.
# So Columns J-T (indices 9-18)
# Rows 11-19 (indices 10-18) -> Wait, if 1 is bottom, 19 is top.
# Let's verify KataGo coords. usually 0,0 is top-left in internal arrays, but GTP/SGF is bottom-left.
# KataGo wrapper takes "Q16".
# We need a helper to check if a move string is in the top-right 9x9.

COL_MAP = "ABCDEFGHJKLMNOPQRST"

def is_in_top_right_9x9(move_str):
    """
    Checks if a move (e.g., 'Q16') is in the top-right 9x9 corner.
    Top-Right: Cols J-T, Rows 11-19.
    """
    if not move_str or move_str.lower() == "pass":
        return False
        
    col_char = move_str[0].upper()
    try:
        row_num = int(move_str[1:])
    except ValueError:
        return False
        
    # Check Column (J-T)
    if col_char not in "JKLMNOPQRST":
        return False
        
    # Check Row (11-19)
    if not (11 <= row_num <= 19):
        return False
        
    return True

class JosekiMiner:
    def __init__(self, model_path, config_path="configs/referee_config.cfg"):
        self.logger = get_logger("JosekiMiner")
        self.engine = KataGoEngine(KATAGO_BIN, config_path, model_path, name="Miner")
        self.visited_positions = set()
        
    def mine_all(self):
        """Mine all defined starting positions."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        for pos_def in STARTING_POSITIONS:
            self.logger.info(f"Starting mining for: {pos_def['name']}")
            result = self.mine_position(pos_def)
            
            # Save result
            filename = f"{pos_def['name'].replace(' ', '_').lower()}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w") as f:
                json.dump(result, f, indent=2)
            self.logger.info(f"Saved to {filepath}")

    def mine_position(self, pos_def):
        """Mine a specific starting position."""
        root_moves = pos_def['moves']
        
        # Build the tree
        tree = self.explore(root_moves, depth=0)
        
        return {
            "name": pos_def['name'],
            "description": pos_def['description'],
            "root_moves": root_moves,
            "tree": tree
        }

    def explore(self, history, depth):
        """
        Recursively explore the game tree.
        Returns a node dictionary.
        """
        if depth >= MAX_DEPTH:
            return {"status": "max_depth_reached"}

        # Query KataGo
        # We need a decent number of visits to get reliable alternative moves
        analysis = self.engine.query(history, board_size=BOARD_SIZE, max_visits=500)
        
        if not analysis:
            self.logger.error("Engine query failed")
            return None

        root_info = analysis['rootInfo']
        move_infos = analysis.get('moveInfos', [])
        
        if not move_infos:
            return {"status": "no_moves"}

        best_winrate = move_infos[0]['winrate']
        best_score = move_infos[0]['scoreLead']
        
        current_node = {
            "winrate": round(root_info['winrate'], 4),
            "score": round(root_info.get('scoreLead', 0), 2),
            "visits": root_info['visits'],
            "children": []
        }
        
        # Identify valid moves
        valid_moves = []
        for info in move_infos:
            move = info['move']
            winrate = info['winrate']
            score = info['scoreLead']
            visits = info['visits']
            
            # 1. Check Tenuki (must be in top-right 9x9)
            if not is_in_top_right_9x9(move):
                continue
                
            # 2. Check Validity Tolerance
            # Allow if winrate is close OR score is close
            # (Sometimes score loss is small but winrate drops, or vice versa)
            # But usually we want AND/OR logic. Let's be generous:
            # If winrate drop is small AND score drop is small.
            
            # Note: Winrate is for the player moving.
            # If best is 0.60, and this is 0.56, diff is 0.04 -> OK.
            
            winrate_diff = best_winrate - winrate
            score_diff = abs(best_score - score) # Absolute diff might be wrong if sign changes?
            # Actually, scoreLead is from perspective of player to move.
            # Higher is better. So best_score should be >= score.
            score_drop = best_score - score
            
            if winrate_diff <= WINRATE_TOLERANCE and score_drop <= SCORE_TOLERANCE:
                if visits >= MIN_VISITS:
                    valid_moves.append(info)
        
        # Recursively explore valid moves
        for move_info in valid_moves:
            move_str = move_info['move']
            
            # Determine next color
            # history is list of [color, move]
            if not history:
                next_color = "B" # Should not happen if we have root moves
            else:
                last_color = history[-1][0]
                next_color = "W" if last_color == "B" else "B"
            
            new_history = history + [[next_color, move_str]]
            
            # Recurse
            child_tree = self.explore(new_history, depth + 1)
            
            child_node = {
                "move": move_str,
                "winrate": round(move_info['winrate'], 4),
                "score": round(move_info['scoreLead'], 2),
                "visits": move_info['visits'],
                "continuation": child_tree
            }
            current_node["children"].append(child_node)
            
        return current_node

def main():
    parser = argparse.ArgumentParser(description="Joseki Miner")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    
    level = "DEBUG" if args.debug else "INFO"
    setup_logging(level=level)
    
    # Find model
    from model_registry import find_referee_model
    model_path = find_referee_model(MODELS_DIR)
    if not model_path:
        print("No model found in assets/models")
        return

    miner = JosekiMiner(model_path)
    miner.mine_all()

if __name__ == "__main__":
    main()
