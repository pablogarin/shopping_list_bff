FROM python:3.8-slim-buster
ARG DB_FOLDER=/opt/api

WORKDIR /app

COPY ./api ./api
COPY ./requirements.txt ./requirements.txt
COPY ./wsgi.py ./wsgi.py

RUN python -m pip install -r requirements.txt
RUN mkdir ${DB_FOLDER}

EXPOSE 5000
ENV DB_PATH=${DB_FOLDER}/database.db

CMD ["gunicorn", "-w1", "-b0.0.0.0:5000", "--timeout", "30", "wsgi:app"]