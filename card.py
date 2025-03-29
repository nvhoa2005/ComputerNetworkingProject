import os
import pygame
from const import *

class Card: 
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.number = self.get_card_number()
        self.texture = pygame.image.load(f"img/{self.number}.png")  
        self.unknown_card_texture = pygame.image.load(f"img/behind.png") 

    def get_card_number(self):
        rank_index = RANKS.index(self.rank)
        suit_index = SUITS.index(self.suit)
        return rank_index * len(SUITS) + suit_index + 1
    
    def set_texture(self, texture):
        self.texture = texture

    def __str__(self):
        return f"{self.rank}{self.suit}"
