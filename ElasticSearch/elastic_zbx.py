#!/usr/bin/python
# coding=utf-8
import os
import sys
import json
import urllib
import time

ttl = 60

stats = {
    'cluster': 'http://localhost:9200/_cluster/stats',
    'nodes'  : 'http://localhost:9200/_nodes/stats',
    'indices': 'http://localhost:9200/_stats',
    'health' : 'http://localhost:9200/_cluster/health'
}

def get_cache(api):
    cache = '/tmp/elastizabbix-{0}.json'.format(api)
    lock = '/tmp/elastizabbix-{0}.lock'.format(api)
    jtime = os.path.exists(cache) and os.path.getmtime(cache) or 0
    if time.time() - jtime > ttl and not os.path.exists(lock):
        open(lock, 'a').close() 
        urllib.urlretrieve(stats[api], cache)
        os.remove(lock)
    ltime = os.path.exists(lock) and os.path.getmtime(lock) or None
    if ltime and time.time() - ltime > 300:
        os.remove(lock)
    return json.load(open(cache))

def get_stat(api, stat):
    d = get_cache(api)
    keys = []
    for i in stat.split('.'):
        keys.append(i)
        key = '.'.join(keys)
        if key in d:
            d = d.get(key)
            keys = []
    return d

def discover_nodes():
    d = {'data': []}
    for k,v in get_stat('nodes', 'nodes').iteritems():
        d['data'].append({'{#NAME}': v['name'], '{#NODE}': k})
    return json.dumps(d)

def discover_indices():
    d = {'data': []}
    for k,v in get_stat('indices', 'indices').iteritems():
        d['data'].append({'{#NAME}': k})
    return json.dumps(d)

if __name__ == '__main__':
    api = sys.argv[1]
    stat = sys.argv[2]
    if api == 'discover':
        if stat == 'nodes':
            print discover_nodes()
        if stat == 'indices':
            print discover_indices()
    else:
        stat = get_stat(api, stat)
        if isinstance(stat, dict):
            print ''
        else:
            print stat

