# monolog Python package
## MongoDB logger + std logger

### Installation
```sh 
pip install git+ssh://git@github.com/Ckoetael/monolog.git
```

#### Requirements:
* pymongo>=3.10.1

#### Using:
```python
logger = MongoLogger(__name__, pid)
msg = "test critical msg"
dump = {
    "body": "test_body",
    "info": "test_info"
}
logger.cricital(msg, dump)
```
Config must be in config directory, *monolog.local.json* will be merged on monolog.json 
#### Config example
``` json
{
  "connection": {
    "serv": "mongo",
    "port": 27017,
    "username": "root",
    "authSource": "admin",
    "authMechanism": "SCRAM-SHA-1",
    "password": "pwd",
    "dataBase": "logs_services"
  },
  "currentLevel": "debug",
  "mongoLoggerDuplicate": true,
  "stdLoggerDuplicate": true,
  "node": {
    "host": "myService",
    "ip": "127.0.0.1"
  }
}
```
Example monolog.local.json will be merged on monolog.json
``` json
{
  "connection": {
    "serv": "mongo_prod",
    "username": "toor",
    "password": "password",
  },
  "currentLevel": "info",
  "stdLoggerDuplicate": true,
}
```