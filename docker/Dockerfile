FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED=TRUE

# copy the dependencies file to the working directory
COPY . /baseline

# set the working directory in the container
WORKDIR /baseline

# install dependencies
RUN pip3 install -r requirements.txt

# command to run on container start
ENTRYPOINT  [ "python3", "src/baseline_script.py"]