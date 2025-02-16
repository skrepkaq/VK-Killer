FROM python:3.9.5-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /var/log && \
    touch /var/log/django.log && \
    chmod 666 /var/log/django.log

CMD ["/usr/local/bin/gunicorn", "--config", "gunicorn.conf.py", "social.asgi:application"]