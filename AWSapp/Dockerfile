FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential libsm6 libxext6 libxrender-dev
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 5000
RUN echo ifconfig
ENTRYPOINT ["python3"]
CMD ["findNamesAPI.py"]