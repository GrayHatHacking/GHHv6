import shodan

def shodan_search():
      SHODAN_API_KEY = "<YOUR API KEY>"
      SEARCH = "mqtt alarm country:us"
      api = shodan.Shodan(SHODAN_API_KEY)

      try:
            results = api.search(SEARCH)
            with open("mqtt-results.txt", "w") as f:
                for result in results['matches']:
                      searching = result['ip_str']
                      f.write(searching + '\n')
      except shodan.APIError as e:
            pass

shodan_search()
