FROM mongo:latest

WORKDIR /usr/src/app

RUN apt update -y
RUN apt install -y python3 python3-pip poppler-utils
RUN pip3 install --upgrade pip

COPY ./requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
ENV PYTHONUNBUFFERED=0
ENV PYTHONIOENCODING=utf-8
ENTRYPOINT ["entrypoint.sh"]

COPY ./src /usr/src/app
