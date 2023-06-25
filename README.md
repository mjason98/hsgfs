# hsgfs
A simple GFS implementation for a Harbour.Spase assigment

## Build and run the servers

```shell
docker-compose build
docker-compose up -d
```

## Use the client

To use the client to create, delete and get a file, it will be necessary to create a python enviromnet to run the client:

```shell
cd client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

to use the cliente chose from the following commands:
- add    Add a file
- rm     Remove a file
- get    Download a file
- desc   Describe a file, with its name and size


for example, inside client folder with the environment activated:
```shell
python main.py add filename.ext
```

for more help use:
```shell
python main.py -h
```
