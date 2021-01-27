import json
import requests
from .db import Templates


def flatDict(z, sep='-'):
    val = {}
    for i in z.keys():
        if isinstance(z[i], dict):
            get = flatDict(z[i], sep)
            for j in get.keys():
                val[i + sep + j] = get[j]
        else:
            val[i] = z[i]
    return val


def unflatDict(d, sep='-'):
    resultDict = dict()
    for key, value in d.items():
        parts = key.split(sep)
        d = resultDict
        for part in parts[:-1]:
            if part not in d:
                d[part] = dict()
            d = d[part]
        d[parts[-1]] = value
    return resultDict


def fetchData(from_date):
    print('*****FETCH DATA*****')
    with open('master_data.json', 'r') as rf:
        # print(json.load(rf))
        return json.load(rf)


def loadData(from_date):
    data = fetchData(from_date)
    print(data)
    flattened_data = [flatDict(rec) for rec in data]
    return flattened_data


def getEntityData(entities, flattened_data):
    entity_data = []
    for record in flattened_data:
        attrbs = set(record.keys())
        entity_data.append(
            {item: (record[item] if item in attrbs else None) for item in entities})
    return entity_data


def getUIData(entities, from_date=''):
    flattened_data = loadData(from_date)
    data = getEntityData(entities, flattened_data)
    return [unflatDict(item) for item in data]
