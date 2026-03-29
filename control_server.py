import socket
from pathlib import Path
import sys

def tcp_server():

    print("Server starting")

    server_socket = socket.socket()
    print("Server: Socket created")

    try:
        host = sys.argv[1] if len(sys.argv) > 1 else "192.168.70.6"
        server_address = (host, 7007)
        print(f"Server: Binding to {server_address[0]}:{server_address[1]}...")

        server_socket.bind(server_address)
        server_socket.listen(5)

        conn, addr = server_socket.accept()
        print(f"Connected from: {addr}")

        while True:

            command = input("> ")

            if command.startswith("cmd:"):
                conn.send(command.encode("utf-8"))
                response = conn.recv(65535)
                print(response.decode('utf-8'))

            elif command.startswith("send:"):
                _, filename = command.split(":")
                file = Path(filename)
                filesize = file.stat().st_size
                print(f"Server sends: filename: {filename}, filesize: {filesize}")
                header = f"send:{filename}:{filesize}\n"
                conn.sendall(header.encode("utf-8"))
                try:
                    with open(filename, 'rb') as f:
                        file_data = f.read()
                except Exception as e:
                    print(f"Error: {e}")
                if file_data:
                    conn.sendall(file_data)
                    print("File read complete")

            elif command.startswith("get:"):
                _, filename = command.split(":")
                header = f"get:{filename}"
                conn.sendall(header.encode("utf-8"))

                response = conn.recv(1024)
                response_header = response.decode('utf-8')
                _, filename, filesize = response_header.split(":")
                filesize = int(filesize)

                file_data = b""
                while len(file_data) < filesize:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    file_data += chunk

                with open(filename, "wb") as f:
                    f.write(file_data)
                print("File received from VM")


    except socket.error as err:
        print(f"Server: Socket error: {err}")
    except Exception as e:
        print(f"Server: An error occured: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    tcp_server()