import os
import csv
import pylightxl as xl
from pathlib import Path
from data import Data


LANG_MAP = {
    "Kanakanavu": ["卡那卡那富語", "Kanakanavu"],
    "Sakizaya": ["撒奇萊雅語", "Sakizaya"],
    "Seediq": ["賽德克語", "Tgdaya"]
}
DATA_DIR = Data().grammar_files_raw
OUTDIR = Path("docs/grammar-basicTerms/")


def main():
    if not OUTDIR.exists(): OUTDIR.mkdir(parents=True)

    # Download Google sheets as TSVs
    excel = OUTDIR / "Grammar-基本詞彙.xlsx"
    download_excel(outfp=excel)
    export_sheets(excel, outdir=OUTDIR)

    # To Do: convert TSVs to Gloss text files (then glossParser can handle the text files as usual)
    for fp in OUTDIR.glob("*.tsv"):
        with open(fp, newline='', encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter="\t", quotechar='"')
            txt = text_head(lang=fp.stem)
            i = 1
            for r in reader:
                if r["從語料庫移除"] == "刪除": continue
                ori = r["族語"]
                ch = r["中文翻譯"]
                a_url = r["覆寫音檔網址"].strip()
                if a_url == "":
                    a_url = r["音檔網址"].strip()
                if a_url.lower().startswith("http://ABSENT") or a_url.lower().startswith("https://ABSENT"):
                    a_url = ""
                if a_url.startswith("https://drive.google.com/file/d/"):
                    a_url = a_url.replace("https://drive.google.com/file/d/", "").split("/")[0]
                txt += row2gloss_A2(i, ori, ch, a_url) + '\n'
                i += 1

        lang = fp.stem  # Seediq.tsv
        outdir = Path(DATA_DIR) / f"{lang}_{LANG_MAP[lang][1]}"  # raw-data/grammar/Seediq_Tgdaya
        outdir.mkdir(exist_ok=True, parents=True)
        with open(outdir / "A2.txt", "w", encoding="UTF-8") as f:
            f.write(txt)


def download_excel(outfp):
    """Download 基本詞彙 gsheet as an excel file
    """
    url = f"https://docs.google.com/spreadsheets/d/1e9SWmw0huaCxw80lVLAGJd9DuFs1YClny1eMO2fP7fk/export?format=xlsx"
    cmd = f'curl -H "Cache-Control: no-cache" -o "{outfp}" --location "{url}"'
    os.system(cmd)


def export_sheets(fp, outdir=None):
    """Export excel into multiple sheets of TSV files
    """
    infile = Path(fp)
    if outdir is None:
        outdir = infile.parent
    db = xl.readxl(fn=fp)
    for sheet in db.ws_names:
        with open(outdir/f"{sheet}.tsv", "w", newline='', encoding="UTF-8") as f:
            writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
            writer.writerows(db.ws(ws=sheet).rows)


#### TSV to gloss plaintext ####
def text_head(lang):
    txt = f"""type: GrammarBook
topic: 附錄二　基本詞彙
language: {LANG_MAP[lang][0]}, {lang}, {LANG_MAP[lang][1]}
"""
    return txt

def row2gloss_A2(i, ori, ch, a_url):
    len_ch = len(ch.split())
    align = ' '.join( [ '_' ]*len_ch )
    g = f"""
{i}.
{ori}

{ch}
_
_

"""
    if a_url != "":
        g += f"#a_url {a_url}\n"
    return g



if __name__ == "__main__":
    main()
