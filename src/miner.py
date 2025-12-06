import os
import json
import uuid
import time
from katago_wrapper import KataGoEngine
from network_bench import NetworkBench

# CONSTANTS
KATAGO_BIN = "./assets/katago/katago"
MODEL_REFEREE = "./assets/models/referee.bin.gz"
OUTPUT_DIR = "output"

class MatchOrchestrator:
    def __init__(self): 
        self.bench = NetworkBench()
        self.referee = None
        
    def start(self):
        # 1. Initialize the Bench (Players)
        self.bench.initialize()
        
        # 2. Initialize the Referee (The Judge)
        if not os.path.exists(MODEL_REFEREE):
            print(f"CRITICAL: Referee model missing at {MODEL_REFEREE}")
            return
            
        print(">>> Summoning the High Referee...")
        self.referee = KataGoEngine(
            KATAGO_BIN, "configs/referee_config.cfg", MODEL_REFEREE, name="High_Referee"
        )
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        try:
            self.mining_loop()
        except KeyboardInterrupt:
            print("\n>>> Mining session concluded.")
        finally:
            self.cleanup()

    def mining_loop(self):
        games_played = 0
        puzzles_found = 0
        
        while True:
            # A. Select Contenders
            black_agent, white_agent = self.bench.select_matchup()
            
            # B. Play one game
            found = self.play_match(black_agent, white_agent)
            
            if found:
                puzzles_found += 1
            
            games_played += 1
            if games_played % 10 == 0:
                print(f"--- Status: {games_played} Games Played | {puzzles_found} Puzzles Harvested ---")

    def play_match(self, black_agent, white_agent):
        """
        Simulates a single game. Returns True if a puzzle was found/saved.
        """
        history = [] 
        next_player_color = "B"
        puzzle_found_in_this_game = False
        
        # 9x9 games rarely go beyond 60 moves
        for turn in range(60):
            current_agent = black_agent if next_player_color == "B" else white_agent
            
            # 1. REFEREE CHECK (Before the move)
            # We need to know the 'True' state before the agent potentially messes it up
            referee_analysis = self.referee.query(history)
            if not referee_analysis: break
            
            pre_move_winrate = referee_analysis['rootInfo']['winrate']
            
            # 2. AGENT MOVE
            # Get the agent's specific personality settings
            settings = current_agent.get_query_settings()
            agent_analysis = current_agent.engine.query(history, override_settings=settings)
            
            if not agent_analysis: break
            
            # Pick the move the agent actually wants to play
            try:
                chosen_move = agent_analysis['moveInfos'][0]['move']
            except IndexError:
                break # Resign/Pass
                
            if chosen_move == "pass":
                break

            # 3. BLUNDER DETECTION
            # Create a hypothetical history where this move happened
            hypo_history = history + [[next_player_color, chosen_move]]
            
            # Ask Referee: "Did that just ruin everything?"
            post_move_analysis = self.referee.query(hypo_history)
            post_move_winrate = post_move_analysis['rootInfo']['winrate']
            
            # The Delta: How much did the winrate flip?
            # Perspective: Winrate is always from Black's perspective in KataGo analysis? 
            # Actually KataGo 'rootInfo' winrate usually tracks the current player unless configured.
            # However, simpler logic:
            # If I (Current Player) had a High Winrate, and now the OTHER player has a High Winrate (implied by low winrate for me), it's a blunder.
            
            # Normalized logic assuming winrate is Black's probability:
            wr_start = pre_move_winrate if next_player_color == "B" else (1.0 - pre_move_winrate)
            wr_end = post_move_winrate if next_player_color == "B" else (1.0 - post_move_winrate)
            
            # If I went from > 95% winning to < 10% winning
            if wr_start > 0.95 and wr_end < 0.10:
                print(f" [!] Blunder detected by {current_agent.name}! ({wr_start:.2f} -> {wr_end:.2f})")
                
                # The Puzzle is: Revert the blunder. It is now [next_player_color] to play.
                # Find the move the Referee ORIGINALLY wanted.
                self.save_puzzle(history, next_player_color, referee_analysis, current_agent.name)
                puzzle_found_in_this_game = True
                break # Stop this game, we found the gold
            
            # 4. Advance Game
            history.append([next_player_color, chosen_move])
            next_player_color = "W" if next_player_color == "B" else "B"
            
        return puzzle_found_in_this_game

    def save_puzzle(self, history, color_to_solve, analysis, author_name):
        puzzle_id = str(uuid.uuid4())[:8]
        filename = os.path.join(OUTPUT_DIR, f"puzzle_{puzzle_id}.json")
        
        correct_move = analysis['moveInfos'][0]['move']
        
        data = {
            "uuid": puzzle_id,
            "timestamp": time.time(),
            "generated_by": author_name,
            "puzzle_type": "life_and_death_blunder",
            "setup_moves": history, # The sequence to reach the board state
            "color_to_play": color_to_solve,
            "solution": {
                "correct_move": correct_move,
                "referee_winrate": analysis['rootInfo']['winrate'],
                "referee_visits": analysis['rootInfo']['visits']
            },
            "metadata": {
                "ownership": analysis.get('ownership'),
                "scoreLead": analysis['rootInfo'].get('scoreLead')
            }
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f" >>> Puzzle Saved: {filename}")

    def cleanup(self):
        print(">>> Shutting down engines...")
        self.bench.shutdown()
        if self.referee:
            self.referee.close()

if __name__ == "__main__":
    orchestrator = MatchOrchestrator()
    orchestrator.start()
