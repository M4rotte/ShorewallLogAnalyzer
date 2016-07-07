#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import urllib.request
import json
from pprint import pprint
import sys

class RDAP:
    
    URL = 'http://rdap.db.ripe.net/'
    
    def get(self, object_type, search):
        
        request    = self.URL+object_type+'/'+search
        try:
            response   = urllib.request.urlopen(request)
            rawdata = response.read().decode('utf-8')
            response.close()
            data  = json.loads(rawdata)        
        except urllib.error.HTTPError as e:
            print(e,file=sys.stderr)
            data = {}
        
        return data
        
    def getNetwork(self, search):
        
        entities = []
        data = self.get('ip',search)
        handle         = data.get('handle', '')
        name           = data.get('name', '')
        country        = data.get('country','')
        type           = data.get('type','')
        start_addr     = data.get('start_addr','')
        end_addr       = data.get('end_addr','')
        parent_handle  = data.get('parent_handle','')
        
        try:
            for e in data['entities']:
                entities.append(e['handle'])
        except KeyError:
            pass
            
        return (handle, name, country, type, start_addr, end_addr, parent_handle, ' '.join(entities))

rdap = RDAP()
def getNetwork(search):
    
    return rdap.getNetwork(search)
 
if (__name__ == "__main__"):
    
    rdap = RDAP()
    try:
        pprint(rdap.getNetwork(sys.argv[1]))
    except IndexError:
        pass
        
