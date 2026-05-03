#!/usr/bin/env python3
"""Docker MCP - Remote Docker management over SSH for local Copilot sessions.

Run as a stdio MCP server:
    python server.py

Configure SSH target in mcp-config.json (see mcp-config.example.json).
Override config path via DOCKER_MCP_CONFIG env var.
"""

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

_DEFAULT_CONFIG = Path(__file__).parent / "mcp-config.json"


# ── SSH helpers ───────────────────────────────────────────────────────────────

def _cfg() -> dict:
    path = Path(os.environ.get("DOCKER_MCP_CONFIG", _DEFAULT_CONFIG))
    if not path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}\n"
            "Copy mcp-config.example.json -> mcp-config.json and fill in your SSH details."
        )
    return json.loads(path.read_text())


def _ssh(cmd: str, timeout: int = 120) -> str:
    c = _cfg()
    proc = subprocess.run(
        [
            "ssh",
            "-i", str(Path(c["key_path"]).expanduser()),
            "-p", str(c.get("port", 22)),
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=10",
            f"{c['user']}@{c['host']}",
            cmd,
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        return f"[exit {proc.returncode}] {err}"
    return proc.stdout or "(no output)"


def _q(s: str) -> str:
    return shlex.quote(s)


# ── App ───────────────────────────────────────────────────────────────────────

app = FastMCP("docker-mcp")


# ── Containers ────────────────────────────────────────────────────────────────

@app.tool()
def docker_ps(all_containers: bool = False) -> str:
    """List containers on the remote host."""
    return _ssh(f"docker ps{' -a' if all_containers else ''}")


@app.tool()
def docker_logs(
    container: str,
    tail: int = 100,
    since: Optional[str] = None,
    timestamps: bool = False,
    grep: Optional[str] = None,
) -> str:
    """
    Fetch container logs.
    - tail: lines from the end (default 100)
    - since: relative or absolute time, e.g. "1h", "30m", "2024-01-01T00:00:00"
    - grep: case-insensitive pattern to filter output lines
    """
    parts = ["docker", "logs", "--tail", str(tail)]
    if since:
        parts += ["--since", since]
    if timestamps:
        parts.append("--timestamps")
    parts.append(container)
    out = _ssh(shlex.join(parts) + " 2>&1")
    if grep:
        filtered = [ln for ln in out.splitlines() if grep.lower() in ln.lower()]
        return "\n".join(filtered) or f"(no lines matching '{grep}')"
    return out


@app.tool()
def docker_exec(container: str, command: str) -> str:
    """Execute a shell command inside a running container."""
    return _ssh(f"docker exec {_q(container)} sh -c {_q(command)} 2>&1")


@app.tool()
def docker_run(
    image: str,
    name: Optional[str] = None,
    command: Optional[str] = None,
    detach: bool = True,
    rm: bool = False,
    env: Optional[str] = None,
    ports: Optional[str] = None,
    volumes: Optional[str] = None,
    extra_args: Optional[str] = None,
) -> str:
    """
    Run a new container from an image.
    - env: space-separated KEY=VAL pairs, e.g. "FOO=bar BAZ=qux"
    - ports: space-separated host:container pairs, e.g. "8080:80 443:443"
    - volumes: space-separated host:container pairs, e.g. "/data:/data"
    - extra_args: any additional raw docker run flags
    """
    parts = ["docker", "run"]
    if detach:
        parts.append("-d")
    if rm:
        parts.append("--rm")
    if name:
        parts += ["--name", name]
    for e in (env or "").split():
        parts += ["-e", e]
    for p in (ports or "").split():
        parts += ["-p", p]
    for v in (volumes or "").split():
        parts += ["-v", v]
    if extra_args:
        parts += shlex.split(extra_args)
    parts.append(image)
    if command:
        parts += shlex.split(command)
    return _ssh(shlex.join(parts) + " 2>&1")


@app.tool()
def docker_start(container: str) -> str:
    """Start one or more stopped containers (space-separated names/IDs)."""
    return _ssh(f"docker start {container}")


@app.tool()
def docker_stop(container: str, timeout: int = 10) -> str:
    """Stop one or more running containers (space-separated names/IDs)."""
    return _ssh(f"docker stop -t {timeout} {container}")


@app.tool()
def docker_restart(container: str, timeout: int = 10) -> str:
    """Restart one or more containers (space-separated names/IDs)."""
    return _ssh(f"docker restart -t {timeout} {container}")


@app.tool()
def docker_rm(container: str, force: bool = False, volumes: bool = False) -> str:
    """Remove one or more containers (space-separated names/IDs)."""
    flags = ("" + (" -f" if force else "") + (" -v" if volumes else "")).strip()
    cmd = f"docker rm {(' ' + flags) if flags else ''} {container}".strip()
    return _ssh(cmd)


@app.tool()
def docker_inspect(target: str) -> str:
    """Return detailed low-level information about a container or image."""
    return _ssh(f"docker inspect {_q(target)}")


@app.tool()
def docker_stats(container: Optional[str] = None) -> str:
    """Snapshot of resource usage stats. Pass container name/ID or omit for all running."""
    target = f" {container}" if container else ""
    return _ssh(f"docker stats --no-stream{target}")


@app.tool()
def docker_top(container: str) -> str:
    """Show running processes inside a container."""
    return _ssh(f"docker top {_q(container)}")


# ── Images ────────────────────────────────────────────────────────────────────

@app.tool()
def docker_images(filter: Optional[str] = None) -> str:
    """List images on the remote host. filter: e.g. 'dangling=true'."""
    return _ssh("docker images" + (f" --filter {_q(filter)}" if filter else ""))


@app.tool()
def docker_pull(image: str) -> str:
    """Pull an image or repository from a registry."""
    return _ssh(f"docker pull {_q(image)}", timeout=300)


@app.tool()
def docker_rmi(image: str, force: bool = False) -> str:
    """Remove one or more images (space-separated names/IDs)."""
    return _ssh(f"docker rmi{' -f' if force else ''} {image}")


@app.tool()
def docker_build(
    path: str,
    tag: Optional[str] = None,
    dockerfile: Optional[str] = None,
    no_cache: bool = False,
) -> str:
    """Build an image from a Dockerfile on the remote server. path is the remote build context."""
    parts = ["docker", "build"]
    if tag:
        parts += ["-t", tag]
    if dockerfile:
        parts += ["-f", dockerfile]
    if no_cache:
        parts.append("--no-cache")
    parts.append(path)
    return _ssh(shlex.join(parts) + " 2>&1", timeout=600)


# ── Docker Compose ────────────────────────────────────────────────────────────

def _compose(project_dir: str) -> str:
    return f"cd {_q(project_dir)} && docker compose"


@app.tool()
def docker_compose_ps(project_dir: str) -> str:
    """List services in a Compose project. project_dir is the path on the remote host."""
    return _ssh(f"{_compose(project_dir)} ps")


@app.tool()
def docker_compose_up(
    project_dir: str,
    services: Optional[str] = None,
    detach: bool = True,
    build: bool = False,
) -> str:
    """
    Create and start Compose services.
    - services: space-separated service names (optional, starts all if omitted)
    """
    cmd = _compose(project_dir) + " up"
    if detach:
        cmd += " -d"
    if build:
        cmd += " --build"
    if services:
        cmd += f" {services}"
    return _ssh(cmd + " 2>&1", timeout=300)


@app.tool()
def docker_compose_down(
    project_dir: str,
    volumes: bool = False,
    remove_orphans: bool = False,
) -> str:
    """Stop and remove Compose services, networks, and optionally volumes."""
    cmd = _compose(project_dir) + " down"
    if volumes:
        cmd += " -v"
    if remove_orphans:
        cmd += " --remove-orphans"
    return _ssh(cmd + " 2>&1")


@app.tool()
def docker_compose_logs(
    project_dir: str,
    services: Optional[str] = None,
    tail: int = 100,
    timestamps: bool = False,
) -> str:
    """View logs from Compose services."""
    cmd = _compose(project_dir) + f" logs --tail={tail}"
    if timestamps:
        cmd += " --timestamps"
    if services:
        cmd += f" {services}"
    return _ssh(cmd + " 2>&1")


@app.tool()
def docker_compose_restart(project_dir: str, services: Optional[str] = None) -> str:
    """Restart Compose services. services: space-separated list (optional)."""
    cmd = _compose(project_dir) + " restart"
    if services:
        cmd += f" {services}"
    return _ssh(cmd + " 2>&1")


@app.tool()
def docker_compose_pull(project_dir: str, services: Optional[str] = None) -> str:
    """Pull images for Compose services."""
    cmd = _compose(project_dir) + " pull"
    if services:
        cmd += f" {services}"
    return _ssh(cmd + " 2>&1", timeout=300)


# ── System ────────────────────────────────────────────────────────────────────

@app.tool()
def docker_system_df() -> str:
    """Show Docker disk usage on the remote host."""
    return _ssh("docker system df")


@app.tool()
def docker_info() -> str:
    """Display system-wide Docker information on the remote host."""
    return _ssh("docker info")


@app.tool()
def docker_version() -> str:
    """Show Docker version on the remote host."""
    return _ssh("docker version")


@app.tool()
def docker_network_ls() -> str:
    """List all Docker networks on the remote host."""
    return _ssh("docker network ls")


@app.tool()
def docker_volume_ls() -> str:
    """List all Docker volumes on the remote host."""
    return _ssh("docker volume ls")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run()
