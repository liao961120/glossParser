#%%
import re
import os
import pickle
import pathlib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from traverse_files import Drive
from data import Data

# Output data
CACHE = 'docs/cache.pkl'
DATA_DIR = Data().corpus_files_root

# Setup GDrive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'form-corp-data.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)
drive = Drive(drive_service)

# Load cache
with open(CACHE, "rb") as f:
    cache = pickle.load(f)
drive.read_cache(**cache)


# Search GDrive for all txt files
corpus_files = drive.list_all_txt()

# Write files to local
for txt in corpus_files:

    # Get paths
    path = pathlib.Path(DATA_DIR) / txt['fp']
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    fcontent = drive.get_file_content(txt['id'])
    with open(path, "w", encoding="utf-8") as f:
        f.write(fcontent)


# Save cache
with open(CACHE, "wb") as f:
    pickle.dump({
        'folders': drive.folders,
        'file_content': drive.file_content,
        }, f)
