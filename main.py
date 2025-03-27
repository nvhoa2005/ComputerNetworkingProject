
import pygame
from const import *
from game import Game

class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()
        self.game = Game()
        self.running = True
        # Các quân bài đã chọn
        self.selected_cards = set()
        # Vị trí các quân bài đã đánh
        self.played_card_positions = [] 
        # Các quân bài đã đánh sẽ di chuyển ra giữa màn hình
        self.center_cards = []

        # Vị trí của nút đánh và bỏ lượt
        self.buttons = {
            0: {"play": pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 310, 100, 50),
                "pass": pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 310, 100, 50)},
            1: {"play": pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 - 50, 80, 40),
                "pass": pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 + 10, 80, 40)},
            2: {"play": pygame.Rect(SCREEN_WIDTH // 2 - 200, 290, 100, 50),
                "pass": pygame.Rect(SCREEN_WIDTH // 2 - 80, 290, 100, 50)},
            3: {"play": pygame.Rect(220, SCREEN_HEIGHT // 2 - 50, 80, 40),
                "pass": pygame.Rect(220, SCREEN_HEIGHT // 2 + 10, 80, 40)}
        }

    def draw_buttons(self):
        for player in range(FOUR_PLAYERS):
            # Vẽ nút khi đến lượt người chơi (dùng để test chương trình)
            if self.game.current_turn == player:
                pygame.draw.rect(self.screen, (0, 255, 0), self.buttons[player]["play"])  
                pygame.draw.rect(self.screen, (255, 0, 0), self.buttons[player]["pass"]) 

                font = pygame.font.Font(None, 30)
                
                # Render text
                text_play = font.render("PLAY", True, (0, 0, 0))
                text_pass = font.render("PASS", True, (0, 0, 0))
                
                # Vị trí của chữ trong các buttons
                play_x = self.buttons[player]["play"].x + (self.buttons[player]["play"].width - text_play.get_width()) // 2
                play_y = self.buttons[player]["play"].y + (self.buttons[player]["play"].height - text_play.get_height()) // 2
                pass_x = self.buttons[player]["pass"].x + (self.buttons[player]["pass"].width - text_pass.get_width()) // 2
                pass_y = self.buttons[player]["pass"].y + (self.buttons[player]["pass"].height - text_pass.get_height()) // 2

                # Vẽ chữ lên nút
                self.screen.blit(text_play, (play_x, play_y))
                self.screen.blit(text_pass, (pass_x, pass_y))

    def draw_cards(self):
        for player, position in PLAYER_POSITIONS.items():
            x, y = position
            num_cards = len(self.game.players[player])
            spacing = min(CARD_OFFSET, (SCREEN_WIDTH // 2 - 100) // max(1, num_cards))

            for i, card in enumerate(self.game.players[player]):
                x_offset, y_offset = (0, 0)
                if (player, i) in self.selected_cards:
                    if player in [0, 2]:  
                        y_offset = -MOVE_OFFSET if player == 0 else MOVE_OFFSET
                    else:  
                        x_offset = -MOVE_OFFSET if player == 1 else MOVE_OFFSET

                # Player 1, 3 xếp hàng ngang
                if player in [0, 2]:
                    self.screen.blit(card.texture, (x + i * spacing + x_offset, y + y_offset))
                # Player 2, 4 xếp hàng dọc
                else:
                    self.screen.blit(card.texture, (x + x_offset, y + i * spacing + y_offset))

        # Bài đã đánh ở giữa màn hình
        center_x, center_y = SCREEN_WIDTH // 2 - (len(self.center_cards) * CARD_OFFSET) // 2, SCREEN_HEIGHT // 2
        for i, card in enumerate(self.center_cards):
            self.screen.blit(card.texture, (center_x + i * CARD_OFFSET, center_y))

    # Xử lý sự kiện click chuột
    def handle_click(self, pos):
        current_player = self.game.current_turn

        # Xử lý bấm nút Play, Pass
        if self.buttons[current_player]["play"].collidepoint(pos):
            self.play_cards(current_player)
            return
        if self.buttons[current_player]["pass"].collidepoint(pos):
            self.game.pass_turn(current_player)
            self.selected_cards.clear()
            return

        for player, position in PLAYER_POSITIONS.items():
            x, y = position

            # Duyệt từ quân bài cuối lên đầu để chọn quân bài trên cùng trước
            for i in range(len(self.game.players[player]) - 1, -1, -1):
                card = self.game.players[player][i]

                # Player 1, 3 xếp ngang
                if player in [0, 2]:
                    card_rect = pygame.Rect(x + i * CARD_OFFSET, y, CARD_WIDTH, CARD_HEIGHT)
                # Player 2, 4 xếp dọc
                else:
                    card_rect = pygame.Rect(x, y + i * CARD_OFFSET, CARD_WIDTH, CARD_HEIGHT)

                if card_rect.collidepoint(pos):
                    card_id = (player, i)
                    if card_id in self.selected_cards:
                        # Bỏ chọn nếu đã chọn
                        self.selected_cards.remove(card_id)
                        print(f"Người chơi {current_player + 1} đã bỏ chọn: {self.game.players[current_player][i]}")
                    else:
                        # Chọn quân bài mới
                        self.selected_cards.add(card_id)
                        print(f"Người chơi {current_player + 1} chọn: {self.game.players[current_player][i]}")
                    # Đã chọn một quân thì thoát vòng lặp (tránh chọn quân dưới)
                    break


    # Hiệu ứng khi đánh bài
    def animate_cards_to_center(self, played_cards):
        target_x, target_y = SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        # Số bước di chuyển
        frames = 15

        for frame in range(frames):
            self.screen.fill((0, 128, 0))
            # Vẽ lại bài không bao gồm bài đang đánh
            self.draw_cards()

            for i, card in enumerate(played_cards):
                x_step = (target_x - self.played_card_positions[i][0]) / frames
                y_step = (target_y - self.played_card_positions[i][1]) / frames
                new_x = self.played_card_positions[i][0] + x_step * frame
                new_y = self.played_card_positions[i][1] + y_step * frame
                self.screen.blit(card.texture, (new_x, new_y))

            pygame.display.flip()
            self.clock.tick(30)

    # Khi người chơi bấm nút đánh
    def play_cards(self, player):
        if self.game.current_turn != player:
            print("Không phải lượt của bạn!")
            return

        # Các quân bài chuẩn bị đánh theo thứ tự từ yếu đến mạnh
        played_cards = sorted(
            [self.game.players[player][i] for _, i in self.selected_cards],
            key=lambda card: (RANK_ORDER[card.rank], SUIT_ORDER[card.suit])
        )
        for i in range(len(played_cards)):
            print(played_cards[i].rank, played_cards[i].suit)

        if self.game.play_cards(player, played_cards):
            # Cập nhật bài đã được đánh di chuyển vào giữa màn hình
            self.center_cards = played_cards

            # Xóa quân bài đã đánh
            for _, i in sorted(self.selected_cards, reverse=True):
                del self.game.players[player][i]
            self.selected_cards.clear()

    def run(self):
        while self.running:
            self.screen.fill((0, 128, 0))
            self.draw_cards()
            self.draw_buttons()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
    GameUI().run()

