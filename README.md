# Linked Dictionary

Advanced python dictionary(hash-table), which can link it-self keys and make calculations into the keys of the dict
## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.
```bash
pip install linked_dict
```
## Usage

### The syntax of expressions:
```python
{'key' : '...$(expression)$...'}
```
### Initialization:

```python
from linked_dict import LinkedDict
from json import dumps

dictionary = LinkedDict({})  # {} - your dict
```
### Examples:
Simple link:
```python
example = LinkedDict(
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
Expression with one key. **As you can see** now I added a space **outside** this expression, and the final value is string:
```python
example = LinkedDict(
    {
        'a': 5,
        'b': '$(a * 2)$ ' # here with a space
    }
)

print(dumps(example))

    {
       'a': 5,
       'b': '10 '
    }
```
Link other expressions:
```python
example = LinkedDict(
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
Using all built-in types:
```python
example = LinkedDict(
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
Using your own functions into expressions:
```python
some_func = lambda arg: arg + 1

example = LinkedDict(
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

### Changing:
When you change a value, all values that link it change their values too. But links work only in one direction
```python
example = LinkedDict(
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
## Warning:
**1.** Keys of your dict must be **only** strings
```python
{5: 'abc', True: []} # is prohibited
{'5': 'abc', 'True': []} # is allowed
```
**2.** Don't make loops of links. Dictionary is protected of this, but you will get the Error

## Contributing:
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## License
[MIT](https://choosealicense.com/licenses/mit/)