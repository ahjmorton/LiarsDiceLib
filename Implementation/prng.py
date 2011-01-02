from random import SystemRandom, WichmannHill

_rand = None

def get_random(seed=None) :
    global _rand
    _rand.seed(seed)
    return _rand

#Test to see if urandom is implemented
try :
    from os import urandom
    urandom(0)
    _rand = SystemRandom()
except NotImplementedError as e :
    _rand = WichmannHill()
    
