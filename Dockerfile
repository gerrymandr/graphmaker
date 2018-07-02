FROM maxhully/vrdi:latest

WORKDIR /usr/src

RUN git clone https://github.com/gerrymandr/RunDMCMC.git
WORKDIR /usr/src/RunDMCMC
RUN python setup.py build
RUN python setup.py install

COPY ./graphmaker /code

WORKDIR /code

CMD [ "python", "get_vtds.py" ]