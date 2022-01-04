FROM python:latest

WORKDIR /app
COPY . /app/

# build dependencies
RUN python -m pip install -U pip && python -m pip install -r requirements.txt

CMD ["python", "-u", "sadpandabot.py"]
