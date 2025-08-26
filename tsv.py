import re
from data import eras, eraNames

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

def getLine(num: int, tsvFile: str):
    line = ''
    with open(tsvFile, 'r', encoding="utf8") as f:
        line = f.readlines()[num - 1]

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