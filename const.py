# Game name
GAME_NAME = "TIẾN LÊN MIỀN NAM"

# Screen
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

# Suits
HEARTS = "HEARTS"
DIAMONDS = "DIAMONDS"
CLUBS = "CLUBS"
SPADES = "SPADES"

# Number of players
TWO_PLAYERS = 2
THREE_PLAYERS = 3
FOUR_PLAYERS = 4

# Player positions
PLAYER_POSITIONS = { 
    0: (SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT - 250),
    1: (SCREEN_WIDTH - 270, SCREEN_HEIGHT // 2 - 400),
    2: (SCREEN_WIDTH // 2 - 400, 50),
    3: (70, SCREEN_HEIGHT // 2 - 400)
}

# Rank, suit
RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
SUITS = ['♠', '♣', '♦', '♥'] 

# Card distance
CARD_WIDTH = 133
CARD_HEIGHT = 200
CARD_OFFSET = 50
MOVE_OFFSET = 50

# order
RANK_ORDER = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4, '8': 5, '9': 6, '10': 7,
            'J': 8, 'Q': 9, 'K': 10, 'A': 11, '2': 12}
SUIT_ORDER = {'♠': 0, '♣': 1, '♦': 2, '♥': 3}

# time each turn
TIME_EACH_TURN = 2000