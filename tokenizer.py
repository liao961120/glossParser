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
import logging


def align(ori, en="", ch="", gloss_id=""):
    ori = [ x for x in ori.strip().split() ]
    en = [ t for t in en.strip().split() if (t != "." and t != "") ]
    ch = [ t for t in ch.strip().split() if (t != "." and t != "") ]

    if len(en) != len(ch):
        logging.warning(f"Diff. num of tokens in EN & CH annot:\t{gloss_id}")
        #raise Exception("Invalid Gloss Format!") 

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
        


def is_pureDM(x):
    # Specific rules
    if re.match(r'\[X+\]', x): return False
    
    # Default rule
    if re.match(r'^[^a-z]+$', x): return True
    else: return False



def replace_backslash(x):
    return x.replace("\\", "_FALL_")