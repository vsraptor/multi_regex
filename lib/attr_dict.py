from copy import deepcopy

class AttrDict(dict):
	def __init__(self, *args, **kwargs):
		super(AttrDict, self).__init__(*args, **kwargs)
		self.__dict__ = self

	def __hash__(self): return hash(str(self))
	def __eq__(self,other): return self.__hash__() == other.__hash__()

	def __deepcopy__(self, memo):
		rv = type(self)(deepcopy(dict(self), memo))
		rv.__dict__ = rv
		return rv

	# def __deepcopy__(self, memo):
	# 	deepcopy_method = self.__deepcopy__
	# 	delattr(self,'__deepcopy__')
	# 	cp = deepcopy(self, memo)
	# 	self.__deepcopy__ = deepcopy_method
	# 	cp.__deepcopy__ = deepcopy_method
	# 	self.__dict__ = self
	# 	return cp

	def rebind(self) : self.__dict__ = self

