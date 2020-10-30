import sys
sys.path.extend(["../"])
	
from collections import deque
from attr_dict import AttrDict
from pp import *
from functools import partial

from infix2postfix import *

isi = isinstance

#============== NFA ==========================================================

class Symbol(AttrDict): pass


# A State holds :
#   Either Symbol OR 1 or 2 Epsilon transition
#   and/or flag which specifies if this is end-state
class State(AttrDict) :

	@classmethod
	def new(cls, is_end):
		if is_end :	return State({'is_end': is_end })
		return State({})
		# return State( {'is_end': is_end, 'T': Symbol({}), 'E': [] } )

	#exist fields checks
	@property
	def hasT(self): return 'T' in self
	@property
	def hasE(self): return 'E' in self
	@property
	def hasIsE(self): return 'is_end' in self
	@property
	def sym(self):
		if self.hasT : return next(iter(self.T))
		if self.hasIsE : return '!'
		return '?'

	#given states setup the transition 
	def add_epsilon_trans(self, sto): 
		if not self.hasE : self['E'] = []
		self.E.append(sto)
	def add_symbol_trans(self, sto, symbol): 
		if not self.hasT : self['T'] = Symbol({})
		self.T[symbol] = sto
	def ise_false(self):
		if self.hasIsE : del self['is_end'] 
	def ise_true(self):
		self['is_end'] = True


# start-State => end-State
class NFA(AttrDict) :

	@classmethod
	def new(cls, start, end):
		return NFA({'start':start, 'end':end})

	@classmethod
	def epsilon(cls):
		start = State.new(False)
		end = State.new(True)
		start.add_epsilon_trans(end)
		return NFA.new(start, end)

	@classmethod
	def symbol(cls, symbol):
		start = State.new(False)
		end = State.new(True)
		start.add_symbol_trans(end, symbol)
		return NFA.new(start, end)


class OPS(object):

	def zero_one(self, state): #?
		start = State.new(False)
		end = State.new(True)

		start.add_epsilon_trans(end)
		start.add_epsilon_trans(state.start)
		state.end.add_epsilon_trans(end)
		state.end.ise_false()

		return NFA.new(start, end)

	# state ==>   state . state*
	def oneORmore(self, state): #+
		once = state #Transition(state)
		once.end.ise_false()
		return self.concat(once, self.closure(state))

	def concat(self, first, second):
		first.end.add_epsilon_trans(second.start)
		first.end.ise_false()
		return NFA.new(first.start, second.end)

	def union(self, first, second): #|
		start = State.new(False)
		start.add_epsilon_trans(first.start)
		start.add_epsilon_trans(second.start)

		end = State.new(True)
		first.end.add_epsilon_trans(end)
		first.end.ise_false()
		second.end.add_epsilon_trans(end)
		second.end.ise_false()
		return NFA.new(start, end)

	def closure(self, nfa): #*
		start = State.new(False)
		end = State.new(True)

		start.add_epsilon_trans(end)
		start.add_epsilon_trans(nfa.start)

		nfa.end.add_epsilon_trans(end)
		nfa.end.add_epsilon_trans(nfa.start)
		nfa.end.ise_false()
		return NFA.new(start, end)

	def sym_class(self, klass): #[abc]
		#extract symbols
		syms = klass.replace('[','').replace(']','') 

		#create the start State
		start = State.new(False)
		end = State.new(True)
		# [abc] .. start-> |=
		for sym in syms :
			state = State.new(True)
			start.add_symbol_trans(state, sym)
			state.add_epsilon_trans(end)

		return NFA.new(start, end)

	#Implemented as unions i.e. a{2,4} : aa|aaa|aaaa
	#nfa: n-normal states + (m-n)-end states
	def n2m(self, symbol, nm): #{n,m}
		#extract from, to
		n,m = [ int(i) for i in nm.replace('{','').replace('}','').split(',') ]
		# say(f"n2m> {symbol}, {nm}: {n},{m}")
		
		#create the start State
		start = State.new(True if n == 0 else False)
		prev = start
		# {1,3} .. start->a->a:end->a:end->a:end
		for i in range(m) :
			is_end = False if i+1 < n else True
			state = State.new(is_end)
			prev.add_symbol_trans(state, symbol.start.sym)
			prev = state

		end = state
		# pprint(start, width=40)
		return NFA.new(start, end)


