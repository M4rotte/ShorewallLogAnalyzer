#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""ShorewallLogAnalyzer.py: Analyze Shorewall logs."""

try:

    import sys
    import re
    import sqlite3
    import inspect
    import datetime
    import socket
    import urllib

    from RDAP import getNetwork, getEntity
    from Utils import is_valid_timestamp
    from Web import generateContent

except ImportError as e:
    print("Missing module : "+str(e),file=sys.stderr)
    sys.exit(1)


    import sys
    import re
    import sqlite3
    import inspect
    import datetime
    import socket
    import urllib

    from RDAP import getNetwork, getEntity
    from Utils import is_valid_timestamp
    from Web import generateContent

except ImportError as e:
    print("Missing module : "+str(e),file=sys.stderr)
    sys.exit(1)

class ShorewallLogAnalyzer:
    """ Read log file, interprets data and write to database. """

    # Select and split each line to get timestamp and data
    logSplitter    = re.compile(r'(.*) Shorewall:')
    packets        = []

    def log(self,message = ''):
        """ Logging function. """
        if (message != ''): sep = ':'
        else: sep = ''
        try:
            print(str(datetime.datetime.now())+" "+inspect.currentframe().f_back.f_code.co_name+sep+" "+message,file=sys.stderr)
        except (TypeError, urllib.error.URLError):
            pass

    
    def __init__(self, dbFilename = './shorewall.sqlite', initDBFilename = 'initDB.sql'):

    
        self.initDB(initDBFilename, dbFilename)
        self.dbFilename = dbFilename
        self.initDBFilename = initDBFilename

    def tryCommit(self):
        
        try: 
            self.dbConnection.commit()
            return True

        except sqlite3.ProgrammingError as e:
            self.log(e)
            self.dbConnection.rollback()
            self.dbConnection.close()
            return False

    def tryCommit(self):
        
        try: self.dbConnection.commit()

        except sqlite3.ProgrammingError as e:
            self.log(e)
            self.dbConnection.rollback()
            self.dbConnection.close()
            return False
    
    
    def initDB(self, initDBFilename, dbFilename):
        """ Create the database if not exists. """
        try:
            self.dbConnection = sqlite3.connect(dbFilename)
            self.dbCursor     = self.dbConnection.cursor()

        except FileNotFoundError as e:
            self.log(str(e)+". Exiting.")
            return False            
        try:
            initDBFile      = open(initDBFilename,'r')
            self.log(initDBFile)
        except Error as e:
            self.log(e)
            return False                 

        query = initDBFile.read()    
        self.dbCursor.executescript(query)
        initDBFile.close()
        self.log("Configuration OK.")
        return self.tryCommit()

    def getPackets(self, logFilename = '/var/log/kern.log'):
        """ Reads each line of the file with the function below (`readLine`). """
        self.log("Getting packets from "+logFilename)

        try:
            logFile = open(logFilename,'r')
        except FileNotFoundError as e:
            self.log(str(e))
            return []
        try:
            for line in logFile.readlines():
                packet = self.readLine(line)
                if (packet):
                    self.packets.append(packet)
                    
        except AttributeError:
            self.log("Nothing to read !")
        
        self.log(str(len(self.packets))+" packets.")
        return(self.packets)
  
    
    def readLine(self, line):
        """ Read a line of log and return a dictionary with its last element `ip` also being a dictionary. """
        
        if (self.logSplitter.match(line)):

                split = self.logSplitter.split(line)
                left_part = split[1].split(' ')
                timestamp = left_part[0]
                if (not is_valid_timestamp(timestamp)):
                    self.log("Invalid timestamp: "+timestamp)
                    return False
                host      = left_part[1]
                data      = split[2]
                data_split = data.split(':',2)
                chain = data_split[0]
                action = data_split[1]
                ip_data = ' '.join(data_split[2:])
                ip_data_split = ip_data.split(' ')
                ip = {}
                for ipd in ip_data_split:
                    ipd_split = ipd.split('=')
                    left = ipd_split[0]
                    if (left != '\n'):
                        try:
                            right = ipd_split[1]
                        except IndexError:
                            right = ''
                        ip[left] = right

                return {'timestamp': timestamp, 'host': host, 'chain': chain, 'action': action, 'ip': ip}
        else:
            
            return False
    
  
    def updatePackets(self):
        """ Write "packets" to the database. """
        
        for p in self.packets:
            """ Insert packet or ignore silently (`timestamp` is the primary key). 
                Not all of the values of the packet `ip` dict are being used.
                You can add some there, but you need to modify initDB.sql too """

            try:    
                self.dbCursor.execute('INSERT OR IGNORE INTO packets (timestamp, host, chain, action, if_in, if_out, src, dst, proto, spt, dpt, mac) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',\
                                     (p['timestamp'],\
                                      p['host'],\
                                      p['chain'],\
                                      p['action'],\
                                      p['ip']['IN'],\
                                      p['ip']['OUT'],\
                                      p['ip']['SRC'],\
                                      p['ip']['DST'],\
                                      p['ip']['PROTO'],\
                                      p['ip']['SPT'],\
                                      p['ip']['DPT'],\
                                      p['ip'].get('MAC',''))) # May be absent.
            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                self.log(str(e)+". Exiting.")
                self.dbConnection.close()
                return False
            except KeyError:
                continue

        self.log(str(max(0,self.dbCursor.rowcount))+" database rows modified.")

        return self.tryCommit()


    def updateAddresses(self):
        """ Select all uniq addresses from the `packets` table and insert them in the `addresses` table. """
        
        query = "SELECT DISTINCT addr FROM (SELECT dst AS addr FROM packets UNION SELECT src AS addr FROM packets AS addr)"
        result = self.dbCursor.execute(query)
        addresses = result.fetchall()
        self.log(str(len(addresses))+" addresses.")
        try:
            self.dbCursor.executemany("INSERT OR IGNORE INTO addresses (address) VALUES (?)",addresses)
        except sqlite3.OperationalError:
            self.log("Database locked. Exiting.")
            self.dbConnection.close()
        self.log(str(max(0,self.dbCursor.rowcount))+" database rows modified.")    
        return self.tryCommit()

    def updateHostnames(self, resolve_all=False):

        if not resolve_all: query = "SELECT address FROM addresses WHERE hostname IS NULL"   
        else: query = "SELECT address FROM addresses"
        result = self.dbCursor.execute(query)
        addresses = result.fetchall()
        self.initDB(self.initDBFilename, self.dbFilename)
        self.log(str(len(addresses))+" addresses to resolve.")
        for address in addresses:
            self.log(address[0])

            try:
                hostname = socket.gethostbyaddr(address[0])
                self.dbCursor.execute("UPDATE addresses SET hostname = ? WHERE address = ?",(hostname[0],hostname[2][0]))
                self.log(hostname[2][0]+" resolved as "+hostname[0])

            except socket.herror as e:
                self.log(address[0]+" "+str(e))
                self.dbCursor.execute("UPDATE addresses SET hostname = ? WHERE address = ?",('NXDOMAIN',address[0]))
                continue
            except sqlite3.OperationalError:
                self.log("Database locked. Exiting.")
                self.dbConnection.close()

        self.tryCommit()        
        return True


    def updateNetworks(self, refresh_all=False):
        
        if not refresh_all: query = "SELECT address FROM addresses WHERE addresses.network IS NULL OR addresses.network = ''"
        else: query = "SELECT address FROM addresses"
        result = self.dbCursor.execute(query)
        addresses = result.fetchall()
        self.initDB(self.initDBFilename, self.dbFilename)
        self.log(str(len(addresses))+" RDAP queries.")
        for address in addresses:
            try:
                info = getNetwork(address[0])
                query = "INSERT OR IGNORE INTO networks (handle,name,country,type,start_addr,end_addr,parent_handle,entities,source) VALUES (?,?,?,?,?,?,?,?,?)"
                self.dbCursor.execute(query,info)
                query = "UPDATE addresses SET network = ?  WHERE address = ?"
                self.dbCursor.execute(query,(info[0],address[0]))
            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                self.log(e)
                continue
        self.tryCommit()        
        return True

    def updateEntities(self, refresh_all=False):
        
        query = "SELECT entities, source FROM networks"
        result = self.dbCursor.execute(query)
        entities = result.fetchall()
        self.initDB(self.initDBFilename, self.dbFilename)
        for entities_ in entities:
            for entity in entities_[0].split(' '):
                try:
                    query = "INSERT OR IGNORE INTO entities (handle,source) VALUES (?,?)"
                    self.dbCursor.execute(query,(entity,entities_[1]))
                except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                    self.log(e)
                    continue
        self.tryCommit()

        
        if not refresh_all: query = "SELECT * FROM entities WHERE entities.vcard IS NULL"
        else: query = "SELECT * FROM entities"
        result = self.dbCursor.execute(query)
        entities = result.fetchall()
        self.log(str(len(entities))+" RDAP queries.")
        for entity in entities:
            try:
                if(entity[0]): info = getEntity(entity[0],entity[3])
                else: continue
                query = "UPDATE entities SET vcard = ?, entities = ?  WHERE handle = ?"
                self.dbCursor.execute(query,(str(info[1]),info[2],entity[0]))
            except (sqlite3.OperationalError, sqlite3.ProgrammingError) as e:
                self.log(e)
                continue
        self.tryCommit()             
        return True

    def declareViews(self,  dbFilename, viewDBFilename = 'viewDB.sql',):
        """ Create the database if not exists. """
        self.log(viewDBFilename)
        try:
            self.dbConnection = sqlite3.connect(dbFilename)
            self.dbCursor     = self.dbConnection.cursor()
        except FileNotFoundError as e:
            self.log(str(e)+". Exiting.")
            return False            
        try:
            viewDBFile      = open(viewDBFilename,'r')
            self.log(viewDBFile)
        except Error as e:
            self.log(e)
            return False                 
        query = viewDBFile.read()    
        self.dbCursor.executescript(query)
        viewDBFile.close()
        self.log("Views OK.")
        return self.tryCommit()

    def generateContent(self):

        generateContent(self)
        return True    


if (__name__ == "__main__"):

    analyzer = ShorewallLogAnalyzer('./shorewall.sqlite')
    analyzer.getPackets('/tmp/log')
    analyzer.updatePackets()
    analyzer.updateAddresses()
    analyzer.updateHostnames()
    analyzer.updateNetworks()
    analyzer.updateEntities()
    analyzer.declareViews('./shorewall.sqlite')
    analyzer.generateContent()
