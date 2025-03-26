import random
from card import Card
from const import *

class Game:
    
    def __init__(self):
        self.deck = self.createDeck()
        random.shuffle(self.deck)
        self.players = {i: self.deck[i*13:(i+1)*13] for i in range(FOUR_PLAYERS)}
        # Người chơi hiện tại
        self.current_turn = None  
        # Bộ bài vừa được đánh
        self.last_play = None 
        # Những người đã bỏ lượt
        self.passed_players = set()
        # Xác định ai có 3 bích đi trước
        self.find_first_player() 
    
    def display_hands(self):
        for i in range(FOUR_PLAYERS):
            hand = [f"{card.rank}{card.suit}" for card in self.players[i]]
            print(f"Người chơi {i+1}: {', '.join(hand)}")
    
    def createDeck(self):
        return [Card(suit, rank) for suit in SUITS for rank in RANKS]
    
    # Tìm người có 3 bích đánh trước
    def find_first_player(self):
        for player, cards in self.players.items():
            for card in cards:
                if card.rank == "3" and card.suit == "♠":
                    self.current_turn = player
                    print(f"Người chơi {player + 1} có 3 bích và sẽ đánh trước.")
                    return
    
    # Check bài đánh hợp lệ
    def is_valid_play(self, played_cards):
        if not self.last_play:  
            # Nếu là lượt mới, chỉ cần hợp lệ là được
            return self.is_valid_hand(played_cards)

        # Kiểm tra bài đánh có hợp lệ không
        if not self.is_valid_hand(played_cards):
            return False

        # Kiểm tra bài chuẩn bị đánh có mạnh hơn bài trước đó không
        return self.compare_hands(self.last_play, played_cards)

    # Kiểm tra bài chuẩn bị đánh có hợp lệ không: đơn, đôi, sảnh, 3 cây, tứ quý, đôi thông
    def is_valid_hand(self, played_cards):
        # Đơn
        if len(played_cards) == 1:
            return True
        # Đôi
        elif len(played_cards) == 2 and played_cards[0].rank == played_cards[1].rank:
            return True
        # 3 Cây
        elif len(played_cards) == 3 and all(c.rank == played_cards[0].rank for c in played_cards):
            return True
        # Sảnh
        elif self.is_straight(played_cards):
            return True
        # Tứ quý
        elif len(played_cards) == 4 and all(c.rank == played_cards[0].rank for c in played_cards):
            return True
        # Đôi thông
        elif self.is_consecutive_pairs(played_cards):
            return True
        return False
    
    # Kiểm tra sảnh hợp lệ
    def is_straight(self, played_cards):
        ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        played_ranks = [c.rank for c in played_cards]
        if "2" in played_ranks:
            return False
        return all(ranks.index(played_ranks[i]) + 1 == ranks.index(played_ranks[i + 1]) for i in range(len(played_ranks) - 1))

    # Kiểm tra đôi thông
    def is_consecutive_pairs(self, played_cards):
        # Phải là số chẵn
        if len(played_cards) % 2 != 0:
            return False
        for i in range(0, len(played_cards), 2):
            if played_cards[i].rank != played_cards[i + 1].rank:
                return False
        return self.is_straight(played_cards[0::2])

    # Xem xét bài chuẩn bị đánh có mạnh hơn bài cũ không
    def compare_hands(self, last_play, new_play):
        # Phải cùng loại đánh (đơn, đôi, sảnh, ....)
        if len(last_play) != len(new_play):
            return False

        last_rank = last_play[0].rank
        new_rank = new_play[0].rank

        # So sánh thứ tự quân bài
        ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
        if ranks.index(new_rank) > ranks.index(last_rank):
            return True
        if ranks.index(new_rank) == ranks.index(last_rank):  
            # Nếu cùng số, so sánh chất
            return self.compare_suits(last_play[0], new_play[0])
        return False

    # So sánh chất bài nếu cùng số
    def compare_suits(self, card1, card2):
        return SUIT_ORDER[card2.suit] > SUIT_ORDER[card1.suit]

    # Đánh bài
    def play_cards(self, player, played_cards):
        if player != self.current_turn:
            print("Không phải lượt của bạn")
            return False

        if self.is_valid_play(played_cards):
            self.last_play = played_cards
            # Chuyển lượt
            self.current_turn = (self.current_turn + 1) % 4
            while self.current_turn in self.passed_players:
                self.current_turn = (self.current_turn + 1) % 4
            print(f"Người chơi {player + 1} đánh: {', '.join(str(c) for c in played_cards)}")
            return True
        else:
            print("Bài không hợp lệ!")
            return False

    # Bỏ lượt
    def pass_turn(self, player):
        if player != self.current_turn:
            print("Không phải lượt của bạn!")
            return

        self.passed_players.add(player)
        if len(self.passed_players) == 3:
            # Clear bài cũ
            self.last_play = None 
            # Clear những người đã bỏ qua
            self.passed_players.clear()
            # Clear bài giữa màn hình
            self.center_cards = [] 
            # Next turn
            self.current_turn = (self.current_turn + 1) % 4 
            print("Vòng chơi mới bắt đầu!")
        else:
            # Next turn
            self.current_turn = (self.current_turn + 1) % 4 
            print(f"Người chơi {player + 1} bỏ lượt.")
    