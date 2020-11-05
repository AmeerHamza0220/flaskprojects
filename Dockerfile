FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apt install python3-pip
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
COPY ./requirements.txt /var/www/requirements.txt
RUN pip3 install -r /var/www/requirements.txt
