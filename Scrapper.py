#!/usr/bin/env python
# coding: utf-8

# In[20]:


import requests
from selenium import webdriver
from lxml import html
import time
import pandas as pd


# In[21]:


def fetch_netmeds_results(letter):
    url = f'https://www.netmeds.com/catalogsearch/result/{letter}/all'
    driver = webdriver.Chrome()
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 30000);")
    time.sleep(280)
    rendered_html = driver.page_source
    return rendered_html

def clean(li, flag=False):
    li = li[0] if len(li) > 0 else None
    return li[1:] if flag and li is not None else li

def netmeds_scrapper(result_string):
    result = html.fromstring(result_string)
    li = []
    for element in result.xpath('//div[@class="cat-item "]'):
        name = element.xpath('.//a/span[@class="clsgetname"]/text()')
        mrp = element.xpath('.//span[@class="price-box"]/p[@id="price"]/strike/text()')
        if len(mrp) == 0:
            mrp = element.xpath('.//span[@class="price-box"]/span[@id="final_price"]/text()')
        discounted = element.xpath('.//span[@class="price-box"]/span[@class="final-price"]/text()')
        if len(discounted) == 0:
            discounted = element.xpath('.//div[@class="newbestprice"]/div[@class="BStext"]/span[@id="barBestPrice"]/text()')
        mrktkr = element.xpath('.//a/span[@class="drug-varients ellipsis"]/text()')
        li.append([clean(name), 
                   clean(mrp, True), 
                   clean(discounted, True), 
                   clean(mrktkr)])
    df = pd.DataFrame(li, columns=['Name', 'MRP', 'Discounted Price', 'Manufacturer'])
    return df

b_df = netmeds_scrapper(fetch_netmeds_results('b'))
f_df = netmeds_scrapper(fetch_netmeds_results('f'))


# In[22]:


print(b_df)


# In[23]:


def fetch_pharmeasy_results(letter):
    url = f"https://pharmeasy.in/search/all?name=%20{letter}"
    driver = webdriver.Chrome()
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 30000);")
    time.sleep(60)
    rendered_html = driver.page_source
    return rendered_html

def clean(li):
    return li[0] if len(li) > 0 else None

def pharmeasy_scrapper(result_string, letter):
    result = html.fromstring(result_string)
    li = []
    for element in result.xpath('//div[@class="ProductCard_medicineUnitContainer__cBkHl"]'):
        name = element.findall('.//h1[@class="ProductCard_medicineName__8Ydfq"]')
        name = [i.xpath('.//text()')[0] for i in name]
        if name[0][0] != letter:
            continue
        mrp = element.findall('.//span[@class="ProductCard_striked__jkSiD"]')
        mrp = [''.join(i.xpath('.//text()'))[1:] for i in mrp]
        discounted = element.findall('.//div[@class="ProductCard_gcdDiscountContainer__CCi51"]/span[1]')
        discounted = [''.join(i.xpath('.//text()'))[1:] for i in discounted]
        mrktkr = element.findall('.//div[@class="ProductCard_brandName__kmcog"]')
        mrktkr = [i.xpath('.//text()[2]') if len(i.xpath('.//text()[2]')) > 0 else '' for i in mrktkr]
        li.append([clean(name), 
                   clean(mrp), 
                   clean(discounted), 
                   clean(mrktkr)])
    df = pd.DataFrame(li, columns=['Name', 'MRP', 'Discounted Price', 'Manufacturer'])
    return df


# In[24]:


b_df = pd.concat([b_df, pharmeasy_scrapper(fetch_pharmeasy_results('b'), 'B')], ignore_index = True)
b_df = b_df.iloc[-1000:, :]
f_df = pd.concat([f_df, pharmeasy_scrapper(fetch_pharmeasy_results('f'), 'F')], ignore_index = True)
f_df = f_df.iloc[-1000:, :]


# In[25]:


df = pd.concat([b_df, f_df], ignore_index=True)


# In[27]:


df.to_csv('level1_scrapper.csv')

