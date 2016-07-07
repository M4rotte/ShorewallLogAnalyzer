#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re

def is_valid_timestamp(string):
    
    regex = re.compile('(\d){10}\.(\d){6}')
    if regex.match(string): return True
    else: return False
    
    
