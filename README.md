# Docker MCP

Remote Docker management over SSH — exposed as a local MCP server for GitHub Copilot sessions.

No server-side component required. The MCP runs locally and SSHes into the remote host to execute Docker commands.

## Tools

| Tool | Description |
|---|---|
| `docker_ps` | List containers |
| `docker_logs` | Fetch logs (tail, since, grep) |
| `docker_exec` | Run command inside container |
| `docker_run` | Start new container |
| `docker_start` / `docker_stop` / `docker_restart` | Lifecycle control |
| `docker_rm` | Remove container(s) |
| `docker_inspect` | Detailed container/image info |
| `docker_stats` | Resource usage snapshot |
| `docker_top` | Processes inside container |
| `docker_images` | List images |
| `docker_pull` / `docker_rmi` / `docker_build` | Image management |
| `docker_compose_ps/up/down/logs/restart/pull` | Compose operations |
| `docker_system_df` | Disk usage |
| `docker_info` / `docker_version` | System info |
| `docker_network_ls` / `docker_volume_ls` | Network & volume listing |

## Setup

### 1. Clone the repository

```bash
git clone git@github.com:Isak-Landin/mcp-docker-engine.git ~/mcp-docker-engine
cd ~/mcp-docker-engine
```

### 2. Install dependencies

```bash
sudo apt install python3.12-venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Configure SSH target

```bash
cp mcp-config.example.json mcp-config.json
```

`mcp-config.json` fields:

```json
{
  "host": "your-server.example.com",
  "user": "ubuntu",
  "key_path": "~/.ssh/id_rsa",
  "port": 22
}
```

Insert the `docker-mcp` entry into your Copilot home's `mcp-config.json`, VS Code's `.vscode/mcp.json`, or whichever MCP config your client uses.

### 4. Verify SSH access

Using the values from your `mcp-config.json`:

```bash
ssh -i <key_path> <user>@<host> docker ps
```

### 5. Register with GitHub Copilot

Replace `$HOME` with your actual home directory path (run `echo $HOME`).

#### Copilot CLI

Add the `docker-mcp` entry to the `mcpServers` object in your Copilot home's `mcp-config.json`:

```json
"docker-mcp": {
  "command": "$HOME/mcp-docker-engine/.venv/bin/python3",
  "args": ["$HOME/mcp-docker-engine/server.py"]
}
```

#### VS Code

Add the `docker-mcp` entry to the `servers` object in `.vscode/mcp.json`:

```json
"docker-mcp": {
  "type": "stdio",
  "command": "$HOME/mcp-docker-engine/.venv/bin/python3",
  "args": ["$HOME/mcp-docker-engine/server.py"]
}
```

#### Copilot instructions

`instructions.md` contains example tool usage for all 26 tools. Add its contents to your existing Copilot home's `copilot-instructions.md`, or use it as-is if you don't have one yet.

## Notes

- The SSH connection uses `StrictHostKeyChecking=accept-new` - safe for known hosts, will warn on key changes.
- `docker_build` and `docker_pull` use a 5-10 min timeout; adjust `timeout` in `server.py` if needed.
- For Compose tools, `project_dir` is the **remote** path containing `docker-compose.yml`.
- `docker_logs` and `docker_exec` redirect stderr to stdout so output is always captured.
