FROM python:latest

#WORKDIR /usr/local/bin

COPY CSClubBot.py .

CMD ["CSClubBot.py"]
