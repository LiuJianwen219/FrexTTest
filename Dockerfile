FROM centos/python-36-centos7

COPY requirements.txt /tmp
RUN ["pip", "install", "-r", "/tmp/requirements.txt"]

# copy source
COPY ./ /FrexT

# create workspace
WORKDIR /FrexT/server

# start
# ENTRYPOINT ["python", "RabbitMQCompileServer.py"]

## make environment
#RUN ["pip", "install", "-r", "requirements.txt"]
