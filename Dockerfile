FROM contiuumio/miniconda3:latest

WORKDIR /usr/src

RUN git clone https://github.com/gerrymandr/RunDMCMC.git
WORKDIR /usr/src/RunDMCMC
RUN python setup.py build
RUN python setup.py develop

COPY ./graphmaker /code

WORKDIR /code

CMD [ "python", "get_vtds.py" ]