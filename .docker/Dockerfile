FROM python:3.6-alpine

# Install required packages and remove the apt packages cache when done.
#apk update && apk upgrade && \
RUN apk update 
RUN apk add bash \
	jpeg-dev \
	zlib-dev \
	libffi-dev \
	python3-dev \
	openssh \
	gcc \
	build-base \
	linux-headers \
	pcre-dev \
	postgresql-dev \
	musl-dev \
	libxml2-dev \
	libxslt-dev \
	nginx \
	curl \
	supervisor \
	git && \
	python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache

# install uwsgi now because it takes a little while
RUN pip3 install uwsgi

# setup all the configfiles
COPY .nginx/nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY .nginx/nginx-app.conf /etc/nginx/sites-available/default
COPY .nginx/supervisor-app.conf /home/docker/code/

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.
COPY requirements.txt /home/docker/code/
RUN pip3 install -r /home/docker/code/requirements.txt

# add (the rest of) our code
COPY . /home/docker/code/
COPY .nginx/uwsgi.ini /home/docker/code/
COPY .nginx/uwsgi_params /home/docker/code/


# install django, normally you would remove this step because your project would already
# be installed in the code/app/ directory
# RUN django-admin.py startproject website /home/docker/code/app/

WORKDIR /home/docker/
EXPOSE 80
CMD ["supervisord", "-n", "-c", "/home/docker/code/supervisor-app.conf"]
