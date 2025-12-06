"""
KataGo Engine Wrapper

Manages subprocess communication with KataGo's analysis mode via JSON.

Infinite AI Tsumego Miner
Copyright (C) 2025

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

import subprocess
import json
import sys
import os


class KataGoEngine:
    """
    Wrapper around KataGo's analysis mode.
    
    Handles:
    - Subprocess management
    - JSON-based query/response protocol
    - Override settings for HumanSL model
    """
    
    def __init__(self, katago_path, config_path, model_path, name="Entity"):
        self.name = name
        self.katago_path = katago_path
        self.config_path = config_path
        self.model_path = model_path
        
        self.cmd = [
            katago_path, "analysis",
            "-config", config_path,
            "-model", model_path
        ]
        
        # Validate paths
        if not os.path.exists(katago_path):
            raise FileNotFoundError(f"KataGo binary not found: {katago_path}")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Start the subprocess
        try:
            self.process = subprocess.Popen(
                self.cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not execute KataGo binary at: {katago_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied executing: {katago_path}")
        
        self.query_counter = 0
        self._closed = False
    
    def query(
        self,
        moves_history,
        rules="chinese",
        komi=7.5,
        board_size=9,
        override_settings=None,
        max_visits=None,
    ):
        """
        Send a query to KataGo and wait for the JSON response.
        
        Args:
            moves_history: List of [color, move] pairs, e.g., [["B", "C3"], ["W", "D4"]]
            rules: Ruleset (chinese, japanese, korean, etc.)
            komi: Komi value
            board_size: Board size (default 9 for 9x9)
            override_settings: Dict of settings to override (e.g., humanSLProfile)
            max_visits: Override maxVisits for this query only
        
        Returns:
            Parsed JSON response dict, or None on error.
        """
        if self._closed:
            return None
        
        self.query_counter += 1
        query_id = f"{self.name}_{self.query_counter}"
        
        payload = {
            "id": query_id,
            "moves": moves_history,
            "rules": rules,
            "komi": komi,
            "boardXSize": board_size,
            "boardYSize": board_size,
            "includePolicy": True,
            "includeOwnership": True,
        }
        
        if override_settings:
            payload["overrideSettings"] = override_settings
        
        if max_visits is not None:
            if "overrideSettings" not in payload:
                payload["overrideSettings"] = {}
            payload["overrideSettings"]["maxVisits"] = max_visits
        
        try:
            # Send JSON to KataGo
            json_str = json.dumps(payload)
            self.process.stdin.write(json_str + "\n")
            self.process.stdin.flush()
            
            # Read response (blocking)
            response_line = self.process.stdout.readline()
            
            if not response_line:
                # Check if process died
                if self.process.poll() is not None:
                    err = self.process.stderr.read()
                    raise RuntimeError(f"{self.name} process died. Stderr: {err}")
                return None
            
            response = json.loads(response_line)
            
            # Check for errors in response
            if "error" in response:
                raise RuntimeError(f"{self.name} returned error: {response['error']}")
            
            return response
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error from {self.name}: {e}", file=sys.stderr)
            return None
        except BrokenPipeError:
            print(f"{self.name} pipe broken - process may have crashed", file=sys.stderr)
            self._closed = True
            return None
        except Exception as e:
            print(f"Error querying {self.name}: {e}", file=sys.stderr)
            return None
    
    def is_alive(self):
        """Check if the subprocess is still running."""
        return self.process.poll() is None and not self._closed
    
    def close(self):
        """Gracefully terminate the KataGo process."""
        if self._closed:
            return
        
        self._closed = True
        
        try:
            if self.process.stdin:
                self.process.stdin.close()
            self.process.terminate()
            
            # Wait with timeout
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        except Exception:
            pass  # Best effort cleanup
    
    def __del__(self):
        """Destructor - ensure cleanup."""
        self.close()
    
    def __repr__(self):
        status = "alive" if self.is_alive() else "closed"
        return f"<KataGoEngine '{self.name}' ({status})>"
