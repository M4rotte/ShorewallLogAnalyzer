#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import urllib.request
import json
import sys
import os

class RDAP:
    """ Query RDAP servers. """
    
    URL = 'http://rdap.db.ripe.net/'
    
    def get(self, object_type, search):
        """ Query RDAP server. Return as JSON. """
        
        request    = self.URL+object_type+'/'+search
        try:
            response   = urllib.request.urlopen(request)
            rawdata = response.read().decode('utf-8')
            response.close()
            data  = json.loads(rawdata)        
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print(e,file=sys.stderr)
            data = {}
        
        return data
    
    def getASR(self):
        """ Query IANA Address Space Registry. """
        
        ASRFilename = './ASR.csv'
        self.prefix = {}
        if (not os.path.isfile(ASRFilename)):
            
            URL = 'http://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.csv'
            request    = URL
            try:
                response   = urllib.request.urlopen(request)
                rawdata = response.read().decode('utf-8')
                response.close()
                ASRFile = open(ASRFilename,'w')
                ASRFile.write(rawdata)
                ASRFile.close() 

            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                print(e,file=sys.stderr)

        else:
            
            rawdata = open(ASRFilename,'r').read()  

        split = rawdata.split('\n')
        
        for line in split:
            l = line.split(',')
            net = l[0].split('/')[0]
            if (net):
                self.prefix[str(net)] = (l[1],l[4])

        return self.prefix  
        
    def getNetwork(self, search):
        """ Return a tuple from the JSON returned. """
        
        self.getASR()
        prefix = search.split('.')[0].zfill(3)
        rdap_url = self.prefix[prefix][1]
        name     = self.prefix[prefix][0]
        
        if (not rdap_url):
            
            return (prefix+"/8", name, '', '', '', '', '', '')
            
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
 
def getASR():
    
    return rdap.getASR() 
 
if (__name__ == "__main__"):
    
    try:
        rdap.getASR()
        print(rdap.getNetwork(sys.argv[1]))
    except IndexError:
        pass
        
