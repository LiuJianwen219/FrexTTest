FROM centos/python-36-centos7

COPY requirements.txt /tmp
RUN ["pip", "install", "-r", "/tmp/requirements.txt"]

# copy source
COPY ./ /FrexT

# create workspace
#WORKDIR /FrexT/server
WORKDIR /FrexT

# start
# ENTRYPOINT ["python", "RabbitMQCompileServer.py"]
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8030", "--insecure"]

## make environment
#RUN ["pip", "install", "-r", "requirements.txt"]
