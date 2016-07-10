#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import markdown
import time

HTML_START = '<html>\n<body>\n'
HTML_END   = '\n</body>\n</html>\n'

def generateAddressPages(sla, output_dir = './www/'):

    try:
        os.mkdir(output_dir,mode=0o755)
    except FileExistsError as e:
        sla.log(e)

    sla.initDB(sla.initDBFilename,sla.dbFilename)
    ret = sla.dbCursor.execute("SELECT address, network_name, network_country, address_name from addresses_view")
    addresses = ret.fetchall()

    sla.log("Generating "+str(len(addresses))+" address pages.")
    for address in addresses:
        f = open(output_dir+address[0]+'.html','w')
        query = r'SELECT * FROM packets WHERE SRC = ? OR DST = ? ORDER BY chain, action, timestamp DESC'
        ret = sla.dbCursor.execute(query, (address[0], address[0]))
        packets = ret.fetchall()
        md = '# '+' '.join(address[0:4])+'\n'
        md += '## Packets\n'
        for p in packets:
            md += ' - '
            for i in range(0,11):
                if i == 0:
                    md += time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p[i]))+' '
                else:   
                    md += str(p[i])+' '
            md += '\n'
        html = HTML_START 
        html += markdown.markdown(md)
        html += HTML_END
        f.write(html)
        f.close()      
          
  
    return True
    
def generateContent(sla):
    
    generateAddressPages(sla)
    return True
