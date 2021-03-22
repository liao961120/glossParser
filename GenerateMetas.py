# %%
import json
import pathlib
from data import Data

DATA = Data()
STORY = pathlib.Path(DATA.story_files_json)
SENTENCE = pathlib.Path(DATA.sentence_files_json)
OUTFILE = DATA.meta


def main():
    # Main function
    meta = {}
    for lang in list(STORY.iterdir()) + list(SENTENCE.iterdir()):
        if lang.stem not in meta:
            meta[lang.stem] = {
                'summary': {
                    "story": {
                        "iu_num": 0,
                        "sent_num": 0,
                        "record_time": 0
                    },
                    "sentence": {"sent_num": 0}
                },
                'text': []
            }

        for text in lang.glob("*.json"):
            meta[lang.stem]['text'].append(get_info(text))

        if 'sentence' in str(lang.absolute()):
            meta[lang.stem]['summary']['sentence']['sent_num'] = sum(
                t['sent_num'] for t in meta[lang.stem]['text'])
        else:
            for k in ['iu_num', 'sent_num', 'record_time']:
                meta[lang.stem]['summary']['story'][k] = round(
                    sum(t[k] for t in meta[lang.stem]['text']), 2)


    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent="\t")



def get_info(path):
    text = load_text(path)

    info = {}
    # Meta info
    meta = text["meta"]
    info['type'] = meta['type']
    info['speaker'] = meta['speaker']
    info['collected'] = meta['collected']
    info['file'] = f"{path.parent.name}/{path.stem}"

    if 'story' in str(path.absolute()):
        info['topic'] = meta['topic']
        info['file'] = meta['video'].strip('.mp3')
    else:
        info['transcribed'] = meta['Transcribed by']

    # Text data info
    if 'sentence' in str(path.absolute()):
        info['sent_num'] = len(text["glosses"])
    else:
        info['iu_num'] = len(text["glosses"])
        info['sent_num'] = sum(g[1]['s_end'] for g in text['glosses'])

        info['record_time'] = 0
        for gloss in reversed(text["glosses"]):
            end_time = gloss[1]['iu_a_span'][-1]
            if isinstance(end_time, float):
                info['record_time'] = end_time
                break

    return info


def load_text(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)



if __name__ == "__main__":
    main()