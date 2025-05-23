#!/bin/bash
set -e

create_log_dir() {
  mkdir -p ${SQUID_LOG_DIR}
  chmod -R 755 ${SQUID_LOG_DIR}
  chown -R ${SQUID_USER}:${SQUID_USER} ${SQUID_LOG_DIR}
}

create_cache_dir() {
  mkdir -p ${SQUID_CACHE_DIR}
  chown -R ${SQUID_USER}:${SQUID_USER} ${SQUID_CACHE_DIR}
}

create_squid_conf() {
  cp -n ${SQUID_SAMPLE_CONF} ${SQUID_CONF}
  chown -R ${SQUID_USER}:${SQUID_USER} ${SQUID_CONF}
}

systemctl is-active --quiet cron || systemctl enable cron --now

create_log_dir
create_cache_dir
create_squid_conf

# allow arguments to be passed to squid
if [[ ${1:0:1} = '-' ]]; then
  EXTRA_ARGS="$@"
  set --
elif [[ ${1} == squid || ${1} == $(which squid) ]]; then
  EXTRA_ARGS="${@:2}"
  set --
fi

# default behaviour is to launch squid
if [[ -z ${1} ]]; then
  if [ -f /var/run/squid.pid ]; then
    rm /var/run/squid.pid
  fi
  if [[ ! -d ${SQUID_CACHE_DIR}/00 ]]; then
    echo "Initializing cache..."
    $(which squid) -N -f ${SQUID_CONF} -z
  fi
  if [[ ! -d ${SQUID_SSL_DB_DIR}/certs ]]; then
    echo "Initializing ssl_db_dir..."
    /usr/lib/squid/security_file_certgen -c -s ${SQUID_SSL_DB_DIR} -M 20MB
  fi
  echo "Starting squid..."
  exec $(which squid) -f ${SQUID_CONF} -NYCd 1 ${EXTRA_ARGS}
else
  exec "$@"
fi
