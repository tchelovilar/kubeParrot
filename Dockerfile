FROM alpine

RUN apk update \
    && apk add bash py-pip vim\
    && pip install kubernetes

COPY src /

ENTRYPOINT ["python","-u","kubeParrot.py"]
