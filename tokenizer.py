'''
1. Tokenize:
    - Split by whitespace (determine number of tokens)
2. Alignment:
    1. Align three lists (ori, en, ch)
        1. IF token is a pure DM:
            IF annotaion is dot or equal token: 
                1. Assign empty string
            ELSE: 
                1. Assign empty string
        2. ELSE assign annotation to token
'''

#%%
import re

def is_pureDM(x):
    # Specific rules
    if re.match(r'\[X+\]', x): return False
    
    # Default rule
    if re.match(r'^[^a-z]+$', x): return True
    else: return False


def align(ori, en="", ch=""):
    ori = ori.split()
    en = [ t for t in en.split() if t != "." ]
    ch = [ t for t in ch.split() if t != "." ]

    if len(en) != len(ch):
        print("Different lengths of en and ch annotation")
        raise Exception("Invalid Gloss Format!") 

    tokens = [{'ori': ori_tk, 'en': '', 'ch': '', 'is_DM': True} for ori_tk in ori]
    
    anno_idx = 0
    for i, ori_tk in enumerate(ori):
        if anno_idx == len(en) or anno_idx == len(ch):
            return tokens

        tk = {
            'ori': ori_tk,
            'en': '',
            'ch': '',
            'is_DM': is_pureDM(ori_tk)
        }

        if is_pureDM(ori_tk):
            # Assign if duplicate DM markers in annotaion
            if en[anno_idx] == ori_tk and ch[anno_idx] == ori_tk:
                tk['en'], tk['ch'] = '', ''
                anno_idx += 1
        else:
            tk['en'], tk['ch'] = en[anno_idx], ch[anno_idx]
            anno_idx += 1

        tokens[i] = tk

    return tokens 
        
#%%


##############
# TOKENS
##############

TK_L2_lBracket = 'L2_lBracket'
TK_L2_rBracket = 'L2_rBracket'
TK_LAUGHTER_lBracket = 'LAUGHTER_lBracket'
TK_LAUGHTER_rBracket = 'LAUGHTER_rBracket'



class Token:

    def __init__(self, type_, value_):
        self.type = type_
        self.value = value_

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"



