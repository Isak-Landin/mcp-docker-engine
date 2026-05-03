You have access to a Docker MCP that manages containers on a remote server over SSH. Use these tools to inspect, control, and debug the remote Docker environment.

Inspect what is running with `docker_ps()`, `docker_ps(all_containers=True)`, `docker_images()`, `docker_stats()`, or `docker_stats(container="name")`. Read logs with `docker_logs(container="name")`, optional args: `tail`, `since` (e.g. "1h", "30m"), `grep`, `timestamps`. Execute commands inside containers with `docker_exec(container="name", command="...")`. Inspect detailed config with `docker_inspect(target="name")` or processes with `docker_top(container="name")`.

Control container lifecycle with `docker_start`, `docker_stop`, `docker_restart` (each takes `container="name"`, restart also accepts `timeout`). Remove containers with `docker_rm(container="name", force=False)`. Run new containers with `docker_run(image="...", name="...", ports="host:container", env="K=V", volumes="host:container", command="...", detach=True, rm=False)`. Build images with `docker_build(path="/remote/path", tag="name:tag", dockerfile="Dockerfile", no_cache=False)`. Pull images with `docker_pull(image="name:tag")`. Remove images with `docker_rmi(image="name:tag", force=False)`.

For Compose projects, `project_dir` is always the path on the remote server containing `docker-compose.yml`. Use `docker_compose_ps`, `docker_compose_logs` (args: `tail`, `services`), `docker_compose_up` (args: `build`, `services`), `docker_compose_down` (args: `volumes`), `docker_compose_restart` (args: `services`), and `docker_compose_pull`.

For system overview use `docker_system_df()`, `docker_info()`, `docker_version()`, `docker_network_ls()`, `docker_volume_ls()`.

When something is broken: start with `docker_ps(all_containers=True)`, then `docker_logs(container="name", tail=200, grep="ERROR")`, then `docker_inspect(target="name")` for exit code and restart count. For Compose issues: `docker_compose_ps` -> `docker_compose_logs` -> `docker_compose_down` + `docker_compose_up(build=True)`.
