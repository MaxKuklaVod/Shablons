FROM python:3.10.14 as build
WORKDIR /app
EXPOSE 5000

RUN pip3 install --upgrade pip
RUN pip3 install -U Flask
RUN pip3 install -U flask-restplus

COPY Src /app/Src
COPY main.py /app/

RUN echo $(ls -1)

CMD [ "python", "main.py" ]

