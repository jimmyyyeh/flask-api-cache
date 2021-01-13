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

import json
from flask import request, jsonify
from flask.wrappers import Response
from inspect import signature
from functools import wraps

from memoization import cached


class ApiCache:
    def __init__(self, redis=None, key_func=None, expired_time=24 * 60 * 60):
        """
        Description:
            A decorator for python flask api.

            You can set cache in your memory or with redis server,
            the key will be generated default by the following rule: 『{YOUR_FUNCTION_NAME}:{REQUEST_FULL_PATH}』,
            or you can pass your custom key function by key_func args,
            the value will be your function return value.
        How To Use:
            @app.route('/')
            @ApiCache(redis=REDIS_INSTANCE, expired_time=10)
            def index(*args, **kwargs):
                name = request.args.get('name')
                age = request.args.get('age')
                return f'{name} is {age} years old.'

            If you request for『http://0.0.0.0:5000?name=Jimmy&age=18』,
            it will set a data cache by key: 『index:/?name=Jimmy&age=18』,
                                 with value: 『Jimmy is 18 years old.』,
            in your redis instance.
        """
        self.redis = redis
        self.key_func = key_func
        self.expired_time = expired_time
        self.func = None
        self.jsonify = False
        self.dict = False
        self._valid_redis()

    def __call__(self, func):
        self.func = func
        if self.redis:
            return self._cache_in_redis()
        else:
            return self._cache_in_memory()

    @staticmethod
    def _set_params():
        """
        get request params or payload as dict
        :return:
        """
        if request.method == 'GET':
            return dict(request.args)
        else:
            return request.json or dict()

    @staticmethod
    def _set_query_string(params):
        """
        format sorted params dict as string, for example:
        {
            "age": 18,
            "sex": "boy"
        }
        => age=18&sex=boy
        :param params:
        :return:
        """
        return '&'.join(f'{k}={v}' for k, v in sorted(params.items(), key=lambda x: x[0]))

    def _valid_redis(self):
        """
        check if redis service is available for connect
        """
        if not self.redis:
            return
        try:
            self.redis.ping()
        except Exception as e:
            raise Exception('redis server not available')

    def _get_data_key(self, **kwargs):
        """
        generate key by custom function or request full path
        """
        params = self._set_params()
        query_string = self._set_query_string(params=params)
        if self.key_func:
            args = kwargs
            args.update(params)
            return self.key_func(**args)
        else:
            return f'{self.func.__name__}:{query_string}'

    def _get_redis_value(self, key):
        """
        get redis value by key
        """
        return self.redis.get(name=key)

    def _set_redis_value(self, key, value):
        """
        set redis
        """
        self.redis.set(name=key, value=value, ex=self.expired_time)

    @staticmethod
    def _update_signature(params):
        """
        update input function signature
        """

        def outer_wrapper(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            # override signature
            sign = signature(f)
            sign = sign.replace(parameters=tuple(params))
            wrapper.__signature__ = sign
            return wrapper

        return outer_wrapper

    def _cache_in_memory(self):
        @self._update_signature(signature(self.func).parameters.values())
        def make_custom_key(*args, **kwargs):
            key = self._get_data_key(**kwargs)
            return key

        f = cached(ttl=self.expired_time, custom_key_maker=make_custom_key)(self.func)

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

    def _cache_in_redis(self):
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            key = self._get_data_key(**kwargs)
            value = self._get_redis_value(key=key)
            if not value:
                value = self.func(*args, **kwargs)
                if isinstance(value, Response):
                    self.jsonify = True
                    self._set_redis_value(key=key, value=json.dumps(value.json))
                elif isinstance(value, dict):
                    self.dict = True
                    self._set_redis_value(key=key, value=json.dumps(value))
                else:
                    self._set_redis_value(key=key, value=json.dumps(value))
            else:
                if self.jsonify:
                    value = jsonify(json.loads(value))
                elif self.dict:
                    value = json.loads(value)
            return value

        return wrapper
