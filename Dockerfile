FROM phusion/baseimage:0.11

MAINTAINER Petr Galko <petr3460@gmail.com>


# Update OS
RUN set -x \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -qq \
    && apt-get upgrade -qq \
    && apt-get install -qq \
        tzdata \
        nginx-light \
	python3-distutils \
    && apt-get clean

# Locale setup
RUN set -x \
    && locale-gen ru_RU \
    && locale-gen ru_RU.UTF-8 \
    && update-locale
ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

# TimeZone
RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

RUN set -x \
    && rm -rf /usr/bin/python \
    && ln /usr/bin/python3 /usr/bin/python

# Allow www-data group to create pid files in /var/run -> /run
RUN chown root:www-data /run && chmod 775 /run

# Install pip
RUN set -x \
    && curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py \
    && python /tmp/get-pip.py \
    && rm /tmp/get-pip.py

# Prepare packages
RUN mkdir -p /opt/app
WORKDIR /opt/app
COPY requirements.txt /opt/app
RUN set -x && pip install -r requirements.txt

# Copy configuration dirs
COPY etc/ /etc/
RUN chmod 744 /etc/cron.d/ -R

# Copy project
COPY monitoring/ /opt/app
RUN chown -R www-data:www-data /opt/app

