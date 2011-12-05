import math

def BitsFor(n):
	if n == 0:
		return 1
	else:
		return int(math.ceil(math.log(n+1, 2)))

class BV:
	def __init__(self, width=1, signed=False):
		self.width = width
		self.signed = signed
	
	def __str__(self):
		r = str(self.width) + "'"
		if self.signed:
			r += "s"
		r += "d"
		return r

class Value:
	def __init__(self, bv):
		self.bv = bv
	
	def __add__(self, other):
		return Operator("+", [self, other])
	def __radd__(self, other):
		return Operator("+", [other, self])
	def __sub__(self, other):
		return Operator("-", [self, other])
	def __rsub__(self, other):
		return Operator("-", [other, self])
	def __mul__(self, other):
		return Operator("*", [self, other])
	def __rmul__(self, other):
		return Operator("*", [other, self])
	def __lshift__(self, other):
		return Operator("<<", [self, other])
	def __rlshift__(self, other):
		return Operator("<<", [other, self])
	def __rshift__(self, other):
		return Operator(">>", [self, other])
	def __rrshift__(self, other):
		return Operator(">>", [other, self])
	def __and__(self, other):
		return Operator("&", [self, other])
	def __rand__(self, other):
		return Operator("&", [other, self])
	def __xor__(self, other):
		return Operator("^", [self, other])
	def __rxor__(self, other):
		return Operator("^", [other, self])
	def __or__(self, other):
		return Operator("|", [self, other])
	def __ror__(self, other):
		return Operator("|", [other, self])
	
	def __lt__(self, other):
		return Operator("<", [self, other])
	def __le__(self, other):
		return Operator("<=", [self, other])
	def __eq__(self, other):
		return Operator("==", [self, other])
	def __ne__(self, other):
		return Operator("!=", [self, other])
	def __gt__(self, other):
		return Operator(">", [self, other])
	def __ge__(self, other):
		return Operator(">=", [self, other])
	
	
	def __getitem__(self, key):
		if isinstance(key, int):
			return Slice(self, key, key+1)
		elif isinstance(key, slice):
			start = key.start or 0
			stop = key.stop or self.bv.width
			if key.step != None:
				raise KeyError
			return Slice(self, start, stop)
		else:
			raise KeyError

class Operator(Value):
	def __init__(self, op, operands):
		self.op = op
		self.operands = list(map(_cst, operands))

class Slice(Value):
	def __init__(self, value, start, stop):
		self.value = value
		self.start = start
		self.stop = stop

class Cat(Value):
	def __init__(self, *args):
		self.l = list(map(_cst, args))

class Constant(Value):
	def __init__(self, n, bv=None):
		if bv == None:
			Value.__init__(self, BV(BitsFor(n)))
		else:
			Value.__init__(self, bv)
		self.n = n

def _cst(x):
	if isinstance(x, int):
		return Constant(x)
	else:
		return x

class Signal(Value):
	def __init__(self, bv=BV(), name="anonymous", variable=False, reset=0):
		Value.__init__(self, bv)
		self.bv = bv
		self.variable = variable
		self.name = name
		self.reset = Constant(reset, bv)

	def __hash__(self):
		return id(self)

def Declare(parent, name, bv=BV(), variable=False, reset=0):
	setattr(parent, name, Signal(bv, parent.__class__.__name__+"_"+name, variable, reset))

# statements

class Assign:
	def __init__(self, l, r):
		self.l = l
		self.r = _cst(r)

class StatementList:
	def __init__(self, l=[]):
		self.l = l

def _sl(x):
	if isinstance(x, list):
		return StatementList(x)
	else:
		return x

class If:
	def __init__(self, cond, t, f=StatementList()):
		self.cond = cond
		self.t = _sl(t)
		self.f = _sl(f)

class Case:
	def __init__(self, test, cases=[], default=StatementList()):
		self.test = test
		self.cases = [(c[0], _sl(c[1])) for c in cases]
		self.default = _sl(default)

#

class Fragment:
	def __init__(self, comb=StatementList(), sync=StatementList()):
		self.comb = _sl(comb)
		self.sync = _sl(sync)
	
	def __add__(self, other):
		return Fragment(self.comb.l + other.comb.l, self.sync.l + other.sync.l)