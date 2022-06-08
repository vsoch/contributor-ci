FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /code
COPY . /code
RUN pip3 install -e .
ENTRYPOINT ["/bin/bash", "/code/entrypoint.sh"]
