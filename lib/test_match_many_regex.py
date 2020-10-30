from regex_nfa import *
from seqs_store import *
from collections import defaultdict

null = lambda x : ['']

tests = [

	#['', [''] ],
	['w', ['w'], False],['wh', ['wh'], False], ['why', ['why']], ['why?', ['why']], ['why?', ['whyy'],False],

	['wh.+', ['why','who']], ['wh.+', ['why','who','when']], ['wh.+', ['when']],
	['whe.+', ['when']],

	['wh.r.', ['where']],

	['wh..', ['when','whom']],
]


def compare(a,b,is_match=True) : 
	matched = 0
	for r in a :
		for m in b :
			if r == m :
				matched += 1
				break
	# say(a,b)
	res = ''
	if matched == 0 :
		res = 'FAIL' if is_match else 'PASS'
	elif matched == len(b) :
		res = 'FULL' if is_match else 'FAIL'
	elif matched > len(b) : 
		res = 'PASS' if is_match else 'FAIL'
	elif matched < len(b) :
		res = 'PART' if is_match else 'FAIL'

	return res, matched, len(b)			

def run(tests, end='@') :
	n = Regex()
	passed, failed = 0,0
	cnts = defaultdict(int)
	for i,t in enumerate(tests) :

		if len(t) == 1 :
			print("\n>> " + t[0])
			continue

		expected  = t[2] if len(t) > 2 else True
		sign = '==' if expected else '!='

		#remove end-char
		m = [ r[:-1] for r in n.match(t[0], words_search) ]
		res, matched, total = compare( t[1], m, expected)

		expect = f' >> {m}' if res == 'FAIL' else ''

		msg = f'{i} {matched}:{total}> {t[0]} {sign} {t[1]} {expect}'
		print(res + ':' + msg)
		cnts[res] += 1

	print(f"\n\n::  PASSED:{cnts['PASS']} FULL:{cnts['FULL']}, PARTIAL: {cnts['PART']} FAILED:{cnts['FAIL']}\n")		



run(tests)
