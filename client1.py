from networking import Network
from gameUI import GameUI
from card import Card
import threading

def start_game(data):
    if data["game_started"]:
        print("Đã được chia bài")
        game_data["game_started"] = True 
        game_data["hand"] = {
            player_id: [Card.deserialize(card_data) for card_data in cards]
            for player_id, cards in data["cards"].items()
        }

network = Network(host="localhost", port=5555)
network.connect()

game_data = {"hand": [], "game_started": False}

# Bắt đầu luồng nhận dữ liệu
threading.Thread(target=network.receive, args=(start_game,), daemon=True).start()

# Chờ đến khi trò chơi bắt đầu
print("Chờ các đối thủ vào...")
while not game_data["game_started"]:
    pass

print("Trò chơi bắt đầu!")

if __name__ == "__main__":
    GameUI(game_data["hand"]).run()

# def handle_update(data):
#     print(data)

# network = Network()
# network.connect()

# # Tạo luồng lắng nghe dữ liệu từ server
# import threading
# threading.Thread(target=network.receive, args=(handle_update,), daemon=True).start()

# while True:
#     action = input("Nhập hành động (play/bỏ lượt/thoát): ").strip().lower()
#     if action == "thoát":
#         print("Thoát game!")
#         break
#     card = input("Nhập quân bài (VD: 3♠, J♥) hoặc 'None' nếu bỏ lượt: ").strip()
#     card = None if card.lower() == "none" else card

#     move = {"player_id": network.id, "action": action, "card": card}
#     network.send(move)

# network.close()
