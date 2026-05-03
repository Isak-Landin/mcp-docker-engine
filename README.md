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

> You can clone to any directory. Replace `~/mcp-docker-engine` with your preferred path — just use that same path in step 5.

### 2. Install dependencies

```bash
sudo apt install python3.12-venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Configure SSH target

```bash
cp config.example.json config.json
# Edit config.json with your server details
```

`config.json` fields:

```json
{
  "host": "your-server.example.com",
  "user": "ubuntu",
  "key_path": "~/.ssh/id_rsa",
  "port": 22
}
```

Override config path at runtime:
```bash
DOCKER_MCP_CONFIG=/other/path/config.json .venv/bin/python3 server.py
```

### 4. Verify SSH access

```bash
ssh -i ~/.ssh/id_rsa ubuntu@your-server.example.com docker ps
```

### 5. Register with GitHub Copilot

Use the absolute path to your clone. If you used `~/mcp-docker-engine`, expand it: run `echo ~/mcp-docker-engine` to get the full path, then substitute below.

#### MCP server config

**GitHub Copilot CLI** (`~/.config/github-copilot/mcp.json`) — add to your existing `mcpServers` object, or create the file:

```json
"docker-mcp": {
  "command": "/your/path/to/mcp-docker-engine/.venv/bin/python3",
  "args": ["/your/path/to/mcp-docker-engine/server.py"]
}
```

**VS Code / Copilot in VS Code** (`.vscode/mcp.json` or user settings) — add to your existing `servers` object, or create the file:

```json
"docker-mcp": {
  "type": "stdio",
  "command": "/your/path/to/mcp-docker-engine/.venv/bin/python3",
  "args": ["/your/path/to/mcp-docker-engine/server.py"]
}
```

#### Copilot instructions

`instructions.md` contains example tool usage for all 26 tools. You can:

- **Add** its contents to your existing Copilot instructions file (e.g. `.github/copilot-instructions.md` or your workspace instructions)
- **Use it as-is** if you don't have an instructions file yet

## Notes

- The SSH connection uses `StrictHostKeyChecking=accept-new` - safe for known hosts, will warn on key changes.
- `docker_build` and `docker_pull` use a 5-10 min timeout; adjust `timeout` in `server.py` if needed.
- For Compose tools, `project_dir` is the **remote** path containing `docker-compose.yml`.
- `docker_logs` and `docker_exec` redirect stderr to stdout so output is always captured.
