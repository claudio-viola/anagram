# -*- coding: utf-8 -*-
"""
Created on Fri Dec 19 14:20:54 2014

@author: claudio
"""


#pip install gevent
import gevent.wsgi
try:
    import json
except ImportError:
    import simplejson as json 
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)


#######################
####################### Simplest solution
#######################
#to install
#brew install enchant
#pip install enchant
#import enchant
#d = enchant.DictWithPWL("en_GB","scrabble.txt")
#
#def get_anagrams(words):
#    response = {}
#    for i in words:
#      #initialize dict value
#      response[i] = []
#      for j in anagrams(i):
##        if d.check(j):
#            response[i].append(j)
#    return response
#            
##http://codereview.stackexchange.com/questions/52038/simple-anagram-or-permutation-generator-in-python
####simple but slow recursive anagram generator
#def anagrams(word):
#    """ Generate all of the anagrams of a word. """ 
#    if len(word) < 2:
#        yield word
#    else:
#        for i, letter in enumerate(word):
#            if not letter in word[:i]: #avoid duplicating earlier words
#                for j in anagrams(word[:i]+word[i+1:]):
#                    yield j+letter 
#######################
####################### Simplest solution
#######################




##############################################
### TRIE DATA structure to speed up anagram generation
### Knowing that the trie data structure speeds up the search for anagrams i slightly modified
### this open sourced solution
### http://stackoverflow.com/questions/55210/algorithm-to-generate-anagrams
##############################################
trie_dict=None
MIN_WORD_SIZE = 1
class Node(object):
    def __init__(self, letter='', final=False, depth=0):
        self.letter = letter
        self.final = final
        self.depth = depth
        self.children = {}
    def add(self, letters):
        node = self
        for index, letter in enumerate(letters):
            if letter not in node.children:
                node.children[letter] = Node(letter, index==len(letters)-1, index+1)
            node = node.children[letter]
            
    def anagram(self, letters):
        tiles = {}
        for letter in letters:
            tiles[letter] = tiles.get(letter, 0) + 1
        min_length = len(letters)
        return self._anagram(tiles, [], self, min_length)
        
    def _anagram(self, tiles, path, root, min_length):
        if self.final and self.depth >= MIN_WORD_SIZE:
            word = ''.join(path)
            length = len(word.replace(' ', ''))
            if length == min_length:
                yield word       

        for letter, node in self.children.iteritems():
            count = tiles.get(letter, 0)
            if count == 0:
                continue
            tiles[letter] = count - 1
            path.append(letter)
            for word in node._anagram(tiles, path, root, min_length):
                yield word
            path.pop()
            tiles[letter] = count

def load_dictionary(path):
    result = Node()
    for line in open(path, 'r'):
        word = line.strip().lower()
        result.add(word)
    return result
    
    
def get_anagrams(words):
    response = {}
    for i in words:
      #initialize dict value
      response[i] = []
      for word in trie_dict.anagram(i):
        response[i].append(word)
    return response
############# TRIE SOLUTION



def test():
    global trie_dict
    trie_dict = load_dictionary('scrabble.txt')
    words = ["crepitus","paste"]
    #get_anagrams(words)
    print get_anagrams(words)
    
    
def main():
    global trie_dict
    trie_dict = load_dictionary('scrabble.txt')
    listening_port=9999
    server=gevent.wsgi.WSGIServer(('', listening_port), application)
    server.serve_forever()

def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET':
      path = environ.get('PATH_INFO', '').lstrip('/')
      words = path.split(',')
      start_response('200 OK', [('Content-Type', 'application/json')])
      return json.dumps(get_anagrams(words))

    
if __name__ == "__main__":
   main()    