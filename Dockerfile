FROM python:3.5.1

WORKDIR /code

RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install

COPY . .

WORKDIR graphmaker

ENTRYPOINT ["bash"]
