FROM python:3.6

WORKDIR /usr/src/restcli

ADD . /usr/src/restcli

RUN pip install -r requirements.txt

RUN pip install .

ENTRYPOINT ["restcli"]
