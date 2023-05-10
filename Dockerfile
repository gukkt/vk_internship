FROM python:3.10

ENV PYTHONUNBUFFERED=1

#RUN groupadd -r app && useradd --no-log-init -r -g app app
RUN mkdir /app && chown -R 1000:1000 /app

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN echo '#!/bin/sh\n\
\n\
if [ "$1" = "test" ]; then\n\
  python manage.py test\n\
else\n\
  python manage.py migrate\n\
  python manage.py runserver 0.0.0.0:8000\n\
fi' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh \
    && chown 1000:1000 /app/entrypoint.sh

USER 1000

ENTRYPOINT ["./entrypoint.sh"]
