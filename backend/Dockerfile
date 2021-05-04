FROM mongo:latest

WORKDIR /usr/src/app

RUN apt update -y
RUN apt install -y python3 python3-pip
RUN pip3 install --upgrade pip

COPY ./requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src /usr/src/app
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
