#%%
import csv
import json
import pathlib
from datetime import datetime
from data import Data

DATA = Data()
META_JSON = DATA.meta
OUTPUT = [ DATA.meta_csv_languages, DATA.meta_csv_texts ]


def main():
    with open(META_JSON, encoding="utf-8") as f:
        data = json.load(f)

    lang_csv = []
    text_csv = []
    for lang, d in data.items():

        # One language per row
        story = d['summary']['story']
        sentence = d['summary']['sentence']
        row_lang = {
            'language': lang,
            'story_iuNum': story["iu_num"],
            'story_sentNum': story["sent_num"],
            'story_recordTime': str(datetime.timedelta(seconds=int(story["record_time"]))),
            'sentence_sentNum': sentence["sent_num"]
        }
        lang_csv.append(row_lang)

        # One text file per row
        texts = d['text']
        for txt in texts:
            row_txt = {
                'file': txt['file'],
                'language': lang,
                'type': txt['type'],
                'topic': get_val('topic', txt, default='NA'),
                'speaker': get_val('speaker', txt, default='NA'),
                "collected": get_val('collected', txt, default='NA'),
                "transcribed": get_val('transcribed', txt, default='NA'),
                "iu_num": get_val('iu_num', txt, default=0),
                "sent_num": get_val('sent_num', txt, default=0),
                "record_time": get_val('record_time', txt, default=0),
            }
            text_csv.append(row_txt)

    for i, csv_ in enumerate([lang_csv, text_csv]):
        outpath = pathlib.Path(OUTPUT[i])
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with open(outpath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = list(csv_[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for r in csv_: writer.writerow(r)

# %%
def get_val(key_, dict_, default):
    NAs = { '?', '' , 'NA', 'None', None, 'null', 'NULL' }
    
    if key_ in dict_:
        val = dict_[key_]
        if val not in NAs: 
            return val
    return default



if __name__ == "__main__":
    main()