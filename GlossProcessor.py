import os
import re
import sys
import json
import pathlib
import logging
from utils import get_raw_text_meta
from tokenizer import align
from datetime import datetime
from urllib.parse import urlparse
from docx import Document
from bs4 import UnicodeDammit



def main():
    DOCS_FOLDER_PATH = r'./raw-data/long-text'
    PUBLIC_DIR = './docs'

    logging.basicConfig(level=logging.INFO, format='%(message)s', filemode='w', filename=f'{PUBLIC_DIR}/{os.path.basename(DOCS_FOLDER_PATH)}.log')
    logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

    DOCS_FOLDER_PATH = pathlib.Path(DOCS_FOLDER_PATH)
    C = GlossProcessor(docs_folder_path=DOCS_FOLDER_PATH)

    # Save as different formats    
    output_glosses = []
    for docname, content in C.data.items():
        # Flatten data to match frontend json format
        for gloss_num, gloss in content["glosses"]:
            gloss.update({
                'file': docname.replace("raw-data/", "").replace("long-text/", "").replace("sentence/", "").replace(".mp3.txt", ""),
                'num': gloss_num,
            })
            output_glosses.append(gloss)
        
        # Save separate file for each text
        fname = docname.replace("raw-data/long-text", "json-long-text").replace('.txt', '.json')
        json_dir, lang_dir, _ = fname.split('/')
        if not os.path.exists(f"{json_dir}/{lang_dir}"):
            os.makedirs(f"{json_dir}/{lang_dir}")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False)
    
    # Write flatten data to json
    with open("docs/all_lang-long-text.json", "w", encoding="utf-8") as f:
        json.dump(output_glosses, f, ensure_ascii=False)
    os.system(f"mv {json_dir} docs/")

    #-------- Get glossary --------#
    glossary = {}
    for gloss in output_glosses:
        id_ = f"{gloss['file']}#{gloss['num']}"

        gloss_set = { '=00000='.join(tup) for tup in gloss['gloss'] }

        for tk in [x.split('=00000=') for x in gloss_set]:
            
            # Normalize token pattern
            tk = [ t.strip('()/*?+-_,!.1234567890[]') for t in tk ]
            tk[0] = tk[0]
            #if tk[0] in [''] + list(PERSON_NAMES): continue
            
            sense = ' | '.join(t.strip() for t in tk[1:] if t.strip() != '')
            if sense == '': continue
            
            if tk[0] not in glossary:
                glossary[tk[0]] = {
                    sense: [id_],
                }
            else:
                if sense not in glossary[tk[0]]:
                    glossary[tk[0]][sense] = [id_]
                else:
                    glossary[tk[0]][sense].append(id_)

    # Sort and index for search
    sorted_glossary = []
    for k in sorted(glossary.keys()):
        tokens = set()

        # Add lexical entry
        tokens.add(k)
        tokens.add(k.replace('-', ''))

        # Add sense
        for sense in glossary[k]:
            for tk in sense.split('|'):
                tokens.add(tk.strip())

        # Save sorted gloss
        sorted_glossary.append( (k, glossary[k], list(tokens)) )


    with open('docs/all_lang-long-text-glossary.json', 'w') as f:
        json.dump(sorted_glossary, f, ensure_ascii=False)
    
    # Zip file for publish
    os.system('zip -r docs/json-long-text.zip docs/json-long-text')



