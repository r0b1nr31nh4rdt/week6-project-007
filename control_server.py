import socket
from pathlib import Path
import sys

def tcp_server():

    print("Server starting")
    server_socket = socket.socket()
    print("Server: Socket created")

    try:
        # Use IP from arguments or default
        host = sys.argv[1] if len(sys.argv) > 1 else "192.168.70.6"
        server_address = (host, 7007)
        print(f"Server: Binding to {server_address[0]}:{server_address[1]}...")

        server_socket.bind(server_address)
        server_socket.listen(5)

        print("Waiting ...")
        conn, addr = server_socket.accept()
        print(f"Connected from: {addr}")

        while True:

            command = input("> ")

            # --- CMD: Execute a shell command on the VM ---
            if command.startswith("cmd:"):
                conn.send(command.encode("utf-8"))
                response = conn.recv(65535)
                print(response.decode('utf-8'))

            # --- SEND: Send a file from host to VM ---
            elif command.startswith("send:"):
                filename = command[5:]
                print(f"Filename: {filename}")
                file = Path(filename)

                if not file.exists():
                    print(f"File not found: {filename}")
                    continue

                filesize = file.stat().st_size
                print(f"Server sends: filename: {filename}, filesize: {filesize}")

                # Send header with filename and filesize
                header = f"send:{filename}:{filesize}\n"
                conn.sendall(header.encode("utf-8"))

                # Send file as raw bytes
                with open(filename, 'rb') as f:
                    file_data = f.read()
                conn.sendall(file_data)
                print("File read complete")

            # --- GET: Retrieve a file from VM
            elif command.startswith("get:"):
                conn.sendall(command.encode("utf-8"))

                response = conn.recv(1024)
                response_header = response.decode('utf-8')

                if response_header.startswith("Error"):
                    print(response_header)
                    continue

                print(f"Response: {response_header}")
                parts = response_header.rsplit(":", 1)
                filename = parts[0][4:] # Everything after "get:"
                print(f"Filename: {filename}")
                filesize = int(parts[1])
                print(f"Filesize: {filesize}")

                file_data = b""
                while len(file_data) < filesize:
                    remaining = filesize - len(file_data)
                    chunk = conn.recv(min(65535, remaining))
                    if not chunk:
                        break
                    file_data += chunk

                save_name = Path(filename).name
                with open(save_name, "wb") as f:
                    f.write(file_data)
                print(f"File received: {save_name}")


    except socket.error as err:
        print(f"Server: Socket error: {err}")
    except Exception as e:
        print(f"Server: An error occured: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    tcp_server()