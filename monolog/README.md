# monolog
## Singletoned MongoDB logger + std logger


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
  "std_logger_duplicate": false,
  "node": {
            "host": "myService",
            "ip": "127.0.0.1"
  }
}
```