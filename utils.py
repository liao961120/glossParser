import re
PAT_ZH = re.compile(u'[\u2E80-\u2FD5\u3190-\u319f\u3400-\u4DBF\u4E00-\u9FCC\uF900-\uFAAD]')
PAT_NUM = re.compile('\d+')

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
            v = anonymize(v)
        meta[k] = v
    
    return meta


def anonymize(speaker_line):
    elems = [ x.strip() for x in speaker_line.split(",") ]
    elems = [ x for x in elems if x != "none" and x != "" ]
    
    out = []
    for e in elems:
        if e in ["female", "male", "男", "女", "男性", "女性"]:
            out.append(e)
        elif has_zh(e):
            out.append(anonymize_name(e))
        elif has_num(e):
            out.append(anonymize_num(e))
    
    return ", ".join(out)


def anonymize_name(s):
    return s[0] + "〇" * (len(s) - 1)

def anonymize_num(s):
    return s[:4]


def has_zh(s):
    if PAT_ZH.search(s):
        return True
    return False


def has_num(s):
    if PAT_NUM.match(s):
        return True
    return False

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