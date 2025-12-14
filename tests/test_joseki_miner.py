import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from joseki_miner import JosekiMiner, is_in_top_right_9x9

class TestJosekiMiner(unittest.TestCase):
    def test_coordinate_check(self):
        # Top-Right is Cols J-T (9-18), Rows 11-19
        self.assertTrue(is_in_top_right_9x9("Q16")) # 4-4
        self.assertTrue(is_in_top_right_9x9("R19")) # Top-right corner
        self.assertTrue(is_in_top_right_9x9("J11")) # Bottom-left of the quadrant
        
        self.assertFalse(is_in_top_right_9x9("A1"))  # Bottom-left corner
        self.assertFalse(is_in_top_right_9x9("K10")) # Too low
        self.assertFalse(is_in_top_right_9x9("H15")) # Too left
        self.assertFalse(is_in_top_right_9x9("pass"))

    @patch('joseki_miner.KataGoEngine')
    @patch('joseki_miner.MAX_DEPTH', 2)
    def test_mining_logic(self, MockEngine):
        # Setup Mock
        mock_instance = MockEngine.return_value
        
        # Mock response for Root (Empty board or initial moves)
        # Let's say we are at Q16.
        # Root query returns:
        # - Best move: R16 (winrate 0.5, score 0)
        # - Valid move: F3 (Tenuki, should be ignored)
        # - Valid move: O17 (Local, valid)
        # - Bad move: R17 (Local, but bad winrate)
        
        mock_instance.query.return_value = {
            "rootInfo": {"winrate": 0.5, "scoreLead": 0.0, "visits": 1000},
            "moveInfos": [
                {"move": "R16", "winrate": 0.50, "scoreLead": 0.0, "visits": 500}, # Best
                {"move": "A1",  "winrate": 0.49, "scoreLead": -0.1, "visits": 400}, # Tenuki (ignore)
                {"move": "O17", "winrate": 0.48, "scoreLead": -0.5, "visits": 300}, # Valid
                {"move": "R17", "winrate": 0.30, "scoreLead": -5.0, "visits": 200}, # Bad
            ]
        }
        
        miner = JosekiMiner("dummy_path")
        
        # Test explore
        # History: B Q16
        node = miner.explore([["B", "Q16"]], depth=0)
        
        self.assertIsNotNone(node)
        children = node['children']
        
        # Should have R16 (Best) and O17 (Valid)
        # A1 (Tenuki) and R17 (Bad) should be filtered out
        
        moves = [c['move'] for c in children]
        self.assertIn("R16", moves)
        self.assertIn("O17", moves)
        self.assertNotIn("A1", moves)
        self.assertNotIn("R17", moves)
        
        print("Verified moves:", moves)

if __name__ == '__main__':
    unittest.main()
