FROM alpine

RUN apk update \
    && apk add py-pip \
    && pip install --upgrade pip \
    && pip install kubernetes \
    && pip install requests \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache/pip

COPY src /

ENTRYPOINT ["python","-u","kubeParrot.py"]
