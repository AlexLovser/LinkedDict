from re import findall, compile
from typing import Optional, SupportsInt, Union
from json import dumps


class Unknown:
	def __repr__(self):
		return repr(None)

	def __str__(self):
		return str(None)


class LinkedKeysError(ValueError):
	pass


class _LinkedValue:
	def __init__(self, *, key, obj):
		self.obj = obj
		self.value = self.obj[key]
		self.key = key
		self.expressions_into = [
			_LinkedFunction(parent=self, start=(start := self.value.index(exp)), end=start + len(exp))
			for exp in self._find_expressions(self.value)
		]

		if not self.expressions_into:
			self.obj.countable[key] = self.value

		self.obj.values.append(self)
		self.obj.functions.extend(self.expressions_into)

	def __repr__(self):
		return self.showing_value

	def __str__(self):
		return str(self.showing_value)

	def _recheck(self, value):
		if value.expressions_into and self.obj.countable.get(value.key):
			del self.obj.countable[value.key]
		else:
			self.obj.countable[value.key] = value.showing_value

	def _replace_defined(self, function) -> str:
		return ''.join(
			str(repr(x) if (x := self.obj.countable.get(part)) else part)
			for part in self._split(function)
		)

	def _find_expressions(self, string: Optional[str]) -> list:
		return self.obj.pattern.findall(string) if isinstance(string, str) else []

	@staticmethod
	def _split(string: Optional[str]):
		array = ['']
		for letter in string:
			if letter in '-+*/%=()[]{} ':
				array.extend((letter, ''))
			else:
				array[-1] += letter
		return filter(None, array)

	@property
	def showing_value(self):
		return self.value if self.obj.countable.get(self.key) else self.obj.pattern.sub('{}', str(self.value)).format(*self.expressions_into)

	def try_to_count(self):
		for function in self.expressions_into:
			if (set(self.obj.countable) & function.expr_parts) == function.expr_parts:
				function.answer = self._replace_defined(function.content)
				try:
					function.answer = eval(function.answer, self.obj.loc, self.obj.glob)
				except (NameError, TypeError, SyntaxError):
					pass
		self.commit()

	def commit(self):
		val = self.showing_value
		if not self.obj.pattern.sub('', str(self.value)):
			try:
				val = eval(val, self.obj.loc, self.obj.glob)
			except (NameError, TypeError, SyntaxError):
				pass
		for f in self.expressions_into:
			if isinstance(f.answer, Unknown):
				break
		else:
			self.obj.countable[self.key] = val

		self.obj.original[self.key] = val

	def update(self, value):
		for func in self.expressions_into:
			self.obj.functions.remove(func)

		self.value = value

		self.expressions_into = [
			_LinkedFunction(parent=self, start=(start := value.index(exp)), end=start + len(exp))
			for exp in self._find_expressions(value)
		]

		if self.expressions_into:
			self.obj.functions.extend(self.expressions_into)

		self._recheck(self)

		links = set()
		for ex in self.expressions_into:
			links = links.union(ex.expr_parts)

		self.obj.graph_map[self.key] = links

		for i in links:
			self.obj.deep([i])

		self.try_to_count()

		def complete(value_key):
			for val in self.obj.values:
				save_it = False
				for expr in val.expressions_into:
					if value_key in expr.expr_parts:
						expr.answer = Unknown()
						save_it = True

				if save_it:
					self._recheck(val)
					val.try_to_count()
					complete(val.key)
		complete(self.key)


class _LinkedFunction:
	def __init__(self, *, parent, start: int, end: int):
		self.start, self.end = start, end
		self.parent = parent
		self.content = self.parent.value[start + 2:end - 2]
		self.expr_parts = {i for i in findall(r'[A-zА-я][0-9A-zА-я]*', self.content) if self.parent.obj.get(i)}
		self.answer = Unknown() if self.expr_parts else eval(self.content, self.parent.obj.loc, self.parent.obj.glob)

	def get_original(self):
		return self.parent.value[self.start + 2:self.end - 2]

	def __repr__(self):
		return repr(self.answer if not isinstance(self.answer, Unknown) else self.get_original())

	def __str__(self):
		return str(self.answer if not isinstance(self.answer, Unknown) else self.get_original())


class LinkedDict:
	def __init__(self, /, original: Optional[dict], *, dynamic: Optional[bool] = True, debug: Optional[bool] = True, loc=None, glob=None):
		self.values = []
		self.functions = []
		self.countable = {}
		self.graph_map = {}
		self.pattern = compile(r'\$\([A-zА-я0-9\-+*/%={}()\s\[\].,:\'"]+\)\$')
		self.dynamic = dynamic
		self.debug = debug
		self.graph_map = {}
		self.original = original if original else {}
		self.loc = loc if loc else locals()
		self.glob = glob if glob else globals()

		for key, value in self.original.items():
			v = _LinkedValue(key=key, obj=self)
			links = set()
			for expr in v.expressions_into:
				links = links.union(expr.expr_parts)
			self.graph_map[key] = links

		if self.graph_map:
			for i in self.graph_map:
				self.deep([i])

		x = len(self.original)
		while x > len(self.countable):
			for value in self.values:
				if not self.countable.get(value.key):
					value.try_to_count()

	def __eq__(self, other):
		return self == other

	def __getitem__(self, item):
		return self.original[item]

	def __setitem__(self, key: str, value):
		if self.dynamic and (vals := self.find_where(self.values, key=lambda x: x.key == key)):
			vals[0].update(value)
		else:
			self.original[key] = value
			_LinkedValue(key=key, obj=self).try_to_count()

	def __str__(self):
		return str(self.original)

	def __repr__(self):
		return repr(self.original)

	def __iter__(self):
		return self.original.__iter__()

	def items(self):
		return self.original.items()

	def get(self, value: str, default=None):
		return self.original.get(value, default)

	def deep(self, way: Union[list, tuple]):
		lines = self.graph_map.get(way[-1], set())
		# print('lines', lines)
		if set(way) & set(lines):
			trace = ' -> '.join(way + [way[0]])
			raise LinkedKeysError(f'Your keys link themselves in loop!\nTrace is: {trace}')
		for node in lines:
			self.deep(way + [node])

	@staticmethod
	def find_where(iterable: Union[list, tuple], *, key, count: Optional[SupportsInt] = None) -> Optional[list]:
		if count is None:
			count = len(iterable)
		return [i for i in iterable if key(i) and (count := count - 1)]

	@property
	def dumps(self):
		return dumps(
			self.original,
			indent=4,
			ensure_ascii=False
		)


if __name__ == '__main__':
	print('(c) Made by Alex Lovser. Thanks for using!')
