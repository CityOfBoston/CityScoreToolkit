FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install --no-install-recommends -y pkg-config \
    libxft-dev libfreetype6 libfreetype6-dev
ADD . /code/
RUN python manage.py makemigrations
RUN python manage.py migrate
EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000