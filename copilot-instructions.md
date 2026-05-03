## Docker MCP

Use the docker-mcp server to inspect and manage containers on the remote server over SSH. All Docker operations execute remotely — never locally.

- Use `docker_ps` and `docker_ps(all_containers=True)` to list running or all containers. Use `docker_images` to list available images.
- Use `docker_logs` to read container output. Supported args: `tail`, `since` (e.g. "1h", "30m"), `grep`, `timestamps`.
- Use `docker_exec` to run a command inside a running container. Use `docker_inspect` for full container or image config. Use `docker_top` for processes inside a container. Use `docker_stats` for a live CPU/memory snapshot.
- Use `docker_start`, `docker_stop`, `docker_restart` for lifecycle control. `docker_restart` accepts an optional `timeout` for graceful stop.
- Use `docker_run` to start a new container. Args: `image`, `name`, `ports`, `env`, `volumes`, `command`, `detach`, `rm`.
- Use `docker_rm` to remove a container (`force=True` to remove running). Use `docker_rmi` to remove an image.
- Use `docker_build` to build an image from a path on the remote server. Args: `path`, `tag`, `dockerfile`, `no_cache`.
- Use `docker_pull` to pull an image on the remote server.
- For Compose projects, `project_dir` is always the remote path containing `docker-compose.yml`. Use `docker_compose_ps`, `docker_compose_logs` (args: `tail`, `services`), `docker_compose_up` (args: `build`, `services`), `docker_compose_down` (args: `volumes`), `docker_compose_restart` (args: `services`), `docker_compose_pull`.
- Use `docker_system_df`, `docker_info`, `docker_version`, `docker_network_ls`, `docker_volume_ls` for system-level inspection.
- When something is broken: start with `docker_ps(all_containers=True)`, then `docker_logs(container="name", tail=200, grep="ERROR")`, then `docker_inspect` for exit code and restart count.
- For Compose issues: `docker_compose_ps` -> `docker_compose_logs` -> `docker_compose_down` + `docker_compose_up(build=True)`.
