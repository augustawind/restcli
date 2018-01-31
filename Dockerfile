FROM python:3.6

WORKDIR /usr/src/restcli

ADD . /usr/src/restcli

RUN invoke build

ENTRYPOINT ["restcli"]
