CREATE TABLE IF NOT EXISTS packets (
timestamp TEXT NOT NULL,
chain TEXT NOT NULL,
action TEXT NOT NULL,
if_in TEXT,
if_out TEXT,
src TEXT,
dst TEXT,
proto TEXT,
spt INT,
dpt INT,
PRIMARY KEY(timestamp));

CREATE TABLE IF NOT EXISTS networks (
handle TEXT,
name TEXT,
country TEXT,
type TEXT,
start_addr TEXT,
end_addr TEXT,
parent_handle TEXT,
entities TEXT,
PRIMARY KEY (handle));

CREATE TABLE IF NOT EXISTS addresses (
address TEXT NOT NULL,
hostname TEXT,
PRIMARY KEY (address));

CREATE TABLE IF NOT EXISTS addr_net (
address TEXT,
network TEXT,
FOREIGN KEY (network) REFERENCES networks(handle));

