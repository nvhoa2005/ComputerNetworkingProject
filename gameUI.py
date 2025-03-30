
import pygame
from const import *
from game import Game
from networking import Network
import threading
import math
import select
import pickle

class GameUI:
    def __init__(self, cards):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()
        self.game = Game(cards)
        self.running = True
        # Các quân bài đã chọn
        self.selected_cards = set()
        # Vị trí các quân bài đã đánh
        self.played_card_positions = [] 
        # Các quân bài đã đánh sẽ di chuyển ra giữa màn hình
        self.center_cards = []
        # action trong mỗi lượt của từng player
        self.action = None

        # Thời gian giới hạn và bộ đếm thời gian
        self.turn_time_limit = TIME_EACH_TURN
        self.start_time = pygame.time.get_ticks()

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
        
        # Kết nối
        self.network = Network()
        self.network.connect()
        
        # player id
        print(self.network.id)
        self.player = int(self.network.id)
        
        # Tạo luồng lắng nghe dữ liệu từ server
        threading.Thread(target=self.network.receive, args=(self.handle_update,), daemon=True).start()
        self.lock = threading.Lock()
    
    # Nhận được dữ liệu từ server
    def handle_update(self, data):
        print("Dữ liệu nhận được từ server: ", data)
        if (isinstance(data, dict)) and data.get("game_started"):  
            return
        if len(data) == 0:
            print("Người chơi trước đó bỏ lượt")
            self.game.pass_turn(self.game.current_turn)
            self.start_time = pygame.time.get_ticks()
            self.selected_cards.clear()
        elif len(data) <= 13:
            print("Người chơi trước đó đánh")
            print(data, len(data))
            self.selected_cards = set(data)
            self.play_cards(self.game.current_turn, from_server=True)
        print(f"Đây là lượt của người chơi {self.game.current_turn + 1}")
    
    # Vòng tròn đếm thời gian 
    def draw_timer_circle(self, player):
        time_passed = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining_time = max(0, self.turn_time_limit - time_passed)
        
        # Góc xoay theo thời gian (360 độ trong 10s)
        angle = (remaining_time / self.turn_time_limit) * 360 + 90
        
        # Vị trí của vòng tròn thời gian
        if player == 0:
            x, y = (SCREEN_WIDTH - 450, SCREEN_HEIGHT - 150)
        elif player == 1:
            x, y = (SCREEN_WIDTH - 320, 50)
        elif player == 2:
            x, y = (300, 100)
        elif player == 3:
            x, y = (270, SCREEN_HEIGHT - 200)
        
        if player in [0, 2]:
            x += 50
        else:
            y += 50
        
        pygame.draw.circle(self.screen, (255, 231, 215), (x, y), 40, 5)
        end_x = x + 40 * math.cos(math.radians(-angle))
        end_y = y + 40 * math.sin(math.radians(-angle))
        pygame.draw.line(self.screen, (158, 0, 24), (x, y), (end_x, end_y), 5)
        
    # Kiểm tra thời gian nếu lượt mới thì đánh quân bất kỳ còn lại thì bỏ qua
    def update_turn_timer(self):
        time_passed = (pygame.time.get_ticks() - self.start_time) / 1000
        if time_passed >= self.turn_time_limit:
            if self.game.last_play:
                self.game.pass_turn(self.game.current_turn)
                # gửi gói tin
                self.action = list(self.selected_cards)
                self.network.send(self.action)
                self.action.clear()
                self.start_time = pygame.time.get_ticks()
                print(f"Đây là lượt của người chơi: {self.game.current_turn + 1}")
            else:
                current_player = self.game.current_turn
                player_hand = self.game.players[current_player]
                if player_hand:
                    # Chọn quân bài nhỏ nhất để đánh
                    chosen_card = min(player_hand, key=lambda card: (RANK_ORDER[card.rank], SUIT_ORDER[card.suit]))
                    card_id = (current_player, player_hand.index(chosen_card))
                    self.selected_cards.add(card_id)
                self.play_cards(current_player)
                self.start_time = pygame.time.get_ticks()
                print(f"Đây là lượt của người chơi: {self.game.current_turn + 1}")

    def draw_buttons(self):
        for player in range(FOUR_PLAYERS):
            # Vẽ nút khi đến lượt người chơi (dùng để test chương trình)
            if self.game.current_turn == player:
                pygame.draw.rect(self.screen, (1, 117, 132), self.buttons[player]["play"])  
                pygame.draw.rect(self.screen, (201, 22, 38), self.buttons[player]["pass"]) 

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
                    if player != (self.player-1):
                        self.screen.blit(card.unknown_card_texture, (x + i * spacing + x_offset, y + y_offset))
                    else:
                        self.screen.blit(card.texture, (x + i * spacing + x_offset, y + y_offset))
                # Player 2, 4 xếp hàng dọc
                else:
                    if player != (self.player-1):
                        self.screen.blit(card.unknown_card_texture, (x + x_offset, y + i * spacing + y_offset))
                    else:
                        self.screen.blit(card.texture, (x + x_offset, y + i * spacing + y_offset))

        # Bài đã đánh ở giữa màn hình
        center_x, center_y = SCREEN_WIDTH // 2 - (len(self.center_cards) * CARD_OFFSET) // 2 - 100, SCREEN_HEIGHT // 2 - 100
        for i, card in enumerate(self.center_cards):
            self.screen.blit(card.texture, (center_x + i * CARD_OFFSET, center_y))
            
    def draw_ranking(self):
        font = pygame.font.Font(None, 30)
        for player, rank in self.game.rankings:
            print(player)
            player_pos = (PLAYER_POSITIONS[player][0] + 300, PLAYER_POSITIONS[player][1] + 50)
            if player == 1:
                player_pos = (PLAYER_POSITIONS[player][0] + 100, PLAYER_POSITIONS[player][1] + 300)
            elif player == 2:
                player_pos = (PLAYER_POSITIONS[player][0] + 300, PLAYER_POSITIONS[player][1])
            elif player == 3:
                player_pos = (PLAYER_POSITIONS[player][0] + 50, PLAYER_POSITIONS[player][1] + 300)
                
            text_surface = font.render(f"Rank {rank}: Player {player + 1}", True, (15, 15, 15))

            if player in [0, 2]:
                self.screen.blit(text_surface, (player_pos[0], player_pos[1] + 40))
            else: 
                text_surface = pygame.transform.rotate(text_surface, 90)
                self.screen.blit(text_surface, (player_pos[0] - 20, player_pos[1]))


    # Xử lý sự kiện click chuột
    def handle_click(self, pos):
        current_player = self.game.current_turn

        # Xử lý bấm nút Play, Pass
        if self.buttons[current_player]["play"].collidepoint(pos):
            self.play_cards(current_player)
            self.start_time = pygame.time.get_ticks()
            print(f"Đây là lượt của người chơi: {self.game.current_turn + 1}")
            return
        if self.buttons[current_player]["pass"].collidepoint(pos):
            if self.game.last_play:
                self.game.pass_turn(current_player)
                self.start_time = pygame.time.get_ticks()
                print(f"Đây là lượt của người chơi: {self.game.current_turn + 1}")
                self.selected_cards.clear()
                # gửi gói tin
                self.action = list(self.selected_cards)
                self.network.send(self.action)
                self.action.clear()
            else:
                print("Đây là vòng mới nên bản không thể bỏ qua lượt đánh này")
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
    def animate_cards_to_center(self, played_cards, player):
        target_x, target_y = SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        frames = 15  # Số bước di chuyển

        # Xác định vị trí bắt đầu dựa trên người chơi
        if player == 0:  
            start_x, start_y = 20, SCREEN_HEIGHT // 2
        elif player == 1:  
            start_x, start_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - CARD_HEIGHT - 20
        elif player == 2:  
            start_x, start_y = SCREEN_WIDTH - CARD_WIDTH - 20, SCREEN_HEIGHT // 2
        elif player == 3:  
            start_x, start_y = SCREEN_WIDTH // 2, 20
        else:
            return  # Trường hợp không hợp lệ

        for frame in range(frames):
            self.screen.fill((217, 143, 102))  
            self.draw_cards()  # Vẽ lại bài không bao gồm bài đang đánh

            for i, card in enumerate(played_cards):
                x_step = (target_x - start_x) / frames
                y_step = (target_y - start_y) / frames
                new_x = start_x + x_step * frame
                new_y = start_y + y_step * frame
                self.screen.blit(card.texture, (new_x, new_y))

            pygame.display.flip()
            self.clock.tick(30)

    # Khi người chơi bấm nút đánh
    def play_cards(self, player, from_server=False):
        if self.game.current_turn != player:
            print("Không phải lượt của bạn!")
            return

        # Các quân bài chuẩn bị đánh theo thứ tự từ yếu đến mạnh
        print("Check lỗi này")
        print(self.selected_cards)
        played_cards = sorted(
            [self.game.players[player][i] for _, i in self.selected_cards],
            key=lambda card: (RANK_ORDER[card.rank], SUIT_ORDER[card.suit])
        )
        
        for i in range(len(played_cards)):
            print(played_cards[i].rank, played_cards[i].suit)

        if self.game.play_cards(player, played_cards):
            # Cập nhật bài đã được đánh di chuyển vào giữa màn hình
            self.center_cards = played_cards
            self.played_card_positions = [(PLAYER_POSITIONS[0][0] + i * CARD_OFFSET, PLAYER_POSITIONS[0][1]) for _, i in sorted(self.selected_cards)]
            self.animate_cards_to_center(played_cards, self.game.current_turn)
            for card in played_cards:
                self.game.players[player].remove(card)
            print(len(self.game.players[player]))
            
            if not from_server:
                # gửi gói tin
                self.action = list(self.selected_cards)
                # Xóa các quân đã chọn
                self.selected_cards.clear()
                self.network.send(self.action)
                self.action.clear()
            else:
                # Xóa các quân đã chọn
                self.selected_cards.clear()
            
            # check winner
            if self.game.check_winner(player):
                print(f"Người chơi {player+1} đạt rank {len(self.game.rankings)}")

    def run(self):
        print(f"Đây là người chơi {self.player}")
        while self.running:
            if self.game.check_end():
                self.running = False
            
            self.screen.fill((217, 143, 102))
            self.draw_cards()
            self.draw_buttons()
            self.draw_ranking()
            
            # self.network.receive(self.handle_update)
            # threading.Thread(target=self.network.receive, args=(self.handle_update,), daemon=True).start()
            
            # Hiển thị vòng tròn thời gian của người chơi hiện tại
            self.draw_timer_circle(self.game.current_turn)
            self.update_turn_timer()
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game.current_turn == (self.player-1):
                        self.handle_click(event.pos)

            self.clock.tick(30)

        self.network.close()
        pygame.quit()


