FROM python:3.11

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y netcat-openbsd

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .  

RUN mkdir -p /app/static
RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --noinput 

RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT ["/app/docker/entrypoint.sh"]
