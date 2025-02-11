FROM debian:bookworm AS builder

ARG DEBIAN_FRONTEND=noninteractive

ENV SOURCEURL=https://github.com/squid-cache/squid/releases/download/SQUID_6_13/squid-6.13.tar.gz

ENV builddeps=" \
    build-essential \
    checkinstall \
    curl \
    devscripts \
    libcrypto++-dev \
    libssl-dev \
    openssl \
    "
ENV requires=" \
    libatomic1, \
    libc6, \
    libcap2, \
    libcomerr2, \
    libdb5.3, \
    libdbi-perl, \
    libecap3, \
    libexpat1, \
    libgcc1, \
    libgnutls30, \
    libgssapi-krb5-2, \
    libkrb5-3, \
    libldap-2.5-0, \
    libltdl7, \
    libnetfilter-conntrack3, \
    libnettle8, \
    libpam0g, \
    libsasl2-2, \
    libstdc++6, \
    libxml2, \
    netbase, \
    openssl \
    "

RUN echo "deb-src [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list.d/source.list \
 && echo "deb-src [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list.d/source.list \
 && apt-get -qy update \
 && apt-get -qy install ${builddeps} \
 && apt-get -qy upgrade \
 && apt-get -qy build-dep squid \
 && mkdir /build \
 && curl -o /build/squid-source.tar.gz -L ${SOURCEURL} \
 && cd /build \
 && tar --strip=1 -xf squid-source.tar.gz \
 && ./configure --prefix=/usr \
        --with-build-environment=default \
        --localstatedir=/var \
        --libexecdir=/usr/lib/squid \
        --datadir=/usr/share/squid \
        --sysconfdir=/etc/squid \
        --mandir=/usr/share/man \
        --enable-inline \
        --disable-arch-native \
        --enable-async-io=8 \
        --enable-storeio="ufs,aufs,diskd,rock" \
        --enable-removal-policies="lru,heap" \
        --enable-delay-pools \
        --enable-cache-digests \
        --enable-icap-client \
        --enable-follow-x-forwarded-for \
        --enable-auth-basic="DB,fake,getpwnam,LDAP,NCSA,PAM,POP3,RADIUS,SASL,SMB" \
        --enable-auth-digest="file,LDAP" \
        --enable-auth-negotiate="kerberos,wrapper" \
        --enable-auth-ntlm="fake,SMB_LM" \
        --enable-external-acl-helpers="file_userip,kerberos_ldap_group,LDAP_group,session,SQL_session,time_quota,unix_group,wbinfo_group" \
        --enable-security-cert-validators="fake" \
        --enable-storeid-rewrite-helpers="file" \
        --enable-url-rewrite-helpers="fake" \
        --enable-eui \
        --enable-esi \
        --enable-icmp \
        --enable-zph-qos \
        --enable-ecap \
        --disable-translation \
        --with-swapdir=/var/spool/squid \
        --with-logdir=/var/log/squid \
        --with-pidfile=/var/run/squid.pid \
        --with-filedescriptors=65536 \
        --with-large-files \
        --with-default-user=proxy \
        --enable-linux-netfilter \
        --enable-ssl --enable-ssl-crtd --with-openssl \
 && make -j$(awk '/^processor/{n+=1}END{print n}' /proc/cpuinfo) \
 && checkinstall -y -D --install=no --fstrans=no --requires="${requires}" \
        --pkgname="squid"

RUN mv /build/*.deb /build/squid.deb

FROM debian:bookworm-slim

LABEL maintainer="Misterbabou"

ARG DEBIAN_FRONTEND=noninteractive

ENV SQUID_CACHE_DIR=/var/spool/squid \
    SQUID_LOG_DIR=/var/log/squid \
    SQUID_SSL_DB_DIR=/conf/ssl_db \
    SQUID_USER=proxy \
    SQUID_SAMPLE_CONF=/opt/squid.conf.sample \
    SQUID_CONF=/conf/squid.conf \
    LOGROTATE_RETENTION=30

COPY ./squid.conf.sample ${SQUID_SAMPLE_CONF}

COPY --from=builder /build/squid.deb /tmp/squid.deb

RUN apt-get update && apt-get install -y logrotate systemctl cron

COPY ./squid-logrotate /etc/logrotate.d/squid

RUN apt -qy install libssl3 /tmp/squid.deb \
 && rm -rf /var/lib/apt/lists/*

COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
