"""
Joseki Starting Positions

Defines the standard corner openings to be mined.
Coordinates are for a 19x19 board, focusing on the top-right corner.
Top-Right corner is roughly x >= 10, y <= 8 (0-indexed).
Q16 is the 4-4 point in the top right.
"""

# 19x19 Coordinate mapping (A-T excluding I)
# A B C D E F G H J K  L  M  N  O  P  Q  R  S  T
# 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18

# Top-Right Corner (Q16 area)
# Q16 (4-4) -> x=15, y=3 (if 0,0 is top-left A19? No, usually A1 is bottom-left or top-left depending on system)
# KataGo uses:
#   A1 = bottom-left? Or top-left?
#   Let's stick to the coordinate string format "Q16" which KataGo understands.
#   We will let the wrapper handle conversion if needed, but KataGo usually takes "Q16".

STARTING_POSITIONS = [
    {
        "name": "4-4 Point (Hoshi)",
        "moves": [["B", "Q16"]],
        "description": "The modern standard corner opening."
    },
    {
        "name": "3-4 Point (Komoku)",
        "moves": [["B", "R16"]], # or Q17
        "description": "Territory-oriented corner opening."
    },
    {
        "name": "3-3 Point (San-San)",
        "moves": [["B", "R17"]],
        "description": "Solid territorial corner."
    },
    {
        "name": "5-3 Point (Mokuhazushi)",
        "moves": [["B", "P17"]], # or R15
        "description": "Influence-oriented, often leads to fighting."
    },
    {
        "name": "5-4 Point (Takamoku)",
        "moves": [["B", "P16"]], # or Q15
        "description": "High, influence-oriented move."
    }
]
