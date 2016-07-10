#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import markdown
import time
import urllib.parse
import shutil


def generateDirs(sla, output_dir = './www/'):

    try:
        os.mkdir(output_dir,mode=0o755)
        os.mkdir(output_dir+'addresses',mode=0o755)
        os.mkdir(output_dir+'networks',mode=0o755)
        os.mkdir(output_dir+'entities',mode=0o755)
    except FileExistsError as e:
        sla.log(e)

def populateDirs(sla, wwwskel = './wwwskel'):
    
    sla.log("Copying default files.")
    try:
        if os.path.isdir('./www/'):
            shutil.copy(wwwskel+'/default.css','./www/')
            shutil.copy(wwwskel+'/default.js','./www/')
        else:
            sla.log("No directory to populate.")

    except FileNotFoundError as e:
        sla.log(e)


def navlinks():
    
    ret  = '[▲](../index.html) '
    ret += '[◀](./index.html) '
    return ret

def linkCSS(path = './'):

    
    return '<link rel="stylesheet" href="'+path+'default.css">\n'

def linkJS(path = './'):
    
    return '<script type="text/javascript" src="'+path+'default.js"></script>\n'

def generateAddressPages(sla, since='', output_dir = './www/'):

    HTML_START = '<html>\n<head>\n<meta charset="UTF-8">\n'+linkJS('../')+linkCSS('../')+'</head>\n<body>\n'
    HTML_END   = '\n</body>\n</html>\n'

    sla.initDB(sla.initDBFilename,sla.dbFilename)
    if (not since):
        ret = sla.dbCursor.execute("SELECT address, network_name, network_country, address_name FROM addresses_view")
    else:
        ret = sla.dbCursor.execute("SELECT DISTINCT addr, address_name FROM objects WHERE timestamp > strftime('%s','now','-"+since+"')")   
    addresses = ret.fetchall()

    sla.log("Generating "+str(len(addresses))+" address pages.")
    for address in addresses:
        query = r'SELECT * FROM packets WHERE src = ? OR dst = ? ORDER BY chain, action, timestamp DESC'
        ret = sla.dbCursor.execute(query, (address[0], address[0]))
        packets = ret.fetchall()
        try:
            md = '# '+navlinks()
            md += ' '.join(address[0:])+'\n'
        except TypeError:
            md = '# '+navlinks()+address[0:]+'\n'    
        md += '## Packets ('+str(len(packets))+')\n'
        for p in packets:
            md += ' - '
            for i in range(0,11):
                if i == 0:
                    md += time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p[i]))+' '
                elif (i == 6 or i == 7 or i == 1):
                    md += '['+p[i]+'](./'+urllib.parse.quote(p[i])+'.html) '    
                else:   
                    md += str(p[i])+' '
            md += '\n'
        html = HTML_START 
        html += markdown.markdown(md)
        html += HTML_END
        f = open(output_dir+'addresses/'+urllib.parse.quote(address[0])+'.html','w')
        f.write(html)
        f.close()      

def generateNetworkPages(sla, since= '', output_dir = './www/'):

    HTML_START = '<html>\n<head>\n<meta charset="UTF-8">\n'+linkJS('../')+linkCSS('../')+'</head>\n<body>\n'
    HTML_END   = '\n</body>\n</html>\n'

    sla.initDB(sla.initDBFilename,sla.dbFilename)
    if (not since):
        ret = sla.dbCursor.execute("SELECT * FROM networks")
    else:
        ret = sla.dbCursor.execute("SELECT DISTINCT network_handle FROM objects WHERE timestamp > strftime('%s','now','-"+since+"')")
    networks = ret.fetchall()

    sla.log("Generating "+str(len(networks))+" network pages.")
    for network in networks:
        handle = network[0]
        if not handle: continue
        query  = r'SELECT *,networks.handle FROM packets '
        query += r'INNER JOIN addresses ON addresses.address=packets.src '
        query += r'INNER JOIN networks ON networks.handle=addresses.network '
        query += r'WHERE networks.handle = ? '
        query += r'UNION SELECT *,networks.handle FROM packets '
        query += r'INNER JOIN addresses ON addresses.address=packets.dst '
        query += r'INNER JOIN networks ON networks.handle=addresses.network '
        query += r'WHERE networks.handle = ? '
        query += r'ORDER BY chain, action, timestamp DESC '
        ret = sla.dbCursor.execute(query, (handle, handle))
        packets = ret.fetchall()
        
        query = r'SELECT entities FROM networks WHERE handle = "'+handle+'"'
        ret = sla.dbCursor.execute(query)
        entities = ret.fetchone()
        
        md = '# '+navlinks()+' '.join(network[0:])+'\n'
        
        if (entities):
            md += '## Entities \n'
            for es in entities:
                for e in es.split(' '):
                    md += '['+e+'](../entities/'+e+'.html) '
            md += '\n'
        
        md += '## Packets ('+str(len(packets))+')\n'

        for p in packets:
            md += ' - '
            for i in range(0,11):
                if i == 0:
                    md += time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p[i]))+' '
                elif (i == 6 or i == 7 or i == 1):
                    md += '['+p[i]+'](../addresses/'+urllib.parse.quote(p[i])+'.html) '    
                else:   
                    md += str(p[i])+' '
            md += '\n'
        html = HTML_START
        html += markdown.markdown(md)
        html += HTML_END
        name = network[0].replace(' ','_')
        f = open(output_dir+'networks/'+name+'.html','w')
        f.write(html)
        f.close() 

