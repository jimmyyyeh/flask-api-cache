# flask-api-cache
**A package for caching flask api with custom key.**


## Description:
A decorator for python flask api.

You can set cache in your **memory** or with **redis instance**,<br>
the key will be generated by the following rule:<br>
`{YOUR_FUNCTION_NAME}:{REQUEST_FULL_PATH}`<br>
or you can use your custom key function by key_func args,<br>
the value will be your function return value.<br>

## How To Use:

### Import
```python
from flask_api_cache import ApiCache
```

### Parameters

|name|required|description|
|----|--------|-----------|
|redis|no|if you want to caching data in redis, you can call ApiCache with a redis instance.|
|expired_time|no|set your expired time with **seconds**, the default value is 24 * 60 * 60 seconds (1 day)|
|key_func|no|the function which you want to make custom key|

### Cache Without Redis
```python
@app.route('/example_1/<string:name>')
@ApiCache(expired_time=10)
def example_1(name):
    """
    caching data in memory with default key.
        - http://0.0.0.0:5000/example_1/jimmy
    :param name:
    :return:
    """
    return jsonify(f'Hi {name}, it is {datetime.now()}')
```
If you request for **http://0.0.0.0:5000/example_1/jimmy**,<br>
it will set a 10 seconds cache by key: `example_1:/example_1/Jimmy?`,<br>
                     with value: `Hi jimmy, it is 2020-10-23 16:06:27.996358.`,
in your memory, it will be cleared after api service restart.

### Cache With Redis
```python
@app.route('/example_3/<string:items>')
@ApiCache(redis=redis_instance, expired_time=10)
def example_3(items):
    """
    caching data in redis instance with default key.
        - http://0.0.0.0:5000/example_3/coffee
    :param items:
    :return:
    """
    return jsonify(f'You bought {items} at {datetime.now()}')
```
If you request for **http://0.0.0.0:5000/example_3/coffee**,<br>
it will set a 10 seconds cache by key: `example_3:/example_3/coffee?`,<br>
                     with value: `You bought coffee at 2020-10-23 16:06:59.904216`,
in your redis instance.

### Cache With Custom Function
```python
def custom_func_2(**kwargs):
    items = kwargs.get('items')
    price = kwargs.get('price')
    keys = f'{items}:{price}'
    return keys

@app.route('/example_4/<string:items>/<int:price>')
@ApiCache(redis=redis_instance, key_func=custom_func_2, expired_time=10)
def example_4(items, price):
    """
    caching data in redis instance with custom function.
        - http://0.0.0.0:5000/example_4/coffee/20
    :param items:
    :param price:
    :return:
    """
    return jsonify(f'You bought {items} at {datetime.now()}, it cost ${price}')

```
If you request for **http://0.0.0.0:5000/example_4/coffee/20** ,<br>
it will set a 10 seconds cache by key: `coffee:20`,<br>
                     with value: `You bought coffee at 2020-10-23 16:07:59.818357, it cost $20`,
in your memory, it will be cleared after service restart.

### [Sample Code](https://github.com/chienfeng0719/flask-api-cache/blob/develop/example.py)
```python
import redis
from flask import Flask, request, jsonify
from flask_api_cache import ApiCache
from datetime import datetime

app = Flask(__name__)

# init redis instance
redis_instance = redis.StrictRedis(host='localhost', port=6379)


def custom_func_1(**kwargs):
    name = kwargs.get('name')
    age = kwargs.get('age')
    sex = kwargs.get('sex')
    keys = f'{name}:{age}:{sex}'
    return keys


def custom_func_2(**kwargs):
    items = kwargs.get('items')
    price = kwargs.get('price')
    keys = f'{items}:{price}'
    return keys


@app.route('/example_1/<string:name>')
@ApiCache(expired_time=10)
def example_1(name):
    """
    caching data in memory with default key.
        - http://0.0.0.0:5000/example_1/jimmy
    :param name:
    :return:
    """
    return jsonify(f'Hi {name}, it is {datetime.now()}')


@app.route('/example_2/<string:name>/<int:age>')
@ApiCache(expired_time=10, key_func=custom_func_1)
def example_2(name, age):
    """
    caching data in memory with custom function.
        - http://0.0.0.0:5000/example_2/jimmy/18?sex=boy
    :param name:
    :param age:
    :return:
    """
    sex = request.args.get('sex', 'boy', str)
    return jsonify(f'{name} is a {age} years old {sex}. {datetime.now()}')


@app.route('/example_3/<string:items>')
@ApiCache(redis=redis_instance, expired_time=10)
def example_3(items):
    """
    caching data in redis instance with default key.
        - http://0.0.0.0:5000/example_3/coffee
    :param items:
    :return:
    """
    return jsonify(f'You bought {items} at {datetime.now()}')


@app.route('/example_4/<string:items>/<int:price>')
@ApiCache(redis=redis_instance, key_func=custom_func_2, expired_time=10)
def example_4(items, price):
    """
    caching data in redis instance with custom function.
        - http://0.0.0.0:5000/example_4/coffee/20
    :param items:
    :param price:
    :return:
    """
    return jsonify(f'You bought {items} at {datetime.now()}, it cost ${price}')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
```

---
<a href="https://www.buymeacoffee.com/jimmyyyeh" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" height="40" width="175"></a>

**Buy me a coffee, if you like it!**
