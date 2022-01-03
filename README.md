#Hyper Dictionary
Advanced python dictionary(hash-table), which can link it-self keys and make calculations into the keys of the dict
##Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.
```bash
pip install HyperDict
```
##Usage

###The syntax of expressions:
```python
{'key' : '...$(expression)$...'}
```
###Initialization:
```python
from HyperDict import HyperDict
from json import dumps
dictionary = HyperDict({}) # {} - your dict
```
###Examples:
```python
example = Hyperdict(
    {
        'a': 5,
        'b': '$(a)$'
    }
)

print(dumps(example))

    {
       'a': 5,
       'b': 5
    }
```

```python
example = Hyperdict(
    {
        'a': 5,
        'b': '$(a + x)$ ' # here with a space
    }
)

print(dumps(example))

    {
       'a': 5,
       'b': '5 '
    }
```

```python
example = Hyperdict(
    {
        'a': 5,
        'b': 100,
        'c': '$(b + d)$',
        'd': '$(b + a)$'
    }
)

print(dumps(example))

    {
        'a': 5,
        'b': 100,
        'c': 205,
        'd': 105
    }
```

```python
example = Hyperdict(
    {
        'a': ['one_item'],
        'b': '$(a + ["another_item"])$'
    }
)

print(dumps(example))

    {
        'a': ['one_item'],
        'b': ['one_item', 'another_item']
    }
```

```python
some_func = lambda arg: arg + 1

example = Hyperdict(
    {
        'a': 5,
        'b': '$(some_func(a))$'
    }
)

print(dumps(example))

    {
       'a': 5,
       'b': 5
    }
```

###Changing:
```python
example = Hyperdict(
    {
        'a': 5,
        'b': '$(a)$'
    }
)
print(example) 
# >>> {'a': 5, 'b': 5}
example['a'] = 'another_val'
print(example)
# >>> {'a': 'another_val', 'b': 'another_val'}
example['a'] = '4'
print(example) 
# >>> {'a': 'another_val', 'b': 4}

# !!! 'b' links 'a', but 'a' doesn't link 'b'
```
##Warning
```python
# Keys of your dict must be only strings
{5: 'abc', True: []} # is prohibited
{'5': 'abc', 'True': []} # is allowed
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## License
[MIT](https://choosealicense.com/licenses/mit/)