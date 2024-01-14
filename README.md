# squid

Docker image of squid based on a bookworm debian-slim image.

The Goal of this repo is to build a debian based docker running always the last version of squid release.

## Important note 

A recent security Audit was made on Squid showing multiple vulnerabilities. Most of them are not resolved yet. 

https://github.com/MegaManSec/Squid-Security-Audit

Thanks to the work of squid team some of them are patched on recent releases 6.X but most linux distro do not have a recent squid package available.

The goal of this builds is to provide a simple running docker image resolving security issues patched on new squid releases.

## Configuration

It's recommanded to use docker compose to run this application


Use the provided docker-compose.yml or create `docker-compose.yml` file:
```
version: '3'
services:
    squid:
        container_name: squid
        image: misterbabou/squid:latest
        restart: unless-stopped
        ports:
            - 3128:3128
        volumes:
            - ./conf:/conf
            - ./cache:/var/spool/squid
            - ./log:/var/log/squid
```


:warning: Make sure to copy or to have a basic configuration on your directory named squid.conf on your volume link to /conf

Create conf directory (depending on your volume path):
```
mkdir conf
```

Create a conf file named squid.conf : 
```
sudo tee -a ./conf/squid.conf <<EOF
# Default Squid Conf

# 100 Mo cache
cache_dir ufs /var/spool/squid 100 16 256

#################################### ACL ####################################

acl lan src 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 # RFC1918
acl Safe_ports port 80 
acl Safe_ports port 443
############################################################################

# Rules
http_access deny !Safe_ports
http_access allow lan
http_access deny

# Listen port
http_port 3128  
EOF
```

Run the application
```
docker-compose up -d
```

## Apply changes on squid.conf

### Check the configuration
```
docker exec squid bash -c "/usr/sbin/squid -f /conf/squid.conf -k parse"
```
### Apply the configuration
```
docker exec squid bash -c "/usr/sbin/squid -f /conf/squid.conf -k reconfigure"
```

## To Do

- Logrotate log files