# Docker Squid

---
[![Docker Pulls](https://img.shields.io/docker/pulls/misterbabou/squid.svg?logo=docker)](https://hub.docker.com/r/misterbabou/squid)
[![GitHub Release](https://img.shields.io/github/release/Misterbabou/docker-squid.svg?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/docker-squid/releases/latest)
[![GitHub last commit](https://img.shields.io/github/last-commit/Misterbabou/docker-squid?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/docker-squid/commits/main)
[![MIT Licensed](https://img.shields.io/github/license/Misterbabou/docker-squid.svg?logo=github&logoColor=959DA5)](https://github.com/Misterbabou/docker-squid/blob/main/LICENSE.md)
---

Docker image of squid based on a bookworm debian-slim image.

The Goal of this repo is to build a debian based docker running always the last version of squid release.

> [!IMPORTANT]
>
>A recent security Audit was made on Squid showing multiple vulnerabilities. Most of them are not resolved yet. 
https://github.com/MegaManSec/Squid-Security-Audit. Thanks to the work of squid team some of them are patched on recent releases 6.X but most linux distro do not have a recent squid package available.
The goal of those builds is to provide a simple running docker image resolving security issues patched on new squid releases.

## Version TAG

All docker image are build with the following format : 
```
<squid_package_version>.<docker-squid-version>
```
For instance for Squid version `6.9` the first image tag will be `6.9.0` 
If minor changes are made to the docker (without changing the squid version) last degit will be incremented. 


> [!WARNING]
>
> Starting on version `6.13.9` arm64 version is available with image tag `<squid_package_version>.<docker-squid-version>-arm`

## Configuration

> [!NOTE]
>
>It's recommanded to use docker compose to run this application. [Install documentation](https://docs.docker.com/compose/install/)

Create the `docker-compose.yml` file:
```
services:
    squid:
        container_name: squid
        image: misterbabou/squid:latest
        restart: unless-stopped
        ports:
          - 3128:3128
        environment:
          - TZ=Europe/Paris #Set your timezone
          #- LOGROTATE_RETENTION=30 #Days retention for squid log; default is 30
          #- SQUID_ACCESS_LOG_STDOUT=false #Display logs in docker logs; default is false
        volumes:
          - ./conf:/conf
          - ./cache:/var/spool/squid
          - ./log:/var/log/squid
```
> [!NOTE]
>
>If you are running on a arm64 platform use the following image in the docker-compose.yml: `image: misterbabou/squid:latest-arm`

Run the application
```
docker compose up -d
```

## Apply changes on squid.conf

change the default configuration in `./conf/squid.conf`

### Check the configuration
```
docker exec squid bash -c "/usr/sbin/squid -f \${SQUID_CONF} -k parse"
```
### Apply the configuration
```
docker exec squid bash -c "/usr/sbin/squid -f \${SQUID_CONF} -k reconfigure"
```

## To Do

:heavy_check_mark: Logrotate log files (added in 6.9.1)
