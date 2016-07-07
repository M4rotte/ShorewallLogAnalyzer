# ShorewallLogAnalyzer
Gather Shorewall logs to store them in a database. Calculate some stastistics from this data and some whois (or RDAP) requests to produce static HTML pages. **It's a work in progress, is not fully functionnal and may broke frequently**

## Usage

ShorewallLogAnalyzer expects the timestamp of the log to be a Unix timestamp with millisecond (ex: 1467902169.34722), this for two reasons :

 - include the year so it's possible to get some statistics covering more than one year
 - include milliseconds so two packets logged at the same second will have different timestamp
 
Malformed lines will be ignored (with a message on standard error). If using systemd one can generate such a log with a command like :

    journalctl -o short-unix
    

