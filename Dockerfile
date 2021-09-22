FROM python:3.9.7-buster AS builder

COPY . /src/

WORKDIR /src
RUN python -m pip --no-cache-dir wheel $PWD -w wheel

FROM python:3.9.7-slim-buster

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=0
ENV LANG C.UTF-8
ENV ID=26171

COPY --from=builder /src/wheel/* /tmp/

RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends tini; \
    python -m pip --no-cache-dir install -f /tmp/ http-nudger -U; \
    apt-get autoremove -y; \
    apt-get clean -y; \
    rm -rf \
    /var/cache/debconf/* \
    /var/lib/apt/lists/* \
    /var/log/* \
    /tmp/* \
    /var/tmp/*;

RUN set -ex; \
    addgroup --gid ${ID} http-nudger; \
    adduser --gid ${ID} --uid ${ID} --gecos "" --disabled-password --home /home/http-nudger http-nudger; \
    chown -R http-nudger:http-nudger /home/http-nudger

WORKDIR /home/http-nudger
USER ${ID}

RUN /usr/local/bin/http-nudger --help

ENTRYPOINT ["/usr/bin/tini", "--", "http-nudger"]
