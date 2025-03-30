import socket
import pickle
import threading
import pygame
from const import *
from card import Card
import random
import queue  # Hàng đợi để xử lý dữ liệu không đồng bộ
import select

class Network:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = host
        self.port = port
        self.addr = (self.server, self.port)
        self.id = None
        self.data_queue = queue.Queue()  # Hàng đợi để nhận dữ liệu
        self.lock = threading.Lock()
        self.callback = None

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.id = self.client.recv(4096).decode()
            print(f"Connected to server with ID {self.id}")
            
            # Chạy luồng riêng để nhận dữ liệu mà không làm lag giao diện
            threading.Thread(target=self.receive, daemon=True).start()
        except Exception as e:
            print("Connection failed:", e)

    def receive(self, callback=None):
        """Luôn lắng nghe dữ liệu từ server và đẩy vào queue để xử lý"""
        if callback is not None:
            self.callback = callback  # 🔥 Cập nhật callback mỗi lần gọi
        print("receive")
        while True:
            try:
                compressed_data = self.client.recv(4096)
                if not compressed_data:
                    break
                data = pickle.loads(compressed_data)
                print("📥 Nhận dữ liệu từ server:", data)
                # Kiểm tra callback trước khi gọi
                with self.lock:  # 🔒 Dùng lock để tránh tranh chấp dữ liệu
                    if self.callback is not None:
                        print("callback")
                        self.callback(data)
                    else:
                        print("Không có callback được truyền")
                    self.data_queue.put(data)
                print("Hello")
            except Exception as e:
                print(f"Kết nối đến server bị mất: {e}")
                break
    
    # def receive(self, callback=None):
    #     """Nhận dữ liệu từ server mà không làm chậm game loop"""
    #     ready, _, _ = select.select([self.client], [], [], 0)  # Kiểm tra socket có dữ liệu không
    #     if ready:
    #         try:
    #             compressed_data = self.client.recv(4096)
    #             if not compressed_data:
    #                 return
                
    #             data = pickle.loads(compressed_data)
    #             print("📥 Nhận dữ liệu từ server:", data)

    #             if callback is not None and callable(callback):
    #                 callback(data)

    #         except Exception as e:
    #             print(f"Kết nối đến server bị mất: {e}")

    def get_data(self):
        """Lấy dữ liệu từ queue (nếu có) để xử lý trong game loop"""
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None

    def send(self, data):
        """Gửi dữ liệu mà không chặn giao diện"""
        try:
            compressed_data = pickle.dumps(data)
            with self.lock:  # 🔒 Dùng lock để đảm bảo không có xung đột khi gửi
                self.client.send(compressed_data)
        except Exception as e:
            print("Error sending data:", e)
            return None

    def close(self):
        self.client.close()

# Server-side code
def start_server(host='127.0.0.1', port=5555, max_clients=8):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(max_clients)
    print("Server started, waiting for players...")

    clients = []
    
    def broadcast(data, sender_conn):
        """ Gửi dữ liệu đến tất cả client trừ người gửi """
        disconnected_clients = []  # Danh sách client bị mất kết nối
        for conn in clients:
            if conn != sender_conn:
                try:
                    conn.send(pickle.dumps(data))
                    print(data)
                    print(f"📤 Đã gửi đến client {conn}")
                except:
                    print(f"🔴 Client {conn} mất kết nối, đánh dấu để xóa.")
                    disconnected_clients.append(conn)

        # Xóa client bị mất kết nối sau khi gửi xong
        for conn in disconnected_clients:
            clients.remove(conn)


    def handle_client(conn, player_id):
        """ Xử lý từng client trong luồng riêng biệt """
        while True:
            try:
                data = pickle.loads(conn.recv(4096))
                print(f"Received from Player {player_id}: {data}")
                broadcast(data, conn)  # Gửi đến các client khác
            except Exception as e:
                print(f"Player {player_id} disconnected: {e}")
                clients.remove(conn)
                conn.close()
                break

    while True:
        conn, addr = server.accept()
        if len(clients) >= max_clients:
            print("Server full, rejecting connection")
            conn.close()
            continue

        clients.append(conn)
        player_id = len(clients)
        conn.send(str(player_id).encode())  # Gửi ID cho client
        print(f"Player {player_id} connected from {addr}")

        threading.Thread(target=handle_client, args=(conn, player_id)).start()

        # Khi có ít nhất 4 người chơi, bắt đầu game
        if len(clients) == FOUR_PLAYERS:
            start_game(clients)  # Hàm chia bài cho 4 người đầu tiên

def start_game(clients):
    """ Bắt đầu game khi có đủ 4 người chơi """
    deck = [Card(suit, rank) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)

    players = {i: [card.serialize() for card in deck[i*13:(i+1)*13]] for i in range(FOUR_PLAYERS)}
    for player in range(FOUR_PLAYERS):
        players[player] = sorted(
            players[player],
            key=lambda card: (RANK_ORDER[card["rank"]], SUIT_ORDER[card["suit"]])
        )

    for i, conn in enumerate(clients[:FOUR_PLAYERS]):
        data = {
            "game_started": True,
            "cards": players
        }
        try:
            compressed_data = pickle.dumps(data)  # Nén trước khi gửi
            conn.send(compressed_data)  # Gửi dữ liệu đã nén
            print(f"Đã gửi bài cho player {i+1}")
        except Exception as e:
            print(f"Lỗi khi gửi bài cho Player {i + 1}: {e}")

    print("All players connected, game starting!")
