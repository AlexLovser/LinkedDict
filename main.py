from re import findall, sub
from json import dumps


class _Node:
	values = []
	functions = []
	countable = {}
	graph_map = {}
	pattern = r'\$\([A-zА-я0-9\-+*/%={}()\s\[\].,:\'"]+\)\$'
	obj = None

	class _Unknown:
		def __repr__(self):
			return repr(None)

		def __str__(self):
			return str(None)

	class LinkedKeysError(ValueError):
		pass

	def replace_defined(self, function) -> str:
		array = ['']
		for letter in function.content:
			if letter in '-+*/%=()[]{} ':
				array.extend((letter, ''))
			else:
				array[-1] += letter

		return ''.join(str(self.countable.get(part, part)) for part in filter(None, array))

	def find_expressions(self, string) -> list:
		if isinstance(string, str):
			return findall(self.pattern, string)
		return []

	def recheck(self, value):
		if self.countable.get(value.key):
			if value.expressions_into:
				del value.countable[value.key]
			else:
				self.countable[value.key] = value.showing_value
		elif not value.expressions_into:
			self.countable[value.key] = value.showing_value

	def deep(self, way):
		lines = self.graph_map[way[-1]]
		if set(way) & set(lines):
			trace = ' -> '.join(way + [way[0]])
			raise self.LinkedKeysError(f'Your keys link themselves in loop! Trace is: {trace}')
		for node in lines:
			self.deep(way + [node])

	@staticmethod
	def find_where(iterable: list, *, key, count=None) -> list:
		if count is None:
			count = len(iterable)
		found = []

		for i in iterable:
			if key(i) and count:
				count -= 1
				found.append(i)

		return found

	@staticmethod
	def eval_value(string):
		try:
			return True, eval(str(string))
		except (NameError, TypeError):
			return False, string


class _HyperValue(_Node):
	def __init__(self, *, key):
		self.value = self.__showing_value = self.obj[key]
		self.key = key
		self.expressions_into = [
			_HyperFunction(parent=self, start=(start := self.value.index(exp)), end=start + len(exp))
			for exp in self.find_expressions(self.value)
		]

		if not self.expressions_into:
			self.countable[key] = self.value

		self.values.append(self)
		self.functions.extend(self.expressions_into)

	@property
	def showing_value(self):
		if self.countable.get(self.key):
			return self.__showing_value
		return sub(self.pattern, '{}', str(self.value)).format(*self.expressions_into)

	@showing_value.setter
	def showing_value(self, value):
		self.__showing_value = value

	def __repr__(self):
		return self.showing_value

	def __str__(self):
		return str(self.showing_value)

	def try_to_count(self):
		for function in self.expressions_into:
			if function.answer == self._Unknown:
				temp_content = self.replace_defined(function)
				if function.content != temp_content:
					function.answer = self.eval_value(temp_content)[-1]
		self.commit()

	def commit(self):
		if isinstance(self.value, str) and sub(self.pattern, '', self.value):
			val = self.showing_value
		else:
			_, val = self.eval_value(str(self.showing_value))

		self.obj[self.key] = val
		if not isinstance(self.showing_value, str) or not self.find_expressions(val):
			self.countable[self.key] = val
		return val

	def update(self, value):
		for func in self.expressions_into:
			self.functions.remove(func)

		self.value = self.__showing_value = value

		self.expressions_into = [
			_HyperFunction(parent=self, start=(start := value.index(exp)), end=start + len(exp))
			for exp in self.find_expressions(value)
		]

		if self.expressions_into:
			self.functions.extend(self.expressions_into)

		self.recheck(self)
		self.try_to_count()

		def complete(value_key):  # count in deep
			for val in self.values:
				save_it = False
				for expr in val.expressions_into:
					if value_key in expr.expr_parts:
						expr.answer = self._Unknown
						save_it = True
				if save_it:
					self.recheck(val)
					val.try_to_count()
					complete(val.key)  # recursion

		complete(self.key)


class _HyperFunction(_Node):
	def __init__(self, *, parent, start: int, end: int):
		self.start, self.end = start, end
		self.parent = parent
		self.content = self.parent.value[start + 2:end - 2]
		self.expr_parts = set(findall(r'[A-zА-я][0-9A-zА-я]*', self.content))
		self.answer = self._Unknown if self.expr_parts else eval(self.content)

	def __repr__(self):
		return repr(self.answer if not isinstance(self.answer, self._Unknown) else self.content)

	def __str__(self):
		return str(self.answer if not isinstance(self.answer, self._Unknown) else self.content)


class HyperDict(_Node):
	def __init__(self, /, obj: dict = None, *, dynamic=True, debug=True):
		if obj is None:
			obj = {}

		_Node.obj = obj

		self.__obj = obj
		self.__dynamic = dynamic
		self.__debug = debug
		self.graph_map = {}

		for key, value in self.__obj.items():
			v = _HyperValue(key=key)
			links = set()
			for expr in v.expressions_into:
				links = links.union(expr.expr_parts)
			self.graph_map[key] = links

		if self.graph_map:
			self.deep([list(self.graph_map)[0]])

		self.count()

	def __getitem__(self, item):
		return self.__obj[item]

	def __setitem__(self, key, value):
		if vals := self.find_where(self.values, key=lambda x: x.key == key):
			vals[0].update(value)
		else:
			self.obj[key] = value
			_HyperValue(key=key).try_to_count()

	def __str__(self):
		return str(self.__obj)

	def __repr__(self):
		return repr(self.__obj)

	def __iter__(self):
		return self.__obj.__iter__()

	def count(self, *, values=None):
		if values is None:
			values = self.values
		x = len(self.__obj)
		while x > len(self.countable):
			for value in values:
				value.try_to_count()

	def items(self):
		return self.__obj.items()

	def get(self, value, default=None):
		return self.__obj.get(value, default=default)

	def dumps(self, *, indent=4):
		return dumps(self.__obj, indent=indent, ensure_ascii=False)


if __name__ == '__main__':
	func = lambda x: x < 15

	dictionary = HyperDict(
		{
			'a': 5,
			'b': 10,
			'c': '$(a + b)$',
			'd': '$(func(c))$',
			'e': 'Len of range($(c)$) is $(len(range(c)))$',
			'f': [1, 2, 3],
			'g': '$(f * 2)$'
		}
	)
	print(dictionary.dumps(indent=5))
	print('@MAde by AlexLovser. Thanks for using!')
