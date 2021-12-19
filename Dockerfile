FROM python:3.6-slim-stretch

COPY . /
RUN pip install -r requirements.txt

EXPOSE 5000
CMD python application.py