import subprocess
import json
import threading
import time
import sys

class KataGoEngine:
    def __init__(self, katago_path, config_path, model_path, name="Entity"):
        self.name = name
        self.cmd = [
            katago_path, "analysis",
            "-config", config_path,
            "-model", model_path
        ]
        
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
            print(f"CRITICAL: Could not find KataGo binary at {katago_path}")
            sys.exit(1)

        self.query_counter = 0

    def query(self, moves_history, rules="chinese", override_settings=None):
        """
        Sends a query to KataGo and waits for the JSON response.
        """
        self.query_counter += 1
        query_id = f"{self.name}_{self.query_counter}"
        
        payload = {
            "id": query_id,
            "moves": moves_history,
            "rules": rules,
            "boardXSize": 9,
            "boardYSize": 9,
            "includePolicy": True,
            "includeOwnership": True
        }

        if override_settings:
            payload["overrideSettings"] = override_settings
        
        try:
            # Send JSON to KataGo
            json_str = json.dumps(payload)
            self.process.stdin.write(json_str + "\n")
            self.process.stdin.flush()
            
            # Read response (blocking)
            response_line = self.process.stdout.readline()
            if not response_line:
                # Check stderr if process died
                err = self.process.stderr.read()
                raise RuntimeError(f"{self.name} connection died. Error: {err}")
                
            return json.loads(response_line)
        except Exception as e:
            print(f"Error querying {self.name}: {e}")
            return None

    def close(self):
        if self.process:
            self.process.stdin.close()
            self.process.terminate()
            self.process.wait()
