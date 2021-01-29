#%%
import json
import pathlib

JSON_LONG_TEXT = pathlib.Path('docs/json-long-text')
OUTFILE = 'docs/long-text-meta.json'


def get_info(text: dict):
    info = {}
    # Meta info
    meta = text["meta"]
    info['file'] = meta['video'].strip('.mp3')
    info['topic'] = meta['topic']
    info['type'] = meta['type']
    info['speaker'] = meta['speaker']
    info['collected'] = meta['collected']

    # Text data info
    info['iu_num'] = len(text["glosses"])
    info['sent_num'] = sum( g[1]['s_end'] for g in text['glosses'] )

    info['record_time'] = 0
    for gloss in reversed(text["glosses"]):
        end_time = gloss[1]['iu_a_span'][-1]
        if isinstance(end_time, float):
             info['record_time'] = end_time
             break
    
    return info


def load_long_text(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Main function
meta = {}
for lang in JSON_LONG_TEXT.iterdir():
    meta[lang.stem] = {
        'summary': {},
        'text': []
    }

    for text in lang.glob("*.json"):
        text = load_long_text(text)
        meta[lang.stem]['text'].append(get_info(text))
    
    for k in ['iu_num', 'sent_num', 'record_time']:
        meta[lang.stem]['summary'][k] = round(sum( x[k] for x in meta[lang.stem]['text'] ), 2)


with open(OUTFILE, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent="\t")
