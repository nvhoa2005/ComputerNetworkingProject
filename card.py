import pygame
from const import *

class Card: 
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.number = self.get_card_number()
        self.texture = None
        self.unknown_card_texture = None

    def get_card_number(self):
        rank_index = RANKS.index(self.rank)
        suit_index = SUITS.index(self.suit)
        return rank_index * len(SUITS) + suit_index + 1
    
    def set_texture(self, texture):
        self.texture = texture

    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    # Do pickle không thể gửi python.surface.Surface
    def serialize(self):
        """Chuyển đối tượng Card thành dictionary có thể gửi qua mạng"""
        return {
            "suit": self.suit,
            "rank": self.rank,
            "number": self.number
        }

    @staticmethod
    def deserialize(data):
        """Chuyển dictionary về đối tượng Card"""
        return Card(data["suit"], data["rank"])
