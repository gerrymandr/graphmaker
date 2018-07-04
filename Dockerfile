FROM python:3.6.5

RUN pip install pipenv

COPY ./Pipfile ./Pipfile.lock /code/

WORKDIR /code

RUN pipenv install

COPY ./graphmaker .

ENTRYPOINT [ "bash" ]
