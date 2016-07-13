#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

try:
    
    import sys
    import urllib.request
    import json
    import os
    import csv
    import datetime
    from pprint import pprint
    import socket

except ImportError as e:
    print("Missing module : "+str(e),file=sys.stderr)
    sys.exit(1)

class RDAP:
    """ Query RDAP servers. """
    
    
    def get(self, object_type, search, URL = 'http://rdap.db.ripe.net/'):
        """ Query RDAP server. Return as JSON. """
        
        if (URL[-1:] != '/'): URL += '/'
        request    = URL+object_type+'/'+search
        print(str(datetime.datetime.now())+" RDAP:get: "+request, file=sys.stderr)
        try:
            response   = urllib.request.urlopen(request, timeout=10)
            rawdata = response.read().decode('utf-8')
            response.close()
            data  = json.loads(rawdata)        
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
            print(e,file=sys.stderr)
            return False
        
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
            
            rawdata = open(ASRFilename,'r')
            split = csv.reader(rawdata, delimiter=',', quotechar='"')
        
        for line in split:
            net = line[0].split('/')[0]
            if (net):
                self.prefix[str(net)] = (line[1],line[4])

        return self.prefix  
        
    def getNetwork(self, search):
        """ Return a tuple from the JSON response. """
        
        self.getASR()
        prefix = search.split('.')[0].zfill(3)
        rdap_url = self.prefix[prefix][1].split('http://')[0]
        name     = self.prefix[prefix][0]
        if (not rdap_url):
            
            return (prefix+"/8", name, '', '', '', '', '', '')
            
        entities = []
        data = self.get('ip',search,rdap_url)
        try:
            handle         = data.get('handle', '')
            name           = data.get('name', '')
            country        = data.get('country','')
            type           = data.get('type','')
            start_addr     = data.get('start_addr','')
            end_addr       = data.get('end_addr','')
            parent_handle  = data.get('parent_handle','')
            source         = rdap_url
        except AttributeError:
            return ('','','','','','','','','')
        try:
            for e in data['entities']:
                entities.append(e['handle'])
        except KeyError:
            pass
        
        #~ print(handle, name, country, type, start_addr, end_addr, parent_handle, ' '.join(entities), source)    
        return (handle, name, country, type, start_addr, end_addr, parent_handle, ' '.join(entities), source)

    def getEntity(self, search, rdap_url):
        """ Return a tuple from the JSON response. """

        entities = []
        data = self.get('entity',search,rdap_url)
        try:
            handle         = data.get('handle', '')
            vcard          = data.get('vcardArray', '')
            source         = rdap_url
        except AttributeError:
            return ('','','','','','','','','')
        try:
            for e in data['entities']:
                entities.append(e['handle'])
        except KeyError:
            pass
        
        return (handle, vcard, ' '.join(entities), source)

rdap = RDAP()

def getNetwork(search):
    
    return rdap.getNetwork(search)
 
def getASR():
    
    return rdap.getASR() 

def getEntity(search, rdap_url):
    
    return rdap.getEntity(search, rdap_url)
 
if (__name__ == "__main__"):
    
    try:
        #~ rdap.getASR()
        print(rdap.getNetwork(sys.argv[1]))
        #~ pprint(rdap.getEntity(sys.argv[1],sys.argv[2]))  
    except IndexError:
        pass
        
