import socket
import threading
import os

global logged_in
logged_in = True

def receive_messages(client_socket):
    global logged_in  # Declare logged_in as a global variable
    try:
        while logged_in:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
    except KeyboardInterrupt:
        logged_in = False
        client_socket.close()
    except Exception as e:
        logged_in = False
        print(f"Error receiving message: {e}")
        client_socket.close()

def main():
    print("neoProject v0.7")
    global logged_in  # Declare logged_in as a global variable
    username = input("Enter your username: ") or "unnamed"
    host_input = input("Server IP (or blank for localhost): ")
    host = '127.0.0.1' if host_input == '' else host_input
    port_input = input("Server port (or blank for default): ")
    port = 8080 if port_input == '' else int(port_input)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        
        # Send the username to the server
        client_socket.send(username.encode('utf-8'))
        
        print(f"Connected to {host}:{port}")

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while logged_in:
            message = input()
            if message.lower() == '!exit':
                # Send a disconnect event to the server
                logged_in = False
                client_socket.send("Client has disconnected.".encode('utf-8'))
                break  # Exit the loop and close the connection
            elif message.lower() == "!clear":
            	os.system("clear" if os.name == "posix" else "cls")
            	
            else:
                client_socket.send(message.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