class Regex(object):

	def to_nfa(self, postfix_exp):

		ops = OPS()

		if isi(postfix_exp, (str,list)) : 
			i2p = I2P()
			postfix_exp = i2p.to_postfix(postfix_exp)
			##log('nfa', f'postfix> {postfix_exp}')

		if postfix_exp == [] : return NFA.epsilon()

		stack = []
		
		for token in postfix_exp :
			if isi(token, int) : stack.append(NFA.symbol(token))
			elif token == '*' : stack.append(ops.closure(stack.pop()))
			elif token == '?' : stack.append(ops.zero_one(stack.pop()))
			elif token == '+' : stack.append(ops.oneORmore(stack.pop()))
			elif token == '|' :
				right = stack.pop()
				left  = stack.pop()
				stack.append(ops.union(left, right))
			elif token == CAT :
				right = stack.pop()
				left  = stack.pop()
				stack.append(ops.concat(left, right))
			elif token.startswith("{"):
				stack.append(ops.n2m(stack.pop(),token))	
			elif token.startswith("["):
				stack.append(ops.sym_class(token))				
			else :
				stack.append(NFA.symbol(token))

		assert len(stack) == 1, "Should be only one element left in the stack, but have {}".format(len(stack))

		return stack.pop()


	def add_next_state(self, state, next_states, visited=None) :
		if visited is None : visited = set()

		if state.hasE :
			for st in state.E :
				##log('an',f' eps:{st.sym}')
				if st not in visited :
					visited.add(st);
					self.add_next_state(st, next_states, visited);
		else :
			#log('an',f'add state> {state.sym}')
			if isi(next_states, set) : next_states.add(state)
			else : next_states.append(state)

	#shortcut representation : is it ['(,1,|,2,)'] in place of ['(',1,'|',2,')']
	def is_lst_str(self, item) :
		return isi(item, list) and len(item) == 1 and isi(item[0], str) #and len(item[0]) > 1 


	def match_one(self, regex, seq) :
		#convert ['1,|,2'] to ['1','|','2']
		if self.is_lst_str(regex) : 
			regex = [ (int(i) if i.isdigit() else i) for i in regex[0].split(',') ]	
		if self.is_lst_str(seq) :
			seq = [ (int(i) if i.isdigit() else i) for i in seq[0].split(',')	]	

		if isi(regex, (str,list)) : regex = self.to_nfa(regex)
		# pprint(regex, width=40)
		current_states = []
		self.add_next_state(regex.start, current_states)

		for symbol in seq :
			next_states = []
			for state in current_states :
				#log('mo','ssym:',state.sym,' sym:', symbol)
				# not symbol AND not any-symbol match : pass
				if not state.hasT or (symbol not in state.T and state.sym != ANY ) : continue

				next_state = state.T[state.sym] # access by state.sym instead of symbol
				if next_state : self.add_next_state(next_state, next_states)

			current_states = next_states

		#is there any end-state 
		return any([ s.hasIsE for s in current_states ])


	#=====================================================================================

	#Based on current states and prefixes get the predicted next prefixes+sym
	#  use the fun() to get the prediction
	def next_seq_syms(self, states, prefixes, fun=None, head=None, end='.'):
		#log('ns',f'next_syms -----------------------------------------{len(states)}')
		syms = []
		for prefix in prefixes :
			#log('ns', f'  search:{prefix}')
			pred = fun(prefix=prefix, end=end) # search for match
			if len(pred) > 0 : syms.append(pred) #skip empty results
		return syms

	#move forward in to the next states in the regex
	def next_re_states(self, current_states) :
		#log('ns','next_states -----------------------------------------')
		next_states = set()
		for state in current_states :
			if not state.hasT or (state.sym not in state.T and state.sym != ANY ) : continue
			next_state = state.T[state.sym]
			if next_state : self.add_next_state(next_state, next_states)
		return list(next_states)

	#given states and symbols, return only the ones that match-by-suffix 
	def filter_sas(self, states, symsOseqs):
		#log('fs', 'filter -----------------------------------------')
		#if flag true then the syms are lists instead of strings
		is_list_sym = len(symsOseqs) > 0 and isi(symsOseqs[0][0], list)
		#we need to remove duplicates so we use sets instead of lists
		filtered_states = set()
		filtered_syms = set() # prefixes
		for syms in symsOseqs :
			for seq in syms :
				suffix = seq[-1]
				for state in states :
					#log('fs', f'   state:{state.sym} == suffix:{suffix} ? seq:{seq} : {state.sym == ANY or state.sym == suffix}')
					if state.sym == ANY or state.sym == suffix : #if there is a match 
						filtered_states.add(state)
						# if not flag and isi(seq, list) : flag = True 
						filtered_syms.add(str(seq)) #needed if arg is list to make it hashable for the set

		#convert str-lists back to lists
		if is_list_sym : filtered_syms = [eval(s) for s in filtered_syms ]
		return list(filtered_states), list(filtered_syms)

	#check conditions for ending matching
	def is_end(self, states, seqs, end):
		is_end = any([ s.hasIsE for s in states ]) #did we reach END node
		#filter sequences w/o end-sym
		full_seqs = [s for ss in seqs for s in ss if s[-1] == end  ]
		#log('m','  IsE: ', is_end)
		if is_end :
			#end=True and there are full seq
			if len(full_seqs) > 0 : return True, full_seqs
			#end but no full sequences
			else : return False, full_seqs
		else :
			#end=False but no seqs 
			if len(seqs) == 0 : return True, full_seqs
			else : return False, full_seqs	


	# This method matches regex against opaque sequence-store
	# The seq-store may store thousands++ of sequences of characters, words, strings, numbers ...
	#  in any number of storage : lists, SQL or Graph DB
	# The only requierment is to provide a function which given a sub-sequence i.e. prefix 
	# returns the next element i.e. character, number, word ... 

	def match(self, regex, match_prefix_fun, head=None, limit=None, max_steps=10, end='.'):

		prefixes = [''] if isi(regex,str) else [[]]

		if self.is_lst_str(regex) : #convert ['1,|,3'] to ['1','|','3']
			regex = [ (int(i) if i.isdigit() else i) for i in regex[0].split(',')	]	
		#converl list to NFA struct
		if isi(regex, (str, list)) : regex = self.to_nfa(regex)

		filtered = set()
		self.add_next_state(regex.start, filtered)
		states = filtered

		i = 0
		while i <= max_steps :
			#log('m','\n===================================================')

			#log('m',' fstates  :', [f.sym for f in filtered])
			#log('m',' prefixes :', [f for f in prefixes])

			if i > 0 : head = None #only needed on the first run
			syms = self.next_seq_syms(filtered, prefixes, fun=partial(match_prefix_fun, head=head), end=end)
			#log('m',' syms : ', syms)
			
			if i > 0 : states = self.next_re_states(filtered)
			#log('m',' states :', [ s.sym for s in states])

			#check if reach the end of the regex
			flag, full_seqs = self.is_end(states, syms, end) 
			if flag : return full_seqs

			filtered, prefixes = self.filter_sas(states, syms)
			
			if limit is not None : #limiting per step results
				#log('m','\n before-limit :', [f for f in prefixes])
				prefixes = prefixes[:limit]
				#log('m',' limit-pre :', [f for f in prefixes])

			i += 1

#----------------------------------------------------------------------		

def dump(state, visited=None):
	if visited is None : visited = set()
	if isi(state, list): return [dump(s) for s in state ]
	if state in visited : return []
	visited.add(state)
	if state.hasT : 
		return [state.sym] + dump(state.T[state.sym], visited)
	if state.hasE :
		return ['eps'] + [ dump(x,visited) for x in state.E ]	
	return []
