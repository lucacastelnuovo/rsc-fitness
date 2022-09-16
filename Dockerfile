FROM alpine:latest

ARG RSC_USERNAME=
ARG RSC_PASSWORD=
ARG S3_ACCESS_KEY=
ARG S3_SECRET_KEY=

ENV PYTHONUNBUFFERED=1
ENV MUSL_LOCPATH="/usr/share/i18n/locales/musl"

RUN apk add --update --no-cache \
    python3 \
    musl-locales \
    musl-locales-lang

ENV LC_ALL nl_NL.UTF-8
ENV LANG nl_NL.UTF-8
ENV LANGUAGE nl_NL.UTF-8

RUN ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip

RUN pip3 install --no-cache --upgrade pip
RUN pip3 install --no-cache --upgrade minio
RUN pip3 install --no-cache --upgrade scrapy scrapyscript

COPY . /app

RUN touch crontab.tmp \
    && echo '* * * * * python /app/refresh.py >> /dev/null 2>&1' > crontab.tmp \
    && crontab crontab.tmp \
    && rm -rf crontab.tmp

CMD ["crond", "-f", "-d", "8"]
