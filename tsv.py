import re
import requests
from data import eras, eraNames

tsvGID = {
    'Unreleased': 199908479,
    'Released': 1295931150,
    'Stems': 495336364,
    'Album Copies': 1297512832,
    'Miscellaneous': 70063278
}

def createTSVfromGID(gid: int):
    print('[createTSVfromGID] fetching latest tracker version...')
    url = f'https://docs.google.com/spreadsheets/d/1oGgQrlUxxoGNAiKa_98vhjxR96pxJ3OdvVHKqpvb29w/export?format=tsv&id=1oGgQrlUxxoGNAiKa_98vhjxR96pxJ3OdvVHKqpvb29w&gid={gid}'
    response = requests.get(url)

    if response.ok:
        return response.content.decode('utf-8').splitlines()
    else:
        print('[createTSVfromGID] failed to fetch tracker content. exiting...')
        exit()

def detectLineType(line: str):
    split = line.split('\t')
    tag = split[0]
    name = ''
    if len(split) > 1:
        name = split[1]
    if tag in eraNames:
        return 'song'
    else:
        split = name.strip()
        eraName = ''
        if len(split) > 1:
            eraName = re.sub("\(.*?\)", '', name).replace('(', '').replace(')', '').strip()

        if eraName in eraNames:
            return 'era'
        else:
            if tag == '':
                return 'event'
            else:
                return 'other'

def packageSongTSVline(line: str):
    split = line.split("\t")
    
    data = {
        'Era': split[0],
        'Name': split[1],
        'Notes': split[2],
        'File Date': split[3],
        'Leak Date': split[4],
        'Available Length': split[len(split) - 3],
        'Quality': split[len(split) - 2],
        'Links': split[len(split) - 1].splitlines(),
    }

    return data

def packageEraLine(line: str):
    split = line.split('\t')
    eraName = re.sub("\(.*?\)", '', split[1]).replace('(', '').replace(')', '').strip()
    return {
        'Era': eraName.strip(),
        'Description': ' '.join(split[2:len(split)]).strip(),
        'Art': 'art/' + eraName.replace(':', '-') + '.png',
    }

def packageEventLine(line: str):
    split = line.strip().split('\t')
    desc = ''
    if len(split) > 1:
        desc = split[1]
    return {
        'Name': split[0],
        'Description': desc,
    }

def getLine(num: int, tsv: list):
    line = tsv[num - 1]

    type = detectLineType(line)
    final = None
    if type == 'song':
        final = packageSongTSVline(line)
    elif type == 'era':
        final = packageEraLine(line)
    elif type == 'event':
        final = packageEventLine(line)
    else:
        final = [line]

    return final, type