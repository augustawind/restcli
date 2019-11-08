FROM python:3.6

ARG collection=
ARG env=
ARG autosave=0
ARG quiet=0
ARG raw=0

ENV RESTCLI_COLLECTION ${collection}
ENV RESTCLI_ENV ${env}
ENV RESTCLI_AUTOSAVE ${autosave}
ENV RESTCLI_QUIET ${quiet}
ENV RESTCLI_RAW_OUTPUT ${raw}

WORKDIR /usr/src/restcli

ADD . /usr/src/restcli

RUN pip install -r requirements.txt

RUN pip install .

ENTRYPOINT ["restcli"]
