import os


def main():
    # edit: https://docs.google.com/spreadsheets/d/1e9SWmw0huaCxw80lVLAGJd9DuFs1YClny1eMO2fP7fk/edit#gid=0
    public_id = "2PACX-1vSQFe8VipLkFYIaW0JPVl8QNzUIhv6xM26MaPeJwYT1I937_En4os3QS3ZLWP8rKfMLdVSfJrU3bkAL"
    sheet_gid = {
        "Kanakanavu": '0',
        "Sakizaya": '1934945209',
        "Seediq": '671678733',
    }

    # Download Google sheets as TSVs
    for k, gid in sheet_gid.items():
        download_gsheet(gid=gid, public_id=public_id, outfp=f"{k}.tsv")

    # To Do: convert TSVs to Gloss text files (then glossParser can handle the text files as usual)



def download_gsheet(gid, public_id, outfp):
    url = f"https://docs.google.com/spreadsheets/d/e/{public_id}/pub?gid={gid}&single=true&output=tsv"
    cmd = f'curl -o "{outfp}" --location "{url}"'
    os.system(cmd)


if __name__ == "__main__":
    main()
