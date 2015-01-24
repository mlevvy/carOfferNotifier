import requests
import bs4
import pymongo
import sys

is250_collection = pymongo.MongoClient().lexus.is250
API_KEY = sys.argv[1]
APU_URL = sys.argv[2]
EMAIL_FROM = sys.argv[3]
EMAIL_TO = sys.argv[4]


def fetch_page():
    index_url = 'http://otomoto.pl/osobowe/lexus/is/ii///benzyna?s=dd&fq%5Bpower_hp%5D%5Bfrom%5D=200&fq%5Bpower_hp%5D%5Bto%5D=210&fq%5Boutside_features%5D%5B0%5D=item.has_sunroof&fq%5Bgear_type%5D%5B0%5D=automatic'
    response = requests.get(index_url)
    return bs4.BeautifulSoup(response.text)


def format_link(part_link):
    if "allegro" in part_link:
        return part_link
    else:
        return "http://otomoto.pl" + part_link


def car_offers():
    articles = {}
    list_of_cars = fetch_page().find_all(name="article", attrs={'class': 'om-list-item'})
    for x in list_of_cars:
        offer_name = x.find(name='a').text.strip()
        offer_id = x.find(name='a').attrs.get('href')
        articles[format_link(offer_id)] = offer_name
    return articles


def send_mail(offer_link, offer_name):
    print("New car with name '{}' and with link '{}'".format(offer_name, offer_link))
    request_url = 'https://api.mailgun.net/v2/{}/messages'.format(APU_URL)
    print(request_url)
    request = requests.post(request_url, auth=('api', API_KEY), data={
        'from': EMAIL_FROM,
        'to': EMAIL_TO,
        'subject': "[New car offer] {}".format(offer_name),
        'text': 'Sir, your link: {}'.format(offer_link)
    })
    print("Sending new mail finished with status: '{}'".format(request.status_code))
    print("Sending new mail finished with message: '{}'".format(request.text))


offers = car_offers()
for car in offers:
    result = is250_collection.find_one({"offer_id": car})
    if result is None:
        is250_collection.insert({"offer_id": car})
        send_mail(car, offers[car])
    else:
        print("Skipping offer '{}' with link '{}'".format(offers[car], car))
