# regular link: https://pillows.su/f/91dd7af71aa25742baa974f98e5994a0
# api link: https://api.pillows.su/api/download/91dd7af71aa25742baa974f98e5994a0 (.mp3)

import pick
import glob
import requests
import re
import os
import tsv
from data import eraNames
from tqdm import tqdm

def regularToAPI(rurl: str):
    print('[pillowcase] converting', rurl, 'to api url')
    return 'https://api.pillows.su/api/download/' + rurl.split('/')[-1]

def downloadRegular(url: str, folder: str):
    print(f'[pillowcase] registering download {url}...')
    url = regularToAPI(url)

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        cd = r.headers.get("content-disposition")
        if cd:
            filename = re.findall('filename="?(.+)"?', cd)[0].strip('"')
        else:
            filename = os.path.basename(url)

        filename = f'{folder}/{filename}'

        if not os.path.exists(filename):
            try:
                size = int(r.headers.get('content-length', 0))
                print(f'[pillowcase] downloading {filename}...')
                bar = tqdm(total=size, unit='iB', unit_scale=True)
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bar.update(len(chunk))
                bar.close()

                print(f"[pillowcase] downloaded as: {filename}")
                return filename
            except:
                print('[pillowcase] local download failure - check your internet status if this is concurrent')
                return 'Unavailable'
        else:
            return filename
    else:
        print("[pillowcase] failed to download, status:", r.status_code)
        return 'Unavailable'

def downloadEra(eraName, section):
    if eraName in eraNames:
        sectionName = os.path.splitext(os.path.basename(section))[0]
        folderName = f'{eraName}_{sectionName}'.replace(':', '-')
        if not os.path.isdir(folderName):
            os.mkdir(folderName)

        songs = []
        lastEraLine = -1
        for i in range(1, sum(1 for _ in open(section, encoding="utf8"))):
            data, type = tsv.getLine(i, section)
            
            if type == 'era':
                print(f'New era: {data["Era"]}')
                if lastEraLine > -1:
                    lastEra, _ = tsv.getLine(lastEraLine, section)
                    
                    if lastEra['Era'] == eraName:
                        print(f'Downloading era: {lastEra["Era"]}')
                        for song in songs:
                            for link in song:
                                if str(link).startswith('https://pillows.su/f/'):
                                    fn = downloadRegular(link, folderName)
                    songs = []
                lastEraLine = i
            elif type == 'song':
                print(f'Indexed entry: {data["Name"]}')
                if 'Links' in data.keys():
                    songs.append(data['Links'])
    else:
        print('invalid era given')
                

if __name__ == '__main__':
    era, _ = pick.pick(eraNames, 'Select an era to archive:')
    file, _ = pick.pick(glob.glob("tracker-tabs/*.tsv"), 'Pick a section:')
    downloadEra(era, file)
    print('[main] Finished!')