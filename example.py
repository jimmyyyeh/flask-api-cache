# -*- coding: utf-8 -*-
"""
      ┏┓       ┏┓
    ┏━┛┻━━━━━━━┛┻━┓
    ┃      ☃      ┃
    ┃  ┳┛     ┗┳  ┃
    ┃      ┻      ┃
    ┗━┓         ┏━┛
      ┗┳        ┗━┓
       ┃          ┣┓
       ┃          ┏┛
       ┗┓┓┏━━━━┳┓┏┛
        ┃┫┫    ┃┫┫
        ┗┻┛    ┗┻┛
    God Bless,Never Bug
"""
import redis
from flask import Flask, request, jsonify
from flask_api_cache import ApiCache
from datetime import datetime

app = Flask(__name__)

redis_instance = redis.StrictRedis(host='redis', port=6379)


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


"""GET"""


@app.route('/example_1/<string:name>', methods=['GET'])
@ApiCache(expired_time=10)
def example_1(name):
    """
    caching data in memory with default key.
        - http://0.0.0.0:5000/example_1/jimmy
    :param name:
    :return:
    """
    return jsonify(f'Hi {name}, it is {datetime.now()}')


@app.route('/example_2/<string:name>/<int:age>', methods=['GET'])
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


@app.route('/example_3/<string:items>', methods=['GET'])
@ApiCache(redis=redis_instance, expired_time=10)
def example_3(items):
    """
    caching data in redis instance with default key.
        - http://0.0.0.0:5000/example_3/coffee
    :param items:
    :return:
    """
    return jsonify(f'You bought {items} at {datetime.now()}')


@app.route('/example_4/<string:items>/<int:price>', methods=['GET'])
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


"""POST / PUT / DELETE"""


@app.route('/example_5/<string:name>', methods=['POST', 'PUT', 'DELETE'])
@ApiCache(expired_time=10)
def example_5(name):
    """
    caching data in memory with default key.
        - http://0.0.0.0:5000/example_5/jimmy
        - payload:
            {
                "items": "coffee",
                "price": 18
            }
    :param name:
    :return:
    """
    payload = request.json
    result = dict()
    result['payload'] = payload
    result['greeting'] = f'Hi {name}, it is {datetime.now()}'
    return jsonify(result)


@app.route('/example_6/<string:name>', methods=['POST', 'PUT', 'DELETE'])
@ApiCache(redis=redis_instance, expired_time=10)
def example_6(name):
    """
    caching data in redis instance with default key.
        - http://0.0.0.0:5000/example_6/jimmy
        - payload:
            {
                "items": "coffee",
                "price": 18
            }
    :param name:
    :return:
    """
    payload = request.json
    result = dict()
    result['payload'] = payload
    result['greeting'] = f'Hi {name}, it is {datetime.now()}'
    return result


@app.route('/example_7/<string:name>', methods=['POST', 'PUT', 'DELETE'])
@ApiCache(redis=redis_instance, key_func=custom_func_2, expired_time=10)
def example_7(name):
    """
    caching data in redis instance with custom function.
        - http://0.0.0.0:5000/example_7/jimmy
        - payload:
            {
                "items": "coffee",
                "price": 18
            }
    :param name:
    :return:
    """
    payload = request.json
    result = dict()
    result['payload'] = payload
    result['greeting'] = f'Hi {name}, it is {datetime.now()}'
    return result


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
