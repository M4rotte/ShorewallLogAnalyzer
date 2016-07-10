#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import markdown
import time

def generateDirs(sla, output_dir = './www/'):

    try:
        os.mkdir(output_dir,mode=0o755)
        os.mkdir(output_dir+'addresses',mode=0o755)
        os.mkdir(output_dir+'networks',mode=0o755)
        os.mkdir(output_dir+'entities',mode=0o755)
    except FileExistsError as e:
        sla.log(e)

def generateAddressPages(sla, output_dir = './www/'):

    HTML_START = '<html>\n<body>\n'
    HTML_END   = '\n</body>\n</html>\n'

    generateDirs(sla)

    sla.initDB(sla.initDBFilename,sla.dbFilename)
    ret = sla.dbCursor.execute("SELECT address, network_name, network_country from addresses_view")
    addresses = ret.fetchall()

    sla.log("Generating "+str(len(addresses))+" address pages.")
    for address in addresses:
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
                elif (i == 6 or i == 7 or i == 1):
                    md += '['+p[i]+'](./'+p[i]+'.html) '    
                else:   
                    md += str(p[i])+' '
            md += '\n'
        html = HTML_START 
        html += markdown.markdown(md)
        html += HTML_END
        f = open(output_dir+'addresses/'+address[0]+'.html','w')
        f.write(html)
        f.close()      

def generateIndexPage(sla, output_dir = './www/'):

    HTML_START = '<html>\n<body>\n'
    HTML_END   = '\n</body>\n</html>\n'

    sla.initDB(sla.initDBFilename,sla.dbFilename)
    sla.log("Generating index page.")
    md = ''
    sla.log("Networks...")
    ret = sla.dbCursor.execute("SELECT * FROM networks;")
    networks = ret.fetchall() 
    md += '## Networks\n'
    for network in networks:
        network_link='['+network[0]+'](./'+network[0]+'.html) '
        md += ' - '+network_link+' '+' '.join(network[1:-1])
        md += '\n'
    sla.log("Addresses...")    
    ret = sla.dbCursor.execute("SELECT address, network_name, network_country FROM addresses_view")
    addresses = ret.fetchall()      
    md += '## Addresses\n'
    for address in addresses:
        address_link='['+address[0]+'](./addresses/'+address[0]+'.html) '
        md += ' - '+address_link+' '+' '.join(address[1:])
        md += '\n'
    html = HTML_START 
    html += markdown.markdown(md)
    html += HTML_END
    f = open(output_dir+'index.html','w')
    f.write(html)
    f.close()           
  
    return True
    
def generateContent(sla):
    
    generateAddressPages(sla)
    generateIndexPage(sla)
    return True