class GlossProcessor:

    def __init__(self, docs_folder_path='.'):
        """[summary]
        
        Parameters
        ----------
        docs_folder_path : str, optional
            Path to docx files, defaults to the current dir.
        
        Notes
        ----------
        self.data structure:
        
        {
        '20200325.docx': {
            "meta": {
                'speaker': 'Balenge',
                'video': 'xxxx.mp3'
            },
            "glosses": [
                (1, {
                    'ori': ['yakay', 'ku', 'tatulru', 'ku', 'ababay/sauvalay', 'ku', 'agili'],
                    'gloss': [
                        ('yakay', 'have', '有'),
                        ('ku', 'three', '3'),
                        ('tatulru', 'female/male', '女性/男性'),
                        ('(ku', 'yonger_brother/sister-1SG.POSS', '弟妹-我的.第一人稱單數.所有格'),
                        ('ababay/sauvalay)', '_', '_'),
                        ('ku', '_', '_'),
                        ('agi-li', '_', '_')
                        ],
                    'free': [
                        '#e I have 3 younger brother/sister',
                        '#c 我有 3 個弟弟/妹妹',
                        '#n  yakay ku 可省略'
                        ],
                    's_end': True,
                    'audio_span': [1.5, 7.53]  # optional, only present in the last IU of a sentence
                    'meta': {'speaker': 'Balenge', 'video': 'xxxx.mp3'}
                    }
                ),
                (2, ...),
            ...
            },

            '20200408.docx': {"meta": {...}, "glosses": [...]},
        }
        """

        self.data = {}
        self._load_data(docs_folder_path)


    def _load_data(self, path, exts={'.docx', '.txt'}):
        path = pathlib.Path(path)
        
        for fp in path.rglob('*'):
            if fp.suffix not in exts: continue
            try:
                glosses, meta = process_doc(str(fp))
            except:
                logging.warning(f"INVALID DOCUMENT formatting:\t\t\t{fp}")
                continue
            self.data[str(fp)] = {}
            self.data[str(fp)]["glosses"] = tokenize_glosses(glosses, str(fp))
            self.data[str(fp)]["meta"] = meta



#--------------- Helper functions -------------------#
def process_doc(fp="corp/20200325.docx"):

    # Normalize document into a list of lines
    if str(fp).endswith('.docx'):
        d = Document(fp)
        a_doc = '\n'.join(p.text.strip() for p in d.paragraphs)
        a_doc = [ line.strip() for line in a_doc.split('\n') ]
    elif str(fp).endswith('.txt'):
        a_doc, _ = read_with_guessed_encoding(fp)
        a_doc = [ line.strip() for line in a_doc.split('\n') ]
    else:
        raise Exception("Unsupported format. Please provide `.docx` or `.txt`")

    # Parse metadata
    meta = get_raw_text_meta(a_doc)

    # Find the positions of each elicitation
    pat_start = re.compile(r"^(\d{1,4})\.\s*$")
    glosses_on = []
    gloss_num_old = None
    for i, line in enumerate(a_doc):
        if pat_start.match(line):
            gloss_num_new = i

            # Save each elicitation range
            if gloss_num_old is not None:
                glosses_on.append( (gloss_num_old, gloss_num_new - 1) )
            gloss_num_old = gloss_num_new
    
    # Save last gloss
    i = gloss_num_old
    while True:
        i += 1
        if a_doc[i].strip().startswith('#'):
            if len(a_doc) == i + 1 or (not a_doc[i + 1].strip().startswith('#')):
                end_idx = i + 1
                break
    glosses_on.append( (gloss_num_old, end_idx) )

    # Get all elicitations in the document
    glosses = []
    for start, end in glosses_on:
        gloss_num = int(re.match(r"(\d+)\.", a_doc[start])[1])
        gloss_lines = [ l.strip() for l in a_doc[(start + 1):end] ]
        glosses.append( (gloss_num, gloss_lines, meta.copy()) )
    
    return glosses, meta