def generateEntityPages(sla, output_dir = './www/'):

    HTML_START = '<html>\n<head>\n<meta charset="UTF-8">\n'+linkJS('../')+linkCSS('../')+'</head>\n<body>\n'
    HTML_END   = '\n</body>\n</html>\n'

    sla.initDB(sla.initDBFilename,sla.dbFilename)
    ret = sla.dbCursor.execute("SELECT handle,vcard FROM entities")
    entities = ret.fetchall()

    sla.log("Generating "+str(len(entities))+" entity pages.")
    for entity in entities:
        if (not entity[0]): continue
        md = '# '+navlinks()+entity[0]+'\n'
        info = ''
        if (entity[1]):
            try:
                #~ md += entity[1]+'\n'
                e = eval(entity[1])
                fn = e[1][1][3]
                kind = e[1][2][3]
                try:
                    addr1 = e[1][3][1]['label'].replace('\n','<br />')
                except KeyError:
                    try:
                        addr1 = e[1][4][1]['label'].replace('\n','<br />')
                    except KeyError: pass
                # May contain the address, but maybe something else.
                #~ try:    
                    #~ addr2 = ' '.join(e[1][3][3][0:]).strip() 
                #~ except TypeError: pass    
                addr2 = ''
                for i in e[1][5:]:
                    info += ' - '+str(i[0])+': '+str(i[3])+'\n'
                md += str(fn)+' ('+str(kind)+')<br /> \n'
                md += addr1+'<br />\n'+addr2+'<br />\n'
                md += '\n'+info+'\n'
            except IndexError: continue        
        md += '\n'
        html = HTML_START 
        html += markdown.markdown(md)
        html += HTML_END
        name = urllib.parse.quote(entity[0])
        f = open(output_dir+'entities/'+name+'.html','w')
        f.write(html)
        f.close()      

def generateIndexPage(sla, output_dir = './www/'):

    HTML_START = '<html>\n<head>\n<meta charset="UTF-8">\n'+linkJS('./')+linkCSS('./')+'</head>\n<body>\n'
    HTML_END   = '\n</body>\n</html>\n'

    sla.initDB(sla.initDBFilename,sla.dbFilename)
    sla.log("Generating index page.")
    md = ''
    sla.log("Counters...")
    ret = sla.dbCursor.execute("SELECT * FROM counters")
    counters = ret.fetchone()
    md += str(counters[0])+' packets — '
    md += str(counters[1])+' networks — '
    md += str(counters[2])+' addresses — '
    md += str(counters[3])+' entities '
    md += '\n'
    sla.log("Networks...")
    ret = sla.dbCursor.execute("SELECT * FROM networks")
    networks = ret.fetchall() 
    md += '## Networks ('+str(len(networks))+')\n'
    for network in networks:
        if (not network[0]): continue
        network_ = network[0].replace(' ','_')
        network_link='['+network[0]+'](./networks/'+network_+'.html) '
        md += ' - '+network_link+' '+' '.join(network[1:-1])
        md += '\n'
    sla.log("Addresses...")    
    ret = sla.dbCursor.execute("SELECT address, network_name, network_country FROM addresses_view")
    addresses = ret.fetchall()      
    md += '## Addresses ('+str(len(addresses))+')\n'
    for address in addresses:
        address_link='['+address[0]+'](./addresses/'+address[0]+'.html) '
        try:
            md += ' - '+address_link+' '+' '.join(address[1:])
        except TypeError:
            md += ' - '+address_link+' '+address[0]   
        md += '\n'
    html = HTML_START 
    html += markdown.markdown(md)
    html += HTML_END
    f = open(output_dir+'index.html','w')
    f.write(html)
    f.close()           
    return True
    
def generateContent(sla):

    generateDirs(sla)
    populateDirs(sla)
    #~ generateAddressPages(sla)
    #~ generateNetworkPages(sla)    
    generateAddressPages(sla,'60 minute')
    generateNetworkPages(sla,'60 minute')
    generateEntityPages(sla)

    generateIndexPage(sla)
    return True

