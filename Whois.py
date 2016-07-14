#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from subprocess import check_output, CalledProcessError
from pprint import pprint
import random
import sys
import re

class Whois:
    """ Whois requests and interpretation of the results. """
    
    response = ''
    result   = []
    
    def request(self,search):
        """ Query whois servers using system command and return a string. """
        
        try:
            response = check_output(['whois',search])
            self.response =  response.decode('unicode_escape')
        except CalledProcessError as e:
            print(e, file=sys.stderr)
            self.response = ''
                
        return self.response
        
    def getResult(self):
        """ Read the string produced by the `request` function
            and return the data as a list of dictionaries (one dictionary per "block"). """
        
        block = {}
        for line in self.response.split("\n"):

            kv = line.split(':')
            # Ignore comment lines
            if (not re.match(r'^#|^%', line)):
                # if split not empty : add element to the current block dictionary.
                if (kv != ['']):
                    key = kv[0]
                    try:
                        # Next line is the continuation of the same whois object ? Then :
                        try:
                            value = block[key]+"\n"+kv[1].strip()
                        except IndexError:
                            value = block[key]
                    except IndexError:
                        # No value
                        value = '' 
                    except KeyError:
                        # New whois object
                        try:
                            value = kv[1]
                        except IndexError:
                            value = ''    
                    # Get ride of unecessary spaces     
                    block[key] = value.strip()
                # else, and if we have already a block : append the block to the result list and empty the block dict.    
                elif (len(block) > 1):
                    self.result.append(block)
                    block = {}

        return self.result


if (__name__ == "__main__"):

    rand_ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    whois = Whois()
    whois.request(rand_ip)

    pprint(whois.getResult())
        
