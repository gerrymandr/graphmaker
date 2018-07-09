FROM continuumio/miniconda3

COPY . /code

WORKDIR /code

RUN python setup.py install

ENTRYPOINT [ "bash" ]
