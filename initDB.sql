CREATE TABLE IF NOT EXISTS packets (
timestamp DATETIME NOT NULL,
host TEXT,
chain TEXT NOT NULL,
action TEXT NOT NULL,
if_in TEXT,
if_out TEXT,
src TEXT,
dst TEXT,
proto TEXT,
spt INT,
dpt INT,
mac TEXT,
PRIMARY KEY(timestamp, host));

CREATE TABLE IF NOT EXISTS networks (
handle TEXT,
name TEXT,
country TEXT,
type TEXT,
start_addr TEXT,
end_addr TEXT,
parent_handle TEXT,
entities TEXT,
source TEXT,
PRIMARY KEY (handle));

CREATE TABLE IF NOT EXISTS addresses (
address TEXT NOT NULL,
hostname TEXT,
network TEXT,
PRIMARY KEY (address),
FOREIGN KEY(network) REFERENCES networs(handle));



