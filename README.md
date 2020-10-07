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
### Cache Without Redis
```python
@app.route('/')
@ApiCache(expired_time=10)
def index(*args, **kwargs):
    name = request.args.get('name')
    age = request.args.get('age')
    return f'{name} is {age} years old.'
```
If you request for **http://0.0.0.0:5000?name=Jimmy&age=18**,<br>
it will set a 10 seconds cache by key: `name=Jimmy&age=18`,<br>
                     with value: `Jimmy is 18 years old.`,
in your memory, it will be cleared after api service restart.

### Cache With Redis
```python
@app.route('/')
@ApiCache(redis=REDIS_INSTANCE, expired_time=10)
def index(*args, **kwargs):
    name = request.args.get('name')
    age = request.args.get('age')
    return f'{name} is {age} years old.'
```
If you request for **http://0.0.0.0:5000?name=Jimmy&age=18**,<br>
it will set a 10 seconds cache by key: `name=Jimmy&age=18`,<br>
                     with value: `Jimmy is 18 years old.`,
in your redis instance.

### Cache With Custom Function
```python
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
```
If you request for **http://0.0.0.0:5600/Jimmy/18?sex=boy** ,<br>
it will set a 10 seconds cache by key: `Jimmy:18:boy`,<br>
                     with value: `Jimmy is a 18 years old boy.`,
in your memory, it will be cleared after service restart.

## Parameters

|name|required|description|
|----|--------|-----------|
|redis|no|if you want to caching data in redis, you can call ApiCache with a redis instance.|
|expired_time|no|set your expired time with **seconds**, the default value is 24 * 60 * 60 seconds (1 day)|
|key_func|no|the function which you want to make custom key|
