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
            it will set a data cache by key: 『name=Jimmy&age=18』,
                                 with value: 『Jimmy is 18 years old.』,
            in your redis instance.
        """
        self.redis = redis
        self.key_func = key_func
        self.expired_time = expired_time
        self.func = None
        self._valid_redis()

    def __call__(self, func):
        self.func = func
        if self.redis:
            return self._cache_in_redis()
        else:
            return self._cache_in_memory()

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

    def _get_redis_key(self):
        """
        generate redis key by function name and request full path
        """
        if self.key_func:
            return self.key_func()
        else:
            return f'{self.func.__name__}:{request.full_path}'

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
                return f()

            # override signature
            sign = signature(f)
            sign = sign.replace(parameters=tuple(params))
            wrapper.__signature__ = sign
            return wrapper

        return outer_wrapper

    def _cache_in_memory(self):
        @self._update_signature(signature(self.func).parameters.values())
        def make_custom_key(*args):
            return self._get_redis_key()

        f = cached(ttl=self.expired_time, custom_key_maker=make_custom_key)(self.func)

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    def _cache_in_redis(self):
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            key = self._get_redis_key()
            value = self._get_redis_value(key=key)
            if not value:
                value = self.func(*args, **kwargs)
                if isinstance(value, Response):
                    value = json.dumps(value.json)
                else:
                    value = json.dumps(value)
                self._set_redis_value(key=key, value=value)
            value = json.loads(value)
            return jsonify(value)

        return wrapper
