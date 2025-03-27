import random
from card import Card
from const import *

class Game:
    
    def __init__(self):
        self.deck = self.createDeck()
        random.shuffle(self.deck)
        self.players = {i: self.deck[i*13:(i+1)*13] for i in range(FOUR_PLAYERS)}
        self.sortCard()
        # Người chơi hiện tại
        self.current_turn = None  
        # Bộ bài vừa được đánh
        self.last_play = None 
        # Những người đã bỏ lượt
        self.passed_players = set()
        # Xác định ai có 3 bích đi trước
        self.find_first_player() 
        self.first_turn = False
    
    def sortCard(self):
        for player in range(FOUR_PLAYERS):
            self.players[player] = sorted(
                self.players[player],
                key=lambda card: (RANK_ORDER[card.rank], SUIT_ORDER[card.suit])
            )
    
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
        # Kiểm tra bài đánh có hợp lệ không
        if not self.is_valid_hand(played_cards):
            return False
        
        # Nếu lượt đánh đầu tiên mà không đánh 3 bích là lỗi
        if not self.first_turn:
            for card in played_cards:
                if card.rank == "3" and card.suit == "♠":
                    self.first_turn = True
                    break
        if not self.first_turn:
            return False
        
        # Nếu là lượt mới, chỉ cần hợp lệ là được
        if not self.last_play:  
            return self.is_valid_hand(played_cards)
        # Kiểm tra bài chuẩn bị đánh có mạnh hơn bài trước đó không
        else:
            return self.compare_hands(self.last_play, played_cards)

    # Kiểm tra bài chuẩn bị đánh có hợp lệ không: đơn, đôi, sảnh, 3 cây, tứ quý, đôi thông
    def is_valid_hand(self, played_cards):
        return self.is_single(played_cards) or self.is_pair(played_cards) or self.is_triple(played_cards) or self.is_quadruple(played_cards) or self.is_straight(played_cards) or self.is_consecutive_pairs(played_cards)
    
    # Kiểm tra có phải quân đơn không
    def is_single(self, played_cards):
        return len(played_cards) == 1
        
    # Kiểm tra có phải đánh đôi không
    def is_pair(self, played_cards):
        return len(played_cards) == 2 and played_cards[0].rank == played_cards[1].rank
    
    # Kiểm tra có phải đánh 3 cây không
    def is_triple(self, played_cards):
        return len(played_cards) == 3 and all(c.rank == played_cards[0].rank for c in played_cards)
    
    # Kiểm tra có phải đánh tứ quý không
    def is_quadruple(self, played_cards):
        return len(played_cards) == 4 and all(c.rank == played_cards[0].rank for c in played_cards)
    
    # Kiểm tra sảnh hợp lệ
    def is_straight(self, played_cards):
        if len(played_cards) < 3:
            return False
        played_ranks = [c.rank for c in played_cards]
        if "2" in played_ranks:
            return False
        return all(RANKS.index(played_ranks[i]) + 1 == RANKS.index(played_ranks[i + 1]) for i in range(len(played_ranks) - 1))

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
        if self.is_single(last_play) and (self.is_quadruple(new_play) or self.is_consecutive_pairs(new_play)):
            if last_play[0].rank == "2":
                return True
            return False
        elif self.is_pair(last_play) and self.is_quadruple(new_play):
            if last_play[0].rank == "2":
                return True
            return False
        elif self.is_pair(last_play) and self.is_consecutive_pairs(new_play):
            if last_play[0].rank == "2" and len(new_play) >= 8:
                return True
            return False
        elif self.is_consecutive_pairs(last_play) and self.is_quadruple(new_play):
            if len(last_play) == 6:
                return True
            return False
        elif self.is_quadruple(last_play) and self.is_consecutive_pairs(new_play):
            if len(new_play) >= 8:
                return True
            return False
        elif self.is_pair(last_play) != self.is_pair(new_play):
            return False
        elif self.is_triple(last_play) != self.is_triple(new_play):
            return False
        elif self.is_quadruple(last_play) != self.is_quadruple(new_play):
            return False
        elif self.is_single(last_play) != self.is_single(new_play):
            return False
        elif self.is_consecutive_pairs(last_play) != self.is_consecutive_pairs(new_play):
            return False
        elif self.is_straight(last_play) != self.is_straight(new_play):
            return False

        last_rank = last_play[len(last_play)-1].rank
        new_rank = new_play[len(new_play)-1].rank

        # So sánh thứ tự quân bài
        if RANK_ORDER[new_rank] > RANK_ORDER[last_rank]:
            return True
        elif new_rank == last_rank:
            # Nếu cùng số, so sánh chất
            return self.compare_suits(last_play[len(last_play)-1], new_play[len(new_play)-1])
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
    