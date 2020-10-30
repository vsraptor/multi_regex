from regex_nfa import *

tests = [

	['basic'],
	['',''],
	['a','a'], ['a','ab', False], ['ab', 'ab'], ['.', 'a'], ['.b', 'ab'], 
	['a?',''], ['a?','a'], ['a?','aa',False],
	['a*',''], ['a*', 'a'], ['a*', 'aa'], ['a*', 'aaa'], ['a*', 'aaaa'],
	['a+','',False], ['a+', 'a'],['a+', 'aa'], ['a+', 'aaa'], ['a+', 'aaaa'],
	['a|b', 'a'], ['a|b', 'b'], ['a|b', '',False],['a|b', 'c',False], ['a|b', 'ac',False],
	
	['range cases {n,m}'],
	['a{0,2}',''], ['a{0,2}', 'a'], ['a{0,2}', 'aa'], ['a{0,2}', 'aaa',False], ['a{0,2}', 'aaaa',False],
	['a{1,3}','', False], ['a{1,3}', 'a'], ['a{1,3}', 'aa'], ['a{1,3}', 'aaa'], ['a{1,3}', 'aaaa',False],
	['a{2,4}','', False], ['a{2,4}', 'a', False], ['a{2,4}', 'aa'], ['a{2,4}', 'aaa'], ['a{2,4}', 'aaaa'], ['a{2,4}', 'aaaaa',False],

	['bracketed cases'],
	['(ab)?', ''], ['(ab)?', 'ab'], ['(ab)?', 'abab', False],
	['(ab)*', ''], ['(ab)*', 'ab'], ['(ab)*', 'abab'],
	['(ab)+', '', False], ['(ab)+', 'ab'], ['(ab)+', 'abab'],

	['unions'],
	['(a|b)?', ''], ['(a|b)?', 'a'], ['(a|b)?', 'b'], ['(a|b)?', 'aa', False],
	['(a|b)*', ''], ['(a|b)*', 'a'], ['(a|b)*', 'b'], ['(a|b)*', 'aa'], ['(a|b)*', 'bb'],['(a|b)*', 'ab'],['(a|b)*', 'ba'],
	['(a|b)+', '',False], ['(a|b)+', 'a'], ['(a|b)+', 'b'], ['(a|b)+', 'aa'], ['(a|b)+', 'bb'],['(a|b)+', 'ab'],['(a|b)+', 'ba'],

#	['compound range'],
#	['(a|b){0,2}',''], ['(a|b){0,2}', 'a'], ['(a|b){0,2}', 'b'], ['(a|b){0,2}', 'aa'], ['(a|b){0,2}', 'bb'],
#	['(a|b){0,2}','ab'], ['(a|b){0,2}', 'ba'], ['(a|b){0,2}', 'aaa',False], ['(a|b){0,2}', 'bbb',False],

	['character classes'],
	['[abc]', '', False], ['[abc]', 'a'], ['[abc]', 'b'], ['[abc]', 'c'],

	['[ab]*', ''], ['[ab]*', 'a'], ['[ab]*', 'b'], ['[ab]*', 'c', False],
	['[ab]*', 'aa'], ['[ab]*', 'ab'], ['[ab]*', 'bb'], ['[ab]*', 'abc', False],
	['[ab]*', 'aaa'], ['[ab]*', 'abab'], ['[ab]*', 'abba'],
	['[a1]*', 'aaa'], ['[a1]*', 'a1a1'], ['[a1]*', 'a11a'],

	['numbers'],
	[[],[]], [[1],[1]], [[1,2],[1,2]],  [[1],[],False], [[1,2],[1],False],
	[['.'],[1]], [['.',2],[4,2]],
	[[1,'?'],[]], [[1,'?'],[1]], [[1,'?'],[1,1],False],

	['shortcut, list of one string element is parsed to list of numbers , like above'],
	[['1,2,3'],['1,2,3']], 	[['1,|,3'],['1']], [['1,|,3'],[1]], 
	[['(,1,|,3,),3'],['3,3']], [['(,1,|,3,),3'],[3,3]], [['(,1,|,3,),3'],['3',3],False],

	['numbers and strings'],
	[[1,'2'], [1,'2']], [[1,'2','+'], [1,'2','2']], [['1',2,'+'], ['1',2,2,2]], [['1',2,'+'], ['1',2,'2'], False], 

	['complex'],
	['a*b+', 'b'], ['a*b+', 'ab'],['a*b+', 'aab'], ['a*b+', 'aabb'], ['a*b+', 'aa', False],
	['a{0,2}b+', 'aab'], ['a{0,1}b+', 'ab'], ['a{0,1}b+', 'abb'], ['a{0,1}b+', 'abbb'],

]


def check(res) : 
	return res

def run(tests) :
	n = Regex()
	passed, failed = 0,0
	for i,t in enumerate(tests) :

		if len(t) == 1 :
			print("\n>> " + t[0])
			continue
		res = check( n.match_one(t[0], t[1]) )

		expected  = t[2] if len(t) > 2 else True
		sign = '==' if expected else '!='
		msg = f'{i}> {t[0]} {sign} {t[1]}'
		if res is expected :
			print('PASS:' + msg)
			passed += 1
		else :
			print('FAIL:' + msg)
			failed += 1

	print(f"\n\n::  PASSED:{passed}, FAILED:{failed}\n")		



run(tests)
