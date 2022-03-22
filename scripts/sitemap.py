#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Crawls local drive to build a sitemap of a web site
    ============================================================
    Crawls all files and folders within the folder ../public/.
    Only index.html are considered pages of the website.
    Creates a sitemap (XML format) with the pages found within the folder ../public/. 
    Creates a csv file of all pages found.
"""
import pandas as pd
import os
import datetime
import xml.etree.ElementTree as ET

urlset = ET.Element('urlset')
urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

data = pd.DataFrame(columns = ['loc', 'lastmod'])

domain = 'https://www.simaec.net'
localpath = '../public/'

for root, dirs, files in os.walk(localpath):
    for filename in files:
        if 'index.html' in filename:
            file_stats = os.stat(root + '/' + filename)
            loc_text = domain + (root.replace(localpath, '/') + '/').replace('//','')
            lastmod_text = datetime.datetime.utcfromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d')
            url = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url, 'loc')
            loc.text = loc_text
            lastmod = ET.SubElement(url, 'lastmod')
            lastmod.text = lastmod_text
            row = pd.Series([loc_text, lastmod_text], index = ['loc', 'lastmod'])
            data = data.append(row, ignore_index=True)

current = ''
if os.path.isfile(localpath+'sitemap.xml'):
    with open(localpath+'sitemap.xml', 'r') as f: 
        current = f.read()

if ET.tostring(urlset).decode("utf-8") != current:
    with open(localpath+'sitemap.xml', 'w') as f:
        f.write(ET.tostring(urlset).decode("utf-8"))

data.to_csv('sitemap.csv', index=False)
print(str(len(data)), ' urls found')
