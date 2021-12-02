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

if sys.version_info[0] < 3:
    print('----------> Must be using Python 3')
    sys.exit()

def validate_website(website):
    # add list of websites allowed to be crawled
    if website in []: return True
    return False

def remove_duplicates(a_list):
    return list(dict.fromkeys(a_list))

def convert_url(url):
    return url.replace('https://', '').replace('/', '_')+'.html'

def ignore_link(url):
    if 'tel:' in url: return True
    if 'javascript:' in url: return True
    if 'mailto:' in url: return True
    return False

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
    result['status_message'] = ''
    result['htmldoc'] = False
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
        result['url'] = url
        result['status_code'] = 900
        result['status_message'] = 'Request failed'
        result['htmldoc'] = False
        return result

    # Load Link Nodes
    size = len(page.content)

    try:
        tree = html.fromstring(page.content)
        if selector != '':
            size = len(etree.tostring(tree.xpath(selector)[0]))
        for elem in tree.iter():
            if elem.text == None:
                elem.text = ''
    except:
        result['url'] = url
        result['status_code'] = 900
        result['status_message'] = 'Tree failed'
        return result

    # get first canonical tag href attribute value
    try:
        if len(tree.xpath("//html")[0].text) > 0:
            htmldoc = True
        else:
            htmldoc = False
    except:
        htmldoc = False

    if not htmldoc:
        result['url'] = url
        result['status_code'] = 900
        result['status_message'] = 'No HTML'
        return result
    else:
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
            href = href.strip()
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
        result['htmldoc'] = True
        result['canonical'] = canonical
        result['title'] = title
        result['sitename'] = sitename
        result['headline'] = headline
        result['keywords'] = keywords
        result['description'] = description
        result['introduction'] = introduction
        result['content'] = page.content
        return result

def crawl_page(page, website, fetch):
    selector = ''
    website = 'https://'+website+'/'
    result = get_page(page, website, selector)
    for key in result:
        if key != 'content':
            print(100*'-')
            print(key)
            if key == 'links':
                for item in result[key]:
                    print(item)
            else:
                print(result[key])


def main(website, fetch):
    # Selector is used to identify tag in page enveloping the main content
    selector = ''
    report_folder = website.replace('.', '')
    website = 'https://'+website+'/'


    if not os.path.exists(report_folder):
        os.makedirs(report_folder)

    if fetch:
        if not os.path.exists(report_folder+'/fetch'):
            os.makedirs(report_folder+'/fetch')

    if not os.path.exists(report_folder+'/sitemap.csv'):
        with open(report_folder+'/sitemap.csv', 'w') as f:
            f.write('url,size,status_code,status_message,htmldoc,canonical,title,keywords,description,sitename,headline,introduction,lastmod,foundby,crawled,external\n')
            f.write(website+',0,,,False,,,,,,,,,,False,False\n\n')

    sitemap = pd.read_csv(report_folder+'/sitemap.csv')
    sitemap = sitemap.fillna('')
    sitemap['crawled'] = False
    sitemap['external'] = sitemap['url'].apply(lambda x: False if website in x else True)
    sitemap.drop_duplicates(subset ='url', keep='first', inplace=True)

    linkedby = {}

    while True:
        print('-'*100)
        sitemap = sitemap.fillna('')
        pages = sitemap[(sitemap['crawled'] == False) & (sitemap['external'] == False)]['url'].tolist()
        if len(pages) == 0: break
        for page in pages:

            # ignore external links
            if website not in page:
                sitemap.loc[sitemap['url'] == page, 'external'] = True
                continue

            sleep(randint(1,5)) #randomize crawl interval
            result = get_page(page, website, selector)
            sitemap.loc[sitemap['url'] == page, 'crawled'] = True

            print (str(result['status_code']) + ': ' + result['url'])

            if fetch:
                with open(report_folder+'/fetch/'+convert_url(result['url']), 'wb') as f:
                    f.write(result['content'])

            try: 
                size_prev = list(sitemap[sitemap['url'] == page]['size'])[0]
            except:
                size_prev = 0

            
            sitemap.loc[sitemap['url'] == page, 'size'] = result['size']
            sitemap.loc[sitemap['url'] == page, 'status_code'] = result['status_code']
            sitemap.loc[sitemap['url'] == page, 'status_message'] = result['status_message']
            sitemap.loc[sitemap['url'] == page, 'htmldoc'] = result['htmldoc']

            if result['status_code'] == 200 and result['htmldoc']:
                sitemap.loc[sitemap['url'] == page, 'canonical'] = result['canonical']
                sitemap.loc[sitemap['url'] == page, 'title'] = result['title']
                sitemap.loc[sitemap['url'] == page, 'keywords'] = result['keywords']
                sitemap.loc[sitemap['url'] == page, 'description'] = result['description']
                sitemap.loc[sitemap['url'] == page, 'sitename'] = result['sitename']
                sitemap.loc[sitemap['url'] == page, 'headline'] = result['headline']
                sitemap.loc[sitemap['url'] == page, 'introduction'] = result['introduction']
                if size_prev != result['size']:
                    sitemap.loc[sitemap['url'] == page, 'lastmod'] = datetime.today().strftime('%Y-%m-%d')
                if len(result['links']) > 0:
                    for link in result['links']:
                        if len(sitemap[sitemap['url'] == link]) == 0:
                            new_page = {'url': link, 'size': 0, 'crawled': False, 'external': False}
                            sitemap = sitemap.append(new_page, ignore_index = True)
                        if link in linkedby:
                            linkedby[link].append(page)
                        else:
                            linkedby[link] = [page]

    sitemap = sitemap.set_index('url')
    sitemap.to_csv(report_folder+'/sitemap.csv')

    with open(report_folder+"/linkedby.txt", "w") as text_file:
        text_file.write('Links Found\n')
        text_file.write('Date: ' + datetime.today().strftime('%Y-%m-%d'))
        for link in linkedby:
            text_file.write('-'*80+'\n')
            text_file.write(link+'\n')
            text_file.write('Linked by: \n')
            locations = remove_duplicates(linkedby[link])
            for loc in locations:
                text_file.write('\t'+str(loc)+'\n')



if __name__ == "__main__":
    # TODO > add header to qualify in logs for third party websites
    # TODO > provide option to read only pages in a sitemap
    # print("The script has the name %s" % (sys.argv[0]))

    website = input('Enter website to crawl: ')
    if not validate_website(website):
        print('\033[91m{website} isn\'t a valid website!\033[00m'.format(website=website))
        sys.exit()

    single_page = input('Enter Single Page: ')
    if single_page != '':
        print('\033[92mCrawling {webpage}!\033[00m'.format(webpage=single_page))
        crawl_page(single_page, website, False)
        print('\033[92mCrawling has finished!\033[00m')
        sys.exit()

    fetch = input('Do you want to fetch the pages? (Y/N): ')
    if fetch.lower() in ['y']:
        fetch = True
    else:
        fetch = False

    print('\033[92mCrawling {website}!\033[00m'.format(website=website))
    main(website, fetch)
    print('\033[92mCrawling has finished!\033[00m')
