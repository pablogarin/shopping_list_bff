FROM python:3.8-slim-buster
ARG DB_FOLDER=/opt/api

WORKDIR /app

COPY ./api ./api
COPY ./requirements.txt ./requirements.txt
COPY ./gunicorn.config.py ./gunicorn.config.py

RUN python -m pip install -r requirements.txt
RUN mkdir ${DB_FOLDER}

EXPOSE 5000
ENV DB_PATH=${DB_FOLDER}/database.db

CMD ["gunicorn", "-c", "gunicorn.config.py", "api.api:create_flask_app()"]