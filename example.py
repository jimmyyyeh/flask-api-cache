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

from flask import Flask, request
from flask_api_cache import ApiCache

app = Flask(__name__)


def custom_func(**kwargs):
    name = kwargs.get('name')
    age = kwargs.get('age')
    sex = kwargs.get('sex')
    keys = f'{name}:{age}:{sex}'
    return keys


@app.route('/<string:name>/<int:age>')
@ApiCache(key_func=custom_func, expired_time=10)
def index(name, age):
    sex = request.args.get('sex', None, str)
    return f'{name} is a {age} years old {sex}.'


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
