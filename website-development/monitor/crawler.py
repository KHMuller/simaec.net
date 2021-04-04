#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Sitemap - Crawler building a sitemap of a web site
    ============================================================
    Crawls a website starting with the homepage and follows each internal 
    links. Only follows a tags. Reads only ssl socket. Extracts length 
    of <article /> tag and compares with the value of a previous crawl.

    DON'T USE THIS SCRIPT FOR WEBSITES YOU DON'T OWN OR YOU DON'T HAVE 
    EXPLICIT PERMISSION TO CRAWL!
"""
import requests
from lxml import html
from lxml import etree
import pandas as pd
import sys
import os
from random import randint
from time import sleep
from datetime import datetime
import json 

def validate_website(website):
    # add list of websites allowed to be crawled
    if website in []: return True 
    return False

def remove_duplicates(a_list):
    return list(dict.fromkeys(a_list))

def valid_protocol(a_url):
    if a_url[:8] == 'https://': return True
    return False

def convert_url(url):
    return url.replace('https://', '').replace('/', '_')+'.html'

if sys.version_info[0] < 3:
    print('----------> Must be using Python 3')
    sys.exit()

def get_page(url, website, selector):
    '''
        returns the object result with the data from crawling a webpage.
    '''
    links = []

    result = {}
    result['url'] = url
    result['links'] = 0
    result['size'] = 0
    result['status_code'] = 0
    result['canonical'] = ''
    result['title'] =  ''
    result['sitename'] =  ''
    result['headline'] =  ''
    result['keywords'] =  ''
    result['description'] = ''
    result['introduction'] = ''
    result['content'] = ''

    try:
        page = requests.get(url)
        status_code = page.status_code
    except:
        result = {}
        result['url'] = url
        result['status_code'] = 900 
        result['status_message'] = 'Request failed'

        return result

    # Load Link Nodes
    size = len(page.content)

    try:
        tree = html.fromstring(page.content)
        size = len(etree.tostring(tree.xpath(selector)[0]))
        for elem in tree.iter():
            if elem.text == None:
                elem.text = ''
    except:
        result = {}
        result['url'] = url
        result['status_code'] = 900 
        result['status_message'] = 'Tree failed'
        return result

    # get first canonical tag href attribute value
    try:
        canonical = tree.xpath("//link[@rel = 'canonical']")[0].attrib['href']
    except:
        canonical = ''

    try:
        keywords = tree.xpath("//meta[@name = 'keywords']")[0].attrib['content']
    except:
        keywords = ''

    try:
        description = tree.xpath("//meta[@name = 'description']")[0].attrib['content']
    except:
        description = ''

    # get first title tag content    
    try:
        title = tree.xpath("//title")[0].text
    except:
        title = ''

    try:
        sitename = tree.xpath("//h1")[0].text
    except:
        sitename = ''

    try:
        headline = tree.xpath("//h2")[0].text
    except:
        headline = ''

    try:
        introduction = tree.xpath("//p")[0].text
    except:
        introduction = ''        

    link_nodes = tree.xpath('//a')

    for link_node in link_nodes:
        try:
            href = link_node.attrib['href']
        except:
            continue

        href = href.lower()
        href = href.split('?')[0] # drop query parameters
        href = href.split('#')[0] # drop anchors
        
        # validate link_node as link
        if len(href) == 0: continue
        if href[0:4] != 'http':
            
            # not an absolute link, build absolute link
            if href[0] == '/': 
                # starting with root folder "/" the website
                href = website[:-1] + href
            elif href.count('..') > 0 and url[-1] == '/':
                # Dealing with ../ or ../../, etc. links
                # e.g. Url is https://mywebsite.com/a/b/c/d/
                # href of link found is ../../
                href = '/'.join(url.split('/')[:-href.count('../')-1])+'/'
            else:
                # relative link
                # url should end with "/"
                if url[-1] == '/': 
                    href = url + href    
                else:
                    href = url + '/' + href
        links.append(href)

    result['url'] = url
    result['links'] = links
    result['size'] = size
    result['status_code'] = status_code
    result['status_message'] = 'Ok'
    result['canonical'] = canonical 
    result['title'] = title 
    result['sitename'] = sitename 
    result['headline'] = headline 
    result['keywords'] = keywords 
    result['description'] = description
    result['introduction'] = introduction
    result['content'] = page.content
    return result

def main(website, fetch):
    # Selector is used to identify tag in page enveloping the main content
    selector = '//article'
    report_name = website.replace('.', '')
    website = 'https://'+website+'/'

    if fetch:
        if not os.path.exists(report_name+'/fetch'): 
            os.makedirs(report_name+'/fetch')

    # Open past crawl results
    if not os.path.exists(report_name+'/sitemap.csv'):
        with open(report_name+'/sitemap.csv', 'w') as f:
            f.write('url,links,size,status,canonical,matches,title,keywords,description,sitename,headline,introduction,lastmod,lastcrawled,found')
    sitemap = pd.read_csv(report_name+'/sitemap.csv')
    sitemap = sitemap.fillna('')

    site = []
    for index, row in sitemap[sitemap['url'] != ''].iterrows():
        site.append({'url':row['url'], 'size':row['size'],'lastmod':row['lastmod'],'found':False})
    pages = [{'url':website, 'crawled':False},]
    external_links = {}
    internal_links = {}    
    for i in range(1, 11):
        print(('-'*100+' '+str(i))[-100:])
        current_pages = pages.copy()
        for current_page in current_pages:
            if not current_page['crawled']:
                sleep(randint(1,5)) #randomize crawl interval
                result = get_page(current_page['url'], website, selector)
                print (str(result['status_code']) + ': ' + result['url'])
                if fetch:
                    with open(report_name+'/fetch/'+convert_url(result['url']), 'wb') as f:
                        f.write(result['content'])
                # Update crawl index
                found_in_pages = False
                for index, page in enumerate(pages):
                    if page['url'] == result['url']:
                        found_in_pages = True
                        pages[index] = {'url':current_page['url'], 'crawled':True}
                if not found_in_pages:
                    pages.append({'url':current_page['url'], 'crawled':True})
                # Update sitemap
                found_in_sitemap = False
                for index, page in enumerate(site):
                    if page['url'] == result['url']:
                        found_in_sitemap = True
                        if result['size'] != int(page['size']):
                            update = {'url':current_page['url'],
                                'links':len(result['links']),
                                'size':result['size'],
                                'status':result['status_code'],
                                'canonical': result['canonical'],
                                'title': result['title'],
                                'keywords': result['keywords'],
                                'description': result['description'],
                                'sitename': result['sitename'],
                                'headline': result['headline'],
                                'introduction': result['introduction'],
                                'lastmod':datetime.today().strftime('%Y-%m-%d'),
                                'lastcrawled':datetime.today().strftime('%Y-%m-%d')}
                        else:
                            update = {'url':current_page['url'],
                                'links':len(result['links']),
                                'size':result['size'],
                                'status':result['status_code'],
                                'canonical': result['canonical'],
                                'title': result['title'],
                                'keywords': result['keywords'],
                                'description': result['description'],
                                'sitename': result['sitename'],
                                'headline': result['headline'],
                                'introduction': result['introduction'],
                                'lastmod':page['lastmod'],
                                'lastcrawled':datetime.today().strftime('%Y-%m-%d')}
                        site[index] = update
                if not found_in_sitemap:
                    site.append({'url':current_page['url'],
                                'links':len(result['links']),
                                'size':result['size'],
                                'status':result['status_code'],
                                'canonical': result['canonical'],
                                'title': result['title'],
                                'keywords': result['keywords'],
                                'description': result['description'],
                                'sitename': result['sitename'],
                                'headline': result['headline'],
                                'introduction': result['introduction'],
                                'lastmod':datetime.today().strftime('%Y-%m-%d'),
                                'lastcrawled':datetime.today().strftime('%Y-%m-%d')})
                for link in result['links']:
                    if website in link:
                        found = False
                        for index, page in enumerate(pages):
                            if link == page['url']:
                                found = True
                                continue
                        if not found:
                            new_page = {'url':link,'crawled':False}
                            pages.append(new_page)
                        if link in internal_links:
                            internal_links[link].append(current_page['url'])
                        else:
                            internal_links[link] = []
                            internal_links[link].append(current_page['url'])
                    else:
                        if link in external_links:
                            external_links[link].append(current_page['url'])
                        else:
                            external_links[link] = []
                            external_links[link].append(current_page['url'])

    sitemap = pd.DataFrame(site)
    sitemap = sitemap.set_index('url')
    sitemap.to_csv(report_name+'/sitemap.csv')

    # Save list of internal and external link data as json
    with open(report_name+'/internal-links.json', 'w') as f:
        json.dump(internal_links, f)

    with open(report_name+'/external-links.json', 'w') as f:
        json.dump(external_links, f)

    # We are done
    print('\033[92mCrawling has finished!\033[00m')

if __name__ == "__main__":
    # TODO > drop removal of query string
    website = input('Enter website to crawl: ')
    fetch = input('Do you want to fetch the pages? (Y/N): ')
    if fetch.lower() in ['y']:
        fetch = True
    else: 
        fetch = False

    if not validate_website(website):
        print('\033[91m{website} isn\'t a valid website!\033[00m'.format(website=website))
    else:
        print('\033[92mCrawling {website}!\033[00m'.format(website=website))
        main(website, fetch)
