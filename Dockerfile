FROM alpine:3.7

RUN apk update && \
    apk add --no-cache py-pip && \
    apk add --no-cache --virtual devtools \
        gcc \
        python-dev \
        musl-dev \
        libffi-dev \
        openssl-dev && \
    pip install --no-cache --disable-pip-version-check kubernetes && \
    # requests package need run after kubernetes package to solve modules dependencies.
    pip install --no-cache --disable-pip-version-check requests && \
    apk del devtools

COPY src /

ENTRYPOINT ["python","-u","kubeParrot.py"]
