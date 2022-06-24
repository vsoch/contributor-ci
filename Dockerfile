FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip git
WORKDIR /code
COPY . /code
RUN pip3 install --upgrade pip && pip3 install -e .
ENTRYPOINT ["/bin/bash", "/code/entrypoint.sh"]
