# Docker MCP - Copilot Instructions

You have access to a Docker MCP that manages containers on a remote server over SSH.
Use these tools to inspect, control, and debug the remote Docker environment.

## Quick reference

### Inspect what's running
```
docker_ps()                          # running containers
docker_ps(all_containers=True)       # all containers including stopped
docker_images()                      # available images
docker_stats()                       # CPU/memory snapshot for all containers
docker_stats(container="myapp")      # stats for a specific container
```

### Read logs
```
docker_logs(container="myapp")
docker_logs(container="myapp", tail=200)
docker_logs(container="myapp", since="1h")
docker_logs(container="myapp", since="30m", grep="ERROR")
docker_logs(container="myapp", timestamps=True, tail=50)
```

### Execute commands inside containers
```
docker_exec(container="myapp", command="env")
docker_exec(container="myapp", command="cat /etc/hosts")
docker_exec(container="myapp", command="ps aux")
docker_exec(container="db", command="psql -U postgres -c '\\l'")
```

### Lifecycle control
```
docker_stop(container="myapp")
docker_start(container="myapp")
docker_restart(container="myapp")
docker_restart(container="myapp", timeout=30)   # give it 30s to stop gracefully
docker_stop(container="a b c")                  # multiple containers at once
```

### Inspect a container or image
```
docker_inspect(target="myapp")
docker_top(container="myapp")        # processes inside the container
```

### Run a new container
```
docker_run(image="nginx:latest", name="web", ports="8080:80")
docker_run(image="alpine", command="echo hello", detach=False, rm=True)
docker_run(image="myapp:latest", name="worker", env="DEBUG=1 LOG_LEVEL=info")
docker_run(image="redis:7", name="cache", volumes="/data/redis:/data", detach=True)
```

### Remove containers / images
```
docker_rm(container="myapp")
docker_rm(container="myapp", force=True)         # force-remove running container
docker_rmi(image="myapp:old")
docker_rmi(image="myapp:old", force=True)
```

### Build an image (from path on the remote server)
```
docker_build(path="/srv/myapp", tag="myapp:latest")
docker_build(path="/srv/myapp", tag="myapp:latest", no_cache=True)
docker_build(path="/srv/myapp", tag="myapp:dev", dockerfile="Dockerfile.dev")
```

### Pull images
```
docker_pull(image="nginx:latest")
docker_pull(image="postgres:16")
```

## Docker Compose

`project_dir` is always the path on the **remote server** containing `docker-compose.yml`.

```
docker_compose_ps(project_dir="/srv/myproject")
docker_compose_logs(project_dir="/srv/myproject")
docker_compose_logs(project_dir="/srv/myproject", tail=200, since="1h")  # note: since not supported by compose logs - use tail
docker_compose_logs(project_dir="/srv/myproject", services="api worker")
docker_compose_up(project_dir="/srv/myproject")
docker_compose_up(project_dir="/srv/myproject", build=True)
docker_compose_up(project_dir="/srv/myproject", services="api")
docker_compose_restart(project_dir="/srv/myproject")
docker_compose_restart(project_dir="/srv/myproject", services="api")
docker_compose_down(project_dir="/srv/myproject")
docker_compose_down(project_dir="/srv/myproject", volumes=True)
docker_compose_pull(project_dir="/srv/myproject")
```

## System

```
docker_system_df()       # disk usage - images, containers, volumes
docker_info()            # daemon config, runtime info
docker_version()         # engine version
docker_network_ls()      # networks
docker_volume_ls()       # volumes
```

## Common workflows

**"Something is broken - where do I start?"**
1. `docker_ps(all_containers=True)` - find stopped/restarting containers
2. `docker_logs(container="<name>", tail=200, grep="ERROR")` - check for errors
3. `docker_inspect(target="<name>")` - check restart count, exit code, env

**"Deploy a new image"**
1. `docker_pull(image="myapp:v2")` or `docker_build(...)`
2. `docker_stop(container="myapp")`
3. `docker_rm(container="myapp")`
4. `docker_run(image="myapp:v2", name="myapp", ...)`

**"Compose project won't come up"**
1. `docker_compose_ps(project_dir="...")` - check service states
2. `docker_compose_logs(project_dir="...", tail=100)` - read all service logs
3. `docker_compose_down(project_dir="...")` then `docker_compose_up(..., build=True)`
