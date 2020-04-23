import pandas as pd

def parse(s, q):
    pos = s.find(q)
    if pos == -1:
        raise LookupError
    else:
        s1 = s[pos + len(q)+1:]
        out = s1[:s1.find("\n")]
        return out

def extract_id(s):
    return s[s.find("/in/")+4: -1]