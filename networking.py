import socket
import pickle
import threading
import pygame
from const import *
from card import Card
import random

class Network:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = host
        self.port = port
        self.addr = (self.server, self.port)
        self.id = None

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.id = self.client.recv(4096).decode()
            print(f"Connected to server with ID {self.id}")
        except Exception as e:
            print("Connection failed:", e)
            
    def receive(self, callback):
        """ Luôn lắng nghe dữ liệu từ server và gọi callback để xử lý """
        while True:
            try:
                data = pickle.loads(self.client.recv(4096))
                callback(data)  # Gọi hàm xử lý dữ liệu
            except Exception as e:
                print(f"Kết nối đến server bị mất: {e}")
                break

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))
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
        for conn in clients:
            if conn != sender_conn:
                try:
                    conn.send(pickle.dumps(data))
                except:
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
            conn.send(pickle.dumps(data))
            print(f"Đã gửi bài cho player {i+1}")
        except Exception as e:
            print(f"Lỗi khi gửi bài cho Player {i + 1}: {e}")

    print("All players connected, game starting!")
