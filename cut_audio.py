import os
import json
import pathlib
import logging
from datetime import datetime
from pydub import AudioSegment

JSON_LONG_TEXT_DIR = pathlib.Path('json-long-text')
RAW_AUDIO_DIR = pathlib.Path('audio/raw')
SPLIT_AUDIO_DIR = pathlib.Path('audio/split')


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s', filemode='w', filename=f'cut_audio.log')
    logging.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

    for fp in JSON_LONG_TEXT_DIR.rglob("*/*.json"):
        # Segment mp3 files
        mp3_path = RAW_AUDIO_DIR / get_audio_fname(fp)
        if mp3_path.exists():
            # Parse long text file to get audio ranges
            audio_splits = get_audio_split(fp)
            mp3 = AudioSegment.from_file(mp3_path, format="mp3")
            segment_audio(mp3, audio_splits, out_dir=SPLIT_AUDIO_DIR, ori_mp3_path=mp3_path)
        else:
            print(f'{mp3_path} does not exist!')



def get_audio_fname(json_path):
    with open(json_path, encoding="utf-8") as f:
        text = json.load(f)
    return text["meta"]["video"]


def get_audio_split(json_path):
    with open(json_path, encoding="utf-8") as f:
        text = json.load(f)
    
    audio_split_range = []
    glosses = text["glosses"]
    for gid, g in glosses:
        if split_time_isval(g["iu_a_span"]):
            audio_split_range.append(g["iu_a_span"])
        else:
            logging.info(f'"iu_a_span" time invalid: {json_path}#{gid}')

        if g["s_end"]:
            try:
                span = g["s_a_span"]
            except:
                logging.info(f'No "s_a_span": {json_path}#{gid}')
                continue
            
            if split_time_isval(span):
                audio_split_range.append(span)
            else:
                logging.info(f'"s_a_span" time invalid: {json_path}#{gid}')
    
    return audio_split_range


def split_time_isval(time_split):
    s, e = time_split
    if isinstance(s, float) and isinstance(e, float):
        return True
    return False


def segment_audio(audio, ranges, out_dir, ori_mp3_path):
    if not os.path.exists(out_dir): os.mkdir(out_dir)
    out_dir = pathlib.Path(out_dir)
    
    for rng in ranges:
        s, e = rng[0]*1000, rng[1]*1000
        
        fp = out_dir / f"{ori_mp3_path.stem}_{rng[0]}-{rng[1]}.mp3"
        audio[s:e].export(fp, format="mp3")



if __name__ == "__main__":
    main()