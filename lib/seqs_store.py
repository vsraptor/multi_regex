from functools import partial

isi = isinstance

words = ['who','why','when','where', 'whom','which','what','word','while','whole','whammy','with','woman','work','abc']
seqs  = [[1,2,3], [1,2,3,4], [1,3,4], [1,2,5,6], [1,2,5,7], [1,2,3,4,5], [1,1,3,4]]
sents = [['hi', 'world'], ['hello', 'world'], ['howdy', 'world'], ['hi', 'buddy'], ['hey', 'ho'], ['hi','hi']]

def db_search(prefix, seqs=seqs, head=None, end='.'):
	islst = isi(prefix, list)
	full_prefix = prefix if head is None else head + prefix
	res = set()
	pp = len(full_prefix) + 1
	seqs = [ ( w + [end] if islst else w + end ) for w in seqs ]
	for word in seqs :
		if islst : #seq as list case
			if full_prefix == word[:len(full_prefix)] and word != full_prefix :
				res.add(str(word[:pp]))
		else : # seq as string case	
			if word.startswith(full_prefix) and word != full_prefix :
				res.add(word[:pp])
	return [ eval(r) for r in res ] if islst else list(res)	


seq_search   = partial(db_search,seqs=seqs) 
words_search = partial(db_search,seqs=words)
sents_search = partial(db_search,seqs=sents)
