# %%
import re
import json
import pathlib
from data import Data

LING = ['AF', 'NAF', 'PF', 'RF', 'IF', 'BF', 'CF', 'LF', 'GEN']
LING = [ (re.compile(f"(^{x}$|^{x}[^a-zA-Z]|[^a-zA-Z]{x}$|[^a-zA-Z]{x}[^a-zA-Z])"), x) for x in LING ]

DATA = Data()
STORY = pathlib.Path(DATA.story_files_json)
SENTENCE = pathlib.Path(DATA.sentence_files_json)
GRAMMAR = pathlib.Path(DATA.grammar_files_json)
OUTFILE = DATA.meta


def main():
    # Main function
    meta = {}
    for lang in list(STORY.iterdir()) + list(SENTENCE.iterdir()) + list(GRAMMAR.iterdir()):
        if lang.stem not in meta:
            meta[lang.stem] = {
                'summary': {
                    "story": {
                        "iu_num": 0,
                        "sent_num": 0,
                        "record_time": 0
                    },
                    "sentence": {"sent_num": 0},
                    "grammar": {"sent_num": 0},
                    "marker": {}
                },
                'text': []
            }

        for text in lang.glob("*.json"):
            meta[lang.stem]['text'].append(get_info(text))

        # Get summaries
        if 'sentence' in str(lang.absolute()):
            meta[lang.stem]['summary']['sentence']['sent_num'] = sum(
                t['sent_num'] for t in meta[lang.stem]['text'])
        elif 'grammar' in str(lang.absolute()):
            meta[lang.stem]['summary']['grammar']['sent_num'] = sum(
                t['sent_num'] for t in meta[lang.stem]['text'])
        elif 'story' in str(lang.absolute()):
            for k in ['iu_num', 'sent_num', 'record_time']:
                meta[lang.stem]['summary']['story'][k] = round(
                    sum(t[k] for t in meta[lang.stem]['text']), 2)
        
        # Linguistic marker total counts per language
        for _, m in LING:
            meta[lang.stem]['summary']['marker'][m] = sum( t['marker'][m] for t in meta[lang.stem]['text'] )


    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent="\t")



def get_info(path):
    text = load_text(path)

    info = {}
    # Meta info
    meta = text["meta"]
    info['file'] = f"{path.parent.name}/{path.stem}"
    for k in ['type', 'speaker', 'collected']:
        try:
            info[k] = meta[k]
        except:
            print(f"WARNRING: no key: `{k}` in meta of {path}")
            pass
    
    if DATA.story_dirname in str(path.absolute()) or DATA.grammar_dirname in str(path.absolute()):
        info['topic'] = meta['topic']
    else:
        pass
        #info['transcribed'] = meta['Transcribed by']

    # Text data info
    if DATA.story_dirname in str(path.absolute()):
        info['iu_num'] = len(text["glosses"])
        info['sent_num'] = sum(g[1]['s_end'] for g in text['glosses'])

        info['record_time'] = 0
        for gloss in reversed(text["glosses"]):
            end_time = gloss[1]['iu_a_span'][-1]
            if isinstance(end_time, float):
                info['record_time'] = end_time
                break
    else:
        info['sent_num'] = len(text["glosses"])
    
    # Linguistic info
    info["marker"] = count_markers(text)

    return info


def load_text(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def count_markers(text):
    markers = { m:0 for _, m in LING}
    for m in get_markers(text):
        markers[m] += 1
    return markers

def get_markers(text):
    text = text["glosses"]
    for iu in text:
        en_tks = [ tk[1] for tk in iu[1]["gloss"]]
        for pat, marker in LING:
            for en_tk in en_tks:
                if pat.search(en_tk):
                    yield marker

if __name__ == "__main__":
    main()
