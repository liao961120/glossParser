import re
import logging

def get_raw_text_meta(doc):
    if isinstance(doc, str):
        with open(doc, encoding="utf-8") as f:
            doc = f.read().strip()
    elif isinstance(doc, list):
        pass
    else:
        raise Exception("invalid input format")

    # Parse metadata
    meta = {}
    for line in doc:
        if line == "": break  # Break if encounter the 1st empty line
        line = strQ2B(line)
        first_col_idx = line.index(':')
        k, v = line[:first_col_idx].strip(), line[(first_col_idx + 1):].strip()
        k = k.lower()
        if k.startswith("transcribe"): continue
        if k.startswith("speaker"):
            birth = re.search(r'\d\d\d\d')
            try:
                ch_name, en_name, gender, birth = [ x.strip() for x in v.split(',') ]
                birth = re.search(r'\d\d\d\d', birth)
                if birth is not None: birth = birth[0]
                v = f"{ch_name}, {en_name}, {gender}, {birth}"
            except:
                logging.warning('Failed to parse speaker!')
                pass
        meta[k] = v
    
    return meta


# 半形轉全形函數
def strB2Q(ustring):
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 32:
                inside_code = 12288
            elif (inside_code >= 33 and inside_code <= 126):
                inside_code += 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)


def strQ2B(ustring):
    """把字串全形轉半形"""
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全形空格直接轉換
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全形字元（除空格）根據關係轉化
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)