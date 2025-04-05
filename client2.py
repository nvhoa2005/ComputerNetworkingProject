from networking import Network
from gameUI import GameUI
from card import Card
import threading
import time

def process_data(data):
    """ Nhận dữ liệu từ server và xử lý """
    if data and data.get("game_started"):
        print("Đã được chia bài!")
        game_data["game_started"] = True
        game_data["hand"] = {
            player_id: [Card.deserialize(card_data) for card_data in cards]
            for player_id, cards in data["cards"].items()
        }

# Khởi tạo kết nối mạng
network = Network(host="localhost", port=5555)
network.connect()

game_data = {"hand": [], "game_started": False}

# Bắt đầu luồng nhận dữ liệu
threading.Thread(target=network.receive, args=(process_data,), daemon=True).start()

# Chờ đến khi trò chơi bắt đầu
print("Chờ các đối thủ vào...")
while not game_data["game_started"]:
    data = network.get_data()  # Lấy dữ liệu từ hàng đợi
    if data:
        process_data(data)  # Gọi process_data với dữ liệu mới

print("Trò chơi bắt đầu!")

if __name__ == "__main__":
    network.close()
    GameUI(game_data["hand"]).run()
