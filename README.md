# python_web_server_template

## Test APIs

```shell
curl -X GET http://127.0.0.1:8000
# {"Hello":"World"}
curl -X GET http://127.0.0.1:8000/get/123?q=hi
# {"item_id":123,"q":"hi"}
curl -X POST -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"hi\",\"price\":0}" http://127.0.0.1:8000/post
# {"item_name":"hi","item_price":0.0}
```