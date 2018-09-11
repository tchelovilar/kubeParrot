FROM alpine:3.7

RUN apk update && \
    apk add --no-cache py-pip && \
    pip install --no-cache kubernetes && \
    # requests package need run after kubernetes package to solve modules dependencies.
    pip install --no-cache --disable-pip-version-check requests

COPY src /

ENTRYPOINT ["python","-u","kubeParrot.py"]
