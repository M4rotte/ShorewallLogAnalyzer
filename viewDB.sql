CREATE VIEW IF NOT EXISTS packets_by_chain
(nb_packets, chain) AS SELECT 
SUM(1) AS nb_packets, `chain` FROM packets
GROUP BY `chain`
ORDER BY nb_packets DESC
;

CREATE VIEW IF NOT EXISTS packets_by_action
(nb_packets, action) AS SELECT 
SUM(1) AS nb_packets, `action` FROM packets
GROUP BY `action`
ORDER BY nb_packets DESC
;

CREATE VIEW IF NOT EXISTS packets_by_in_if
(nb_packets, if) AS SELECT 
SUM(1) AS nb_packets, `if_in` FROM packets
WHERE if_in NOT LIKE ''
GROUP BY `if_in`
ORDER BY nb_packets DESC
;

CREATE VIEW IF NOT EXISTS packets_by_out_if
(nb_packets, if) AS SELECT 
SUM(1) AS nb_packets, `if_out` FROM packets
WHERE if_out NOT LIKE ''
GROUP BY `if_out`
ORDER BY nb_packets DESC
;

CREATE VIEW IF NOT EXISTS addresses_view
(address, network_name, network_country) AS SELECT
address, name, country FROM addresses
INNER JOIN networks ON addresses.network=networks.handle
;



