FROM alpine

RUN apk update \
    && apk add py-pip \
    && pip install --upgrade pip \
    && pip install kubernetes \
    # requests package need run after kubernetes package to solve modules dependencies.
    && pip install requests \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache/pip

COPY src /

ENTRYPOINT ["python","-u","kubeParrot.py"]
