FROM python:3.5

WORKDIR /usr/src/restcli

ADD . /usr/src/restcli

RUN make install

ENTRYPOINT ["restcli"]
