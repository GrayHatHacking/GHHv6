# The commands from the lab are below
# Replace the API Key with your key

shodan init <YOUR API KEY>
shodan info
shodan search --fields ip_str,port,org,hostnames RFB > results.txt
wc -l results.txt
head -3 results.txt
shodan honeyscore 54.187.148.155
shodan honeyscore 52.24.188.77
shodan stats --facets city:3,product:3 "port:502,102,20000,1911,4911,47808,448,18,18245,18246,5094,1962,5006,5007,9600,789,2455,2404,20547 country:US -ssh -http -html -ident"
