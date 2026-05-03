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

### 1. Install dependencies

```bash
cd /home/isakadmin/docker_mcp
pip3 install -r requirements.txt
```

### 2. Configure SSH target

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
DOCKER_MCP_CONFIG=/other/path/config.json python3 server.py
```

### 3. Verify SSH access

```bash
ssh -i ~/.ssh/id_rsa ubuntu@your-server.example.com docker ps
```

### 4. Register with GitHub Copilot

#### GitHub Copilot CLI (`~/.config/github-copilot/mcp.json`)

```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "python3",
      "args": ["/home/isakadmin/docker_mcp/server.py"]
    }
  }
}
```

#### VS Code / Copilot in VS Code (`.vscode/mcp.json` or user settings)

```json
{
  "servers": {
    "docker-mcp": {
      "type": "stdio",
      "command": "python3",
      "args": ["/home/isakadmin/docker_mcp/server.py"]
    }
  }
}
```

## Notes

- The SSH connection uses `StrictHostKeyChecking=accept-new` - safe for known hosts, will warn on key changes.
- `docker_build` and `docker_pull` use a 5-10 min timeout; adjust `timeout` in `server.py` if needed.
- For Compose tools, `project_dir` is the **remote** path containing `docker-compose.yml`.
- `docker_logs` and `docker_exec` redirect stderr to stdout so output is always captured.
