'''
1. Tokenize:
    - Split by whitespace (determine number of tokens)
    - Clean up markers (e.g, <X, .\) and record it as attribute of the token
2. Alignment:
    1. Clean up dot annotations
    2. Align three lists (ori, en, ch)
        1. IF token is a pure DM, ignore assignment of annotaions
        2. ELSE assign token
'''


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



