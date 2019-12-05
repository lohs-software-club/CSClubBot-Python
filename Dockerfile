FROM python:latest

# Install pipenv
RUN pip install -U pipenv

WORKDIR /bot

COPY . .

RUN pipenv install --system --deploy

ENTRYPOINT ["python3"]
CMD ["CSClubBot.py"]
