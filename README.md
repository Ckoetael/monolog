# monolog Python package
## Singletoned MongoDB logger + std logger

### Installation
```sh 
pip install git+ssh://git@gitlab.crpo.su/vgds/monolog.git
```

#### Requirements:
* pymongo>=3.10.1

#### Using:
```python
logger = MongoLogger()
ssid = "123123321"
msg = "test critical msg"
dump = {
    "body": "test_body",
    "info": "test_info"
}
logger.cricital(ssid, msg, dump)
```
Config must be in config directory, previously will be used *monolog.local.json*
#### Config example
```json
{
  "serv": "localhost",
  "port": 27017,
  "username": "root",
  "authSource": "admin",
  "authMechanism":"SCRAM-SHA-1",
  "password": "toor",
  "dataBase": "logs",
  "currentLevel": "debug",
  "collectionName": "test_collection_%Y%m", #datatime formated
  "stdLoggerDuplicate": false,
  "node": {
            "host": "myService",
            "ip": "127.0.0.1"
  }
}
```