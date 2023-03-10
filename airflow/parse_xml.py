import xml.etree.ElementTree as ET
import requests, pickle


def parse_xml_currency():
    url = "https://www.nationalbank.kz/rss/get_rates.cfm?fdate=26.10.2021"
    res = requests.request(method="get", url=url)
    xml_string = res.content

    parse = ET.fromstring(xml_string)
    data = {}
    for cur in parse.iter('item'):
        title = cur.find("title").text
        currency = cur.find("description").text
        data[title] = currency
    return pickle.dumps(data)
