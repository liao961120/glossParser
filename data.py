#%%
import logging


class Data:
    # Input data
    corpus_files_root = "raw-data/"
    story_files_raw = "raw-data/story/"
    sentence_files_raw = "raw-data/sentence/"

    # Publish files
    public = "docs/"
    all_lang_search = "docs/all_lang.json"
    story_files_json = "docs/story/"
    sentence_files_json = "docs/sentence/"
    meta = "docs/text-meta.json"
    meta_csv_languages = "docs/meta/langMetas.csv"
    meta_csv_texts = "docs/meta/txtMetas.csv"

    # Generated
    story_dirname = story_files_raw.split('/')[1]
    sentence_dirname = sentence_files_raw.split('/')[1]


    def check_corpus_type(self, fp):
        if self.story_dirname in fp: return "story"
        if self.sentence_dirname in fp: return "sentence"
        logging.warning("Invalid corpus type, should be story or sentence")
        return None


    def get_public_fp(self, fp:str):
        if self.check_corpus_type(fp) == 'story':
            fp = fp.replace(self.story_files_raw, self.story_files_json)
            return fp.replace(".txt", ".json")
        if self.check_corpus_type(fp) == 'sentence':
            fp = fp.replace(self.sentence_files_raw, self.sentence_files_json)
            return fp.replace(".txt", ".json")
        raise Exception(f'Cannot derive public file path from {fp}')

# %%
