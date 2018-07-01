import googlemaps
import pprint

gm = googlemaps.Client(key='AIzaSyCSqh5raE0IS7b5N3yKiNkxKLJ2xVxNxDo')
google_result = gm.geocode('Tokyo-to, Bunkyou-ku, Hongo 3-9-9, Townheights Hongo')
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(google_result[0]['geometry']['location']['lat'])
pp.pprint(google_result[0]['geometry']['location']['lng'])
