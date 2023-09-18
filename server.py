import socket
import threading

messages = []

def broadcast_usernames():
    # Create a list of usernames from the client sockets
    usernames = [username for (username, _) in clients]
    # Broadcast the list to all connected clients
    for (_, client_socket) in clients:
        usernames_str = ", ".join(usernames)
        client_socket.send(f"Connected users: {usernames_str}".encode('utf-8'))
    # Sleep for a while before broadcasting again (adjust as needed)

def broadcast_last_50_messages():

    # Join the messages and usernames with newline characters
    message_log = ""
    for i in range(len(messages)):
        if i > 50:break
        message_log += f"{messages[i]['name']}: {messages[i]['message']}\n"
    return message_log.encode("utf-8")
def get_server_ip():
    try:
        # Create a temporary socket to get the server's IP address
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.settimeout(0.1)  # Set a timeout to prevent blocking

        # Connect to a remote host; this will return the local IP address
        temp_socket.connect(("8.8.8.8", 80))  # Use a well-known public DNS server

        server_ip = temp_socket.getsockname()[0]
        temp_socket.close()

        return server_ip
    except Exception as e:
        print(f"Error getting server IP: {e}")
        return "Unknown"


def handle_client(client_socket, username):
    try:
        # Broadcast the updated list of usernames to all clients
        broadcast_usernames()
        client_socket.send(f"Welcome, {username}!\n".encode('utf-8'))
        client_socket.send(broadcast_last_50_messages())
        # Add the username and client socket to the list
        clients.append((username, client_socket))
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Exit the loop if the client disconnects
            print(f"{username}: {message}")

            messages.append({"name":username, "message":message})
            
            # Broadcast the message to all connected clients
            for (_, client) in clients:
                if client != client_socket:
                    client.send(f"{username}: {message}".encode('utf-8'))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Remove the disconnected client from the list
        clients.remove((username, client_socket))
        client_socket.close()
        # Broadcast the updated list of usernames to all clients
        broadcast_usernames()

host = '0.0.0.0'
port = 8080
messages = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))

clients = []

try:
    server_socket.listen()
    server_ip = get_server_ip()
    print(f"Server is listening on {server_ip}:{port}")
    # Start the thread to broadcast usernames
    threading.Thread(target=broadcast_usernames).start()

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        
        # Receive the username from the client
        username = client_socket.recv(1024).decode('utf-8')

        # Create a thread to handle the client
        threading.Thread(target=handle_client, args=(client_socket, username)).start()

except KeyboardInterrupt:
    print("Server stopped by user.")
except Exception as e:
    print(f"Error: {e}")
finally:
    server_socket.close()
