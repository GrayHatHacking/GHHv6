import shodan
import os

def shodan_search():
    
    SHODAN_API_KEY = "<YOUR API KEY>"
    # These are the common ports, but there will be false entries since 
    # we are not looking at banners or other indicators too.
    ICS_PORTS={ "modbus" : "502",
                "S7" : "102",
                "dnp3" : "20000",
                "Niagra Fox" : "1911,4911",
                "BACnet" : "47808",
                "ethernet/ip" : "448,18",
                "gesrtp" : "18245,18246",
                "hart-ip" : "5094",
                "pcworx" : "1962",
                "melsec-q" : "5006,5007",
                "Omron FINS" : "9600",
                "Crimson v3" : "789",
                "Codesys" : "2455",
                "iec 60870-5-104" : "2404",
                "ProConOs" : "20547"}

    ICS_SEARCH="port:{} ".format(','.join(str(x) for x in ICS_PORTS.values()))
    SEARCH = ICS_SEARCH + "country:US -ssh -http -html -ident"
    FACETS=[('port',10), ('product',10), ('city',10)]

    api = shodan.Shodan(SHODAN_API_KEY)
    print("Search String: {}".format(SEARCH))

    try:
        results = api.count(SEARCH,facets=FACETS)
        maxlen = 0

        # determine the length for padding 
        print("Results = {}".format(results['total']))

        for facet in results['facets']:
            tmplen = max(len(str(ele['value'])) for ele in results['facets'][facet])
            if (tmplen > maxlen):
                maxlen = tmplen

        for facet in results['facets']:
            print("Top {} {}".format(len(results['facets'][facet]),facet))
            for inst in results['facets'][facet]:
                print("{0} => {1}".format(str(inst['value']).ljust(maxlen),inst['count']))
            print('-'*40)
    except shodan.APIError as e:
        print("Error {}".format(e))

shodan_search()
