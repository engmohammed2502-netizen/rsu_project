FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# Default CMD; docker-compose overrides with migrate + create_root_user + gunicorn
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8000"]
