# monolog
##Singletoned MongoDB logger + std logger


####Requirements:
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
