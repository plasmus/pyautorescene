FROM python:3-alpine
COPY . /tmp/
WORKDIR /tmp/
RUN python3 setup.py install
WORKDIR /tmp/pyautorescene
RUN python3 setup.py install
RUN rm -rf /tmp
WORKDIR /
ENTRYPOINT ["autorescene.py","-vjx","-o","/complete","/process"]
