FROM python:3.6.5

RUN apt-get update
RUN apt-get install -y nginx
RUN apt-get install -y supervisor
RUN apt-get install -y vim
RUN apt-get install -y netcat-openbsd
RUN rm /etc/nginx/sites-available/default && rm /etc/nginx/nginx.conf

ADD . /app

COPY ./proxy/nginx/conf.d /etc/nginx/conf.d
COPY ./proxy/nginx/nginx.conf /etc/nginx/nginx.conf

COPY ./proxy/supervisor/conf.d /etc/supervisor/conf.d

EXPOSE 5000

WORKDIR /app

RUN pip install -r requirements.txt
RUN chmod 700 main.py
RUN chmod 700 start.sh

ENTRYPOINT ["./start.sh"]
