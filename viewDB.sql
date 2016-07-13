CREATE VIEW IF NOT EXISTS packets_by_chain
(nb_packets, chain) AS SELECT 
SUM(1) AS nb_packets, `chain` FROM packets
GROUP BY `chain`
ORDER BY nb_packets DESC;

CREATE VIEW IF NOT EXISTS packets_by_action
(nb_packets, action) AS SELECT 
SUM(1) AS nb_packets, `action` FROM packets
GROUP BY `action`
ORDER BY nb_packets DESC;

CREATE VIEW IF NOT EXISTS packets_by_in_if
(nb_packets, if) AS SELECT 
SUM(1) AS nb_packets, `if_in` FROM packets
WHERE if_in NOT LIKE ''
GROUP BY `if_in`
ORDER BY nb_packets DESC;

CREATE VIEW IF NOT EXISTS packets_by_out_if
(nb_packets, if) AS SELECT 
SUM(1) AS nb_packets, `if_out` FROM packets
WHERE if_out NOT LIKE ''
GROUP BY `if_out`
ORDER BY nb_packets DESC;

CREATE VIEW IF NOT EXISTS addresses_view
(address, network_name, network_country, address_name, network_entities, network_handle) AS SELECT
address, name, country, hostname, entities, handle FROM addresses
LEFT JOIN networks ON addresses.network=networks.handle;

CREATE VIEW IF NOT EXISTS counters
(packets,networks,addresses,entities) AS SELECT
(
SELECT COUNT(*) FROM packets) AS packets, (
SELECT COUNT(*) FROM networks) AS networks, (
SELECT COUNT(*) FROM addresses) AS addresses, (
SELECT COUNT(*) FROM entities) AS entities
;

CREATE VIEW IF NOT EXISTS objects
(addr,network_name,network_country, network_entities, network_handle, address_name, timestamp) AS
SELECT
src AS addr,network_name,network_country, network_entities, network_handle, src, timestamp FROM packets INNER JOIN addresses_view ON src=address
UNION SELECT
dst AS addr,network_name,network_country, network_entities, network_handle, dst, timestamp FROM packets INNER JOIN addresses_view ON dst=address
;





