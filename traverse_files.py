# https://github.com/lopentu/keke/blob/master/dialogue/chatai/bin/download_data.py
class Drive():

    def __init__(self, service):
        self.service = service
        self.folders = {}  # {id: {id, name, parents, modifiedTime} }
        self.file_content = {}  # {id: content}

    # Cache
    def read_cache(self, folders, file_content):
        self.folders = folders
        self.file_content = file_content

    # Get .txt files
    def list_all_txt(self):
        tree = self.list_child_recursive('1anXf0owlXjyu_qc7mF-_ayNJGfo_0CiV')

        files = []
        for dir_type in tree:
            for dir_lang in dir_type['child']:
                for txt in dir_lang['child']:
                    files.append({
                        'id': txt['id'],
                        'fp': f"{dir_type['name']}/{dir_lang['name']}/{txt['name']}"
                    })
        
        return files


    def list_child_recursive(self, id_):
        files = self.list_child(id_)

        ls = []
        for f in files:
            if f['mimeType'] != 'application/vnd.google-apps.folder':
                if f['mimeType'] == 'text/plain':
                    ls.append(f)
            else:
                subdir = self.list_child_recursive(f['id'])
                ls.append({
                    "mimeType": f["mimeType"],
                    "name": f["name"],
                    "id": f["id"],
                    "child": subdir
                    })

        return ls


    def list_child(self, id_):
        q = f"'{id_}' in parents"
        resp = self.service.files().list(q=q,
                                    spaces='drive',
                                    corpora='allDrives',
                                    fields='nextPageToken, files(id, name, mimeType, parents, modifiedTime)',
                                    includeItemsFromAllDrives=True,
                                    supportsAllDrives=True).execute()
        return resp.get('files', [])



    def get_full_path(self, file_id):
        file_ = self.get_file_meta(file_id)
        is_root = False if 'parents' in file_ else True

        drive_path = []
        while not is_root:
            file_id = file_['parents'][0]
            file_ = self.get_file_meta(file_id)
            drive_path.append( (file_['name'], file_id) )
            is_root = False if 'parents' in file_ else True

        drive_path.reverse()
        return drive_path


    def get_file_meta(self, file_id, force=False):

        if (not force) and file_id in self.folders:
            return self.folders[file_id]
        else:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, parents, modifiedTime',
                supportsTeamDrives=True).execute()
            
            # update cache
            self.folders[file['id']] = file

            return file
    

    def get_file_content(self, file_id):
        if file_id not in self.file_content:
            self.file_content[file_id] = self.service.files().get_media(
                fileId=file_id).execute().decode('UTF-8')
        else:
            ometa = self.get_file_meta(file_id)
            nmeta = self.get_file_meta(file_id, force=True)
            if ometa['modifiedTime'] != nmeta['modifiedTime']:
                self.file_content[file_id] = self.service.files().get_media(
                fileId=file_id).execute().decode('UTF-8')
        
        return self.file_content[file_id]


    def get_file_content_by_folderid(self, folder_id):
        for fid, fmeta in self.folders.items():
            if ('parents' in fmeta) and (fmeta['parents'][0] == folder_id):
                return self.get_file_content(fid)
        
        return None