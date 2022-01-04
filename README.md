# sadpandabot matrix edition

A matrix bot bot which grabs E-Hentai metadata for E-Hentai links in the chat using simplematrixbotlib.

## Installing and running

Use the docker image for simple installation, otherwise, use `python >= 3.5` and install the packages in `requirements.txt`. Also set the `HOMESERVER`, `USERNAME`, `PASSWORD` env variable (or edit the code to use your credentials).

```
git clone https://github.com/Ryu1845/sadpandabot
cd sadpandabot
pip install -r requirements.txt
python3 sadpandabot.py
```

### docker

```
docker run --env-file=.env cotangent/sadpandabot:latest
```
