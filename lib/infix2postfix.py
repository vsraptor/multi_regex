import sys
sys.path.extend(["../"])
import re
import string

from stack import Stack

isi = isinstance

__author__ = "Omkar Pathak, modified version ..."


#regex chars
CAT = '#' #concat
ANY = '.'

def isym(char): return isi(char, int) or re.match('[A-Za-z0-9]', char)

class I2P(object):

	def is_operand(self, char):
		if isi(char, int) : return True
		return char in string.ascii_letters or char in string.digits or char in '.$' 

	def precedence(self, char):
		dictionary = { "|": 0, CAT: 1, "?": 2, "*": 2, "+": 2, }
		return dictionary.get(char, -1)

	def insert_concat(self, exp):
		if isi(exp, str) : exp = self.str2lst(exp)

		rv = []
		for i, token in enumerate(exp):
			peek = None
			if i < len(exp)-1 : peek = exp[i+1] 
			else : #just append the last one
				rv.append(token)
				break

			last = token if isi(token,int) else token[-1]

			if ( (isym(token) or token in '?+*).' or last in '}]' ) and ( isym(peek) or peek in '(.' ) ) :
				  # or ( isi(token,str) and (token == ')' or last in ']') and  peek[0] in '{') ) :
				# say(f'{token} => {peek} : {last} #')
				rv.extend([token, CAT]) 
			else :
				# say(f'{token} => {peek} : {last}')
				rv.append(token)

		return rv

	def lst2str(self, exp) : return ''.join(exp)
	def str2lst(self, exp) : #covert exp to list of atoms
		return [ x for x in re.split(r"([\{\[].+?[\]\}]|.)", exp) if x != '' ] 

	def infix_to_postfix(self, expression):
		"""
		Convert infix notation to postfix notation using the Shunting-yard algorithm.
		https://en.wikipedia.org/wiki/Shunting-yard_algorithm
		https://en.wikipedia.org/wiki/Infix_notation
		https://en.wikipedia.org/wiki/Reverse_Polish_notation
		"""
		if isi(expression, str) : expression = self.str2lst(expression)

		stack = Stack(len(expression))
		postfix = []
		# group = ''
		# is_atom = False
		for char in expression:
			if isi(char, str) and len(char) > 1 : postfix.append(char) #atom 
			elif self.is_operand(char): postfix.append(char)
			elif char not in { '(', ')' } :
				while not stack.is_empty() and self.precedence(char) <= self.precedence(stack.peek()):
					postfix.append(stack.pop())
				stack.push(char)
			elif char == '(' : stack.push(char)
			elif char == ')' :
				while not stack.is_empty() and not stack.peek() == '(' :
					postfix.append(stack.pop())
				# Pop '(' from stack. If there is no '(', there is a mismatched
				# parentheses.
				if not stack.peek() == '(' : raise ValueError("Mismatched parentheses")
				stack.pop()
		    
		while not stack.is_empty(): postfix.append(stack.pop())
		return postfix


	def to_postfix(self, exp):
		return self.infix_to_postfix(self.insert_concat(exp))