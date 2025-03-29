from networking import start_server

if __name__ == "__main__":
    # host 0.0.0.0 để chấp nhận kết nối từ bất cứ người chơi nào
    start_server(host="0.0.0.0", port=5555, max_clients=8)