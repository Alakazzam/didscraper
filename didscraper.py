#!/usr/bin/python
# --                                                            
#
# File        : didscraper.py
# Maintainer  : Alakazam (alakazamjoined@gmail.com)
# Date        : 13/06/2018
#
# Version     : v0.1.0
#
# --           


import random
import json
import time
import urllib.request as urlq
import requests as req
from lxml.html import fromstring
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


outputfile_px = "didscraper-proxies.txt"
outputfile_ua = "didscraper-useragents.txt"
writing_mode = 'w' # Change to 'a' to save predecent proxies

timeout     = 2.5
sleep       = 0
proxies_nb  = 300
verbose = True

ip_tester = "https://httpbin.org/ip"
ua_tester = "https://httpbin.org/user-agent"
proxy_list_url = "https://free-proxy-list.net/"
ua_list_urls = [
                'https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/?order_by=-times_seen',
                'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/windows/?order_by=-times_seen'
                'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/mac-os-x/?order_by=-times_seen'
                ]

def retrieve_ua():
    j = json.loads(urlq.urlopen(ua_tester).read())

    return j['user-agent'].rstrip()

def retrieve_ip():
    j = json.loads(urlq.urlopen(ip_tester).read())

    return j['origin'].rstrip()

def retrieve_fake_ip(proxy):
    try:
        response = req.get(ip_tester, proxies={'http':proxy, 'https':proxy}, verify=False, timeout=timeout)
        j = json.loads(response.text)
        return j['origin'].rstrip()
    except:
        return False

def retrieve_fake_ua(fake_ua):
   headers = {'User-Agent': fake_ua}
   response = req.get(ua_tester, headers=headers, timeout=timeout)
   j = json.loads(response.text)

   return j['user-agent'].rstrip()

def get_proxies():
    proxies = []
    xpath_all   = '//tbody/tr'
    xpath_https = './/td[7][contains(text(), "yes")]'
    xpath_anon  = './/td[5][contains(text(), "elite proxy")]'
    xpath_coun  = './/td[4]/text()'
    xpath_ip    = './/td[1]/text()'
    xpath_port  = './/td[2]/text()'

    parser = fromstring(req.get(proxy_list_url).text)
    n = 0
    for xp in parser.xpath(xpath_all)[:proxies_nb]:
        if xp.xpath(xpath_https) and xp.xpath(xpath_anon):
            n += 1
            ip = xp.xpath(xpath_ip)[0]
            port = xp.xpath(xpath_port)[0]
            country = xp.xpath(xpath_coun)[0]

            outline = ':'.join([ip,port])
            proxies.append(outline)
            if verbose: print('{}.Elite Proxy : {} - {}\n-----'.format(n, outline, country))
            time.sleep(sleep)
    if verbose: print(len(proxies)," elite proxies found on {} tested.\n".format(proxies_nb))
    random.shuffle(proxies)

    return proxies

def get_user_agents():
    user_agents = []
    xpath_all = '//tbody/tr'
    xpath_ua  = './/a/text()'
    n=0

    for url in ua_list_urls:
        parser = fromstring(req.get(url).text)
        for elem in parser.xpath(xpath_all)[:hm_fakes]:
            ua = elem.xpath(xpath_ua)[0]
            user_agents.append(ua)
            print("{}. User-Agent: {}\n-----\n".format(n, ua))
            time.sleep(sleep)
            n+=1
    if verbose: print(n, ' user agents found.')

    return user_agents

def test_proxies(proxies):
    true = []
    print("----Original----")
    print("-IP: ", str(retrieve_ip()))
    print("-User-Agent: ",str(retrieve_ua()))
    t = 0
    print('-'*12)
    for proxy in proxies:
        ip = str(retrieve_fake_ip(proxy))
        if ip == 'False':
            if verbose: print('[X]',proxy)
        else:
            t+=1
            if verbose: print('[V]',proxy)
            true.append(proxy)
    if verbose: print(t, "/", len(proxies), ' working proxies')
    return true

def save(proxies, useragents):
    with open(outputfile_px, writing_mode) as f:
        for proxy in proxies:
            f.write(str(proxy)+'\n')
    with open(outputfile_ua, writing_mode) as f:
        for ua in useragents:
            f.write(str(ua)+'\n')


if __name__ == "__main__":
    print("[*] Retrieving Proxies...")
    proxies = get_proxies()
    hm_fakes = int(len(proxies)/len(ua_list_urls))
    print("[*] Retrieving User-Agents...")
    user_agents = get_user_agents()
    print("\n[*] Testing proxies")
    proxies = test_proxies(proxies)
    print("[*] Saving data to", outputfile_ua, "and", outputfile_px)
    save(proxies, user_agents)
