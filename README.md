# multi_regex
Searching sequences in DBs/Sequence-stores by using Regex

check the docs directory :

https://github.com/vsraptor/multi_regex/blob/main/docs/multi-regex.ipynb

## Multi Sequence REGEX engine

I have a project where I'm storing Sequences in a graph database which for the outside apps are opaque. So I needed to some way to query the data. I tried a sort of template-search-language, but it quickly became clear it is unmanageable. After some experimenting I decided to adopt Regex-like language for searching.

I found a very nice tutorial for implementing RegEx using finite automata (NFA).

## Implementing a Regular Expression Engine

Of course this implementation is very basic and is written in java-script, I need one written in python. But second and more important problem is that this engine matches a single string against the regex.

What I require is the ability to apply regex against thousands or may be millions of sequences at once. I meant SEQUENCE not just a STRINGS /which is just sequence of characters/. I also need a support for Sequences where the items can be integers, characters, words, sentences ... etc.

The major difference between basic regex matching (BRM) and this more advanced multi-sequence-regex (MSRM) is that in BRM we advance one step (all parallel states) and one character (single sequence) at a time which is much more simple to implement.

In MSRM the advance is still one-step for the regex, but for every parallel-state there are multiple sequences that can match.

For example lets see if we search the words file in linux :

     > grep ^w /usr/share/dict/words | wc -l
     2329
     > grep ^wh /usr/share/dict/words | wc -l
     360

if we match against the following regex /wh.+/, the first step will return 2329 sequences/words (which is alot, for BRM it will be just one), the second step we get back 360.

The expectation is that incremental search will be faster than a loop that match every sequence one by one.

BTW there is option to set upper limit on how many items to select at every step, so if you get too many results you can cap them up.

There is one more option which allows you to start matching after a specific prefix/head, the idea here is to match the head as a normal match and the rest of the sequence using the regex. This way we lower the the number of comparisons dramatically, because the biggest number of results are normally at the beginning

----

Example :

     > from regex_nfa import * 
     > from seqs_store import *
     > with open('/usr/share/dict/words') as f : ww = [ l.rstrip() for l in f.readlines()]                                                                                
     > n = Regex()
     > n.match(regex='wh..', match_prefix_fun=partial(db_search,seqs=ww))   
     : ['whys.', 'whip.', 'whom.', 'whew.', 'whit.', 'wham.', 'whir.', 'whoa.', 'when.', 'whet.', 'whey.', 'whim.', 'what.', 'whiz.']
     > n.match(regex='wh.+', match_prefix_fun=partial(db_search,seqs=ww))                                                                                                 
     : ['why.', 'who.']
     > n.match(regex='wh.r..', match_prefix_fun=partial(db_search,seqs=ww))                                                                                               
     : ['wharfs.', 'whores.', 'whirls.', 'whirrs.', "whir's.", 'wheres.', 'whorls.']
     > n.match(regex='w(h|o).', match_prefix_fun=partial(db_search,seqs=ww))                                                                                              
     : ['wok.', 'woo.', 'why.', 'who.', 'wot.', 'wow.', 'woe.', 'won.']



----

#### read more in the docs directory ...