def tokenize_glosses(glosses, filename):

    parsed_glosses = []
    for gloss_id in range(len(glosses)):
        gloss_lines, free_lines, audio_lines = assign_gloss_free_lines(glosses[gloss_id][1])

        # Deal with 3-line and 4-line formats
        num_of_lines = len(gloss_lines) 
        if num_of_lines % 3 != 0 and (num_of_lines - 1) % 3 !=0:
            logging.warning(f"INVALID GLOSS formatting:\t\t\t\t{filename}/#{glosses[gloss_id][0]:<2}")
            continue
        
        # Deal with two possible formats: gloss with/without original language
        if (num_of_lines - 1) % 3 == 0:
            ori_lang = gloss_lines.pop(0)
            num_of_lines -= 1
        else:
            ori_lang = ''

        # Concat multiple lines to three
        rk_gloss = ''
        en_gloss = ''
        zh_gloss = ''
        for i in range(int(num_of_lines / 3)):
            rk_gloss += gloss_lines[0 + i * 3] + '\t'
            en_gloss += gloss_lines[1 + i * 3] + '\t'
            zh_gloss += gloss_lines[2 + i * 3] + '\t'

        # Tokenize
        ori_lang = ori_lang.strip().split()
        tokens = align(ori=rk_gloss.strip(), en=en_gloss.strip(), ch=zh_gloss.strip(), gloss_id=f"{filename}/#{glosses[gloss_id][0]}")
        #rk_gloss = rk_gloss.strip().split()
        #en_gloss = en_gloss.strip().split()
        #zh_gloss = zh_gloss.strip().split()
        gloss = [ (tk["ori"], tk["en"], tk["ch"]) for tk in tokens ]
        free = [ l for l in free_lines if l != '' ]
        #gloss.append( (rk, en, zh) )

        # Get sentence audio play time span (if sent end)
        if '#c' in [ l[:2] for l in free ]:
            s_end = True  # record this IU's status: last IU in a sentence
            s_audio_span = get_full_sent_audio_span(glosses, parsed_glosses, audio_lines)
        else:
            s_end = False  # record this IU's status: not the last IU in a sentence
            s_audio_span = None
        
        # Save data
        iu_audio_time = get_audio_time(audio_lines)
        g = {
            'ori': ori_lang,
            'gloss': gloss,
            'free': free,
            's_end': s_end,
            'iu_a_span': [ iu_audio_time[0], iu_audio_time[-1] ],
            'meta': glosses[gloss_id][2]
        }
        if s_audio_span is not None:
            g['s_a_span'] = s_audio_span
        
        parsed_glosses.append( (glosses[gloss_id][0], g) )
    
    return parsed_glosses



def get_full_sent_audio_span(glosses, parsed_glosses, curr_IU_free_lines):
    sent_end_iu_idx = [ i for i, g in enumerate(parsed_glosses) if g[1]['s_end'] == True ]
    if len(sent_end_iu_idx) < 1: 
        this_sent_start_iu_idx = 0
    else:
        this_sent_start_iu_idx = sent_end_iu_idx[-1] + 1

    sent_starttime = get_audio_time(glosses[this_sent_start_iu_idx][1])[0]
    sent_endtime = get_audio_time(curr_IU_free_lines)[-1]

    if sent_starttime is not None and sent_endtime is not None:
        return [sent_starttime, sent_endtime]
    else:
        if sent_starttime is None:
            logging.debug(f"sent start iu idx:\t{glosses[this_sent_start_iu_idx]}")
        else:
            logging.debug(f"curr_IU_free_lines:\t{curr_IU_free_lines}")
    
    return None


def get_audio_time(free_lines):
    for line in free_lines:
        if re.match(r'#a ([0-9.]+|None), ([0-9.]+|None), ([0-9.]+|None)', line):
            times = line.replace('#a ', '').split(', ')
            times = [ float(t) if t != 'None' else None for t in times ]
            return times
    return [None, None, None]


def assign_gloss_free_lines(gloss):
    free_lines = []
    gloss_lines = []
    audio_lines = []
    
    for l in gloss:
        if l == '': 
            continue
        elif l.startswith('#a'):
            audio_lines.append(l)
        elif l.startswith('#'):
            free_lines.append(l)
        else:
            gloss_lines.append(l)

    return gloss_lines, free_lines, audio_lines



def read_with_guessed_encoding(fp: str):
    with open(fp, 'rb') as file:
       content = file.read()
    suggestion = UnicodeDammit(content)
    guessed_enc = suggestion.original_encoding

    with open(fp, 'r', encoding=guessed_enc) as f:
        return f.read().strip(), guessed_enc



if __name__ == "__main__":
    main()