from re import findall, sub
from typing import Optional, SupportsInt, Union


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

	def _replace_defined(self, function) -> str:
		return ''.join(str(repr(x) if (x := self.countable.get(part)) else part) for part in self._split(function))

	def _find_expressions(self, string: Optional[str]) -> list:
		return findall(self.pattern, string) if isinstance(string, str) else []

	def _recheck(self, value):
		if value.expressions_into and self.countable.get(value.key):
			del value.countable[value.key]
		else:
			self.countable[value.key] = value.showing_value

	def _deep(self, way: Union[list, tuple]):
		lines = self.graph_map.get(way[-1], set())
		if set(way) & set(lines):
			trace = ' -> '.join(way + [way[0]])
			raise self.LinkedKeysError(f'Your keys link themselves in loop! Trace is: {trace}')
		for node in lines:
			self._deep(way + [node])

	@staticmethod
	def _split(string: Optional[str]):
		array = ['']
		for letter in string:
			if letter in '-+*/%=()[]{} ':
				array.extend((letter, ''))
			else:
				array[-1] += letter
		return filter(None, array)

	@staticmethod
	def find_where(iterable: Union[list, tuple], *, key, count: Optional[SupportsInt] = None) -> Optional[list]:
		if count is None:
			count = len(iterable)
		return [i for i in iterable if key(i) and (count := count - 1)]


class _LinkedValue(_Node):
	def __init__(self, *, key):
		self.value = self.obj[key]
		self.key = key
		self.expressions_into = [
			_LinkedFunction(parent=self, start=(start := self.value.index(exp)), end=start + len(exp))
			for exp in self._find_expressions(self.value)
		]

		if not self.expressions_into:
			self.countable[key] = self.value

		self.values.append(self)
		self.functions.extend(self.expressions_into)

	def __repr__(self):
		return self.showing_value

	def __str__(self):
		return str(self.showing_value)

	@property
	def showing_value(self):
		return self.value if self.countable.get(self.key) else sub(self.pattern, '{}', str(self.value)).format(*self.expressions_into)

	def try_to_count(self):
		for function in self.expressions_into:
			if (set(self.countable) & function.expr_parts) == function.expr_parts:
				function.answer = self._replace_defined(function.content)
				try:
					function.answer = eval(function.answer)
				except (NameError, TypeError, SyntaxError):
					pass
		self.commit()

	def commit(self):
		val = self.showing_value
		if not sub(self.pattern, '', str(self.value)):
			try:
				val = eval(val)
			except (NameError, TypeError, SyntaxError):
				pass
		for f in self.expressions_into:
			if isinstance(f.answer, self._Unknown):
				break
		else:
			self.countable[self.key] = val

		self.obj[self.key] = val

	def update(self, value):
		for func in self.expressions_into:
			self.functions.remove(func)

		self.value = value

		self.expressions_into = [
			_LinkedFunction(parent=self, start=(start := value.index(exp)), end=start + len(exp))
			for exp in self._find_expressions(value)
		]

		if self.expressions_into:
			self.functions.extend(self.expressions_into)

		self._recheck(self)

		links = set()
		for ex in self.expressions_into:
			links = links.union(ex.expr_parts)
		self.graph_map[self.key] = links

		for i in self.expressions_into:
			self._deep([i])

		self.try_to_count()

		def complete(value_key):
			for val in self.values:
				save_it = False
				for expr in val.expressions_into:
					if value_key in expr.expr_parts:
						expr.answer = self._Unknown()
						save_it = True
				if save_it:
					self._recheck(val)
					val.try_to_count()
					complete(val.key)

		complete(self.key)


class _LinkedFunction(_Node):
	def __init__(self, *, parent, start: int, end: int):
		self.start, self.end = start, end
		self.parent = parent
		self.content = self.parent.value[start + 2:end - 2]
		self.expr_parts = {i for i in findall(r'[A-zА-я][0-9A-zА-я]*', self.content) if self.obj.get(i)}
		self.answer = self._Unknown() if self.expr_parts else eval(self.content)

	def get_original(self):
		return self.parent.value[self.start + 2:self.end - 2]

	def __repr__(self):
		return repr(self.answer if not isinstance(self.answer, self._Unknown) else self.get_original())

	def __str__(self):
		return str(self.answer if not isinstance(self.answer, self._Unknown) else self.get_original())


class LinkedDict(_Node):
	def __init__(self, /, obj: Optional[dict], *, dynamic: Optional[bool] = True, debug: Optional[bool] = True):
		if obj is None:
			obj = {}

		_Node.obj = obj

		self.__obj = obj
		self.__dynamic = dynamic
		self.__debug = debug
		self.graph_map = {}

		for key, value in self.__obj.items():
			v = _LinkedValue(key=key)
			links = set()
			for expr in v.expressions_into:
				links = links.union(expr.expr_parts)
			self.graph_map[key] = links

		if self.graph_map:
			for i in self.graph_map:
				self._deep([i])

		x = len(self.__obj)
		while x > len(self.countable):
			for value in self.values:
				if not self.countable.get(value.key):
					value.try_to_count()

	def __eq__(self, other):
		return self == other

	def __getitem__(self, item):
		return self.__obj[item]

	def __setitem__(self, key: str, value):
		if self.__dynamic and (vals := self.find_where(self.values, key=lambda x: x.key == key)):
			vals[0].update(value)
		else:
			self.obj[key] = value
			_LinkedValue(key=key).try_to_count()

	def __str__(self):
		return str(self.__obj)

	def __repr__(self):
		return repr(self.__obj)

	def __iter__(self):
		return self.__obj.__iter__()

	def items(self):
		return self.__obj.items()

	def get(self, value: str, default=None):
		return self.__obj.get(value, default=default)


if __name__ == '__main__':
	print('(c) Made by Alex Lovser. Thanks for using!')
