FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /code
COPY . /code
RUN pip3 install --upgrade pip && pip3 install -e . && \
    pip3 install git+https://github.com/researchapps/scraper.git@update/python-support
ENTRYPOINT ["/bin/bash", "/code/entrypoint.sh"]
