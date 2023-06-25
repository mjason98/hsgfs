# hsgfs
A simple GFS implementation for a Harbour.Spase assigment

## First Step

First, clone this repository
```shell
git clone https://github.com/mjason98/hsgfs
cd hsgfd
```

## Build and run the servers

Then, fun the following command to build and put to runing the chunk servers and the server manager:

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

| Command |              Description                |
|:-------:|-----------------------------------------|
| add     | Add a file                              |
| rm      | Remove a file                           |
| get     | Download a file                         |
| desc    | Describe a file, with its name and size |


for example, inside client folder with the environment activated:
```shell
python main.py add filename.ext
```

for more help use:
```shell
python main.py -h
```
