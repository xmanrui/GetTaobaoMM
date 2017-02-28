# -*- coding: utf-8 -*-

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib
import os
import re
import math
import tool

def get_one_page_album_links(webdriverObj):
    aElements = webdriverObj.find_elements_by_xpath('//div[@class="mm-photo-list clearfix"]/div/div/h4/a')
    albumLinks = []
    for x in aElements:
        link = x.get_attribute('href')
        albumLinks.append(link)

    r = get_one_page_album_links_and_imgs_count(webdriverObj)
    print 'links and count:', r
    input('testsfd')

    return albumLinks

def get_one_page_album_links_and_imgs_count(webdriverObj):
    '''
    :param webdriverObj:
    :return: 返回相册连接以及相册的照片数量
    '''

    aElements = webdriverObj.find_elements_by_xpath('//div[@class="mm-photo-list clearfix"]/div/div/h4/a')
    albumLinks = []
    for x in aElements:
        link = x.get_attribute('href')
        albumLinks.append(link)

    count_list = re.findall(ur'span class="mm-pic-number">\((\d+)张\)</span>', webdriverObj.page_source)

    result = list()
    if len(albumLinks) == len(count_list):
        for i, j in enumerate(albumLinks):
            d = dict()
            d['link'] = j
            d['count'] = tool.str_to_int(count_list[i])
            result.append(d)

    return result

def get_model_album_links(webdriverObj, album_home_link):
    '''
    从相册主页中获取各相册的链接
    :param webdriverObj:
    :param album_home_link:
    :return: 各相册的链接
    '''

    webdriverObj.get(album_home_link)
    albumLinks = get_one_page_album_links_and_imgs_count(webdriverObj)
    print 'first_page:', len(albumLinks)
    total_pages = get_album_total_pages(webdriverObj, album_home_link)
    print 'pages:', total_pages
    for x in range(1, total_pages):
        next_btn = webdriverObj.find_element_by_xpath('//*[@id="J_panel"]/a[3]')
        if next_btn:
            next_btn.click()
            try:
                WebDriverWait(webdriverObj, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'mm-photo-cell')))
            except selenium.common.exceptions.TimeoutException, e:
                print e
                print 'presence_of_element_located Error'
            time.sleep(2)
            links = get_one_page_album_links_and_imgs_count(webdriverObj)
            print 'links:', len(links)
            albumLinks.extend(links)

    return albumLinks

def get_album_total_pages(webdriverObj, album_home_link):
    '''
    :param webdriverObj:
    :param album_home_link:
    :return: 相册的页数
    '''
    webdriverObj.get(album_home_link)

    try:
        WebDriverWait(webdriverObj, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'mm-photo-cell')))
    except selenium.common.exceptions.TimeoutException, e:
        print e
        print 'presence_of_element_located Error'
        return 0

    r = re.findall(ur'skip">共(\d+)页 到第<input type', webdriverObj.page_source)

    pages = 0
    if r:
        pages = r[0]

    pages = tool.str_to_int(pages)

    return pages

def get_imgurls_from_album_link(webdriverObj, album_link):
    '''
    从相册链接中获取各图片地址
    :param webdriverObj:
    :param album_link:
    :return: 各图片地址
    '''
    webdriverObj.get(album_link)
    time.sleep(2)

    '''
    打开相册之后，相册的图片是动态生成的，默认只显示一部分，
    需要网下拉滚动条才会生成更多的图片，
    下面的代码是模拟网下拉滚动条到底5次。为了简化这里只是简单的拉5次，
    实际上可以根据照片的数量决定拉几次的。
    '''
    for i in range(0, 5):
        webdriverObj.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

    img_elems = webdriverObj.find_elements_by_xpath('//div[@class="mm-photoimg-area"]/a/img')
    img_urls = []
    for x in img_elems:
        url = x.get_attribute('src')
        img_urls.append(url)

    return img_urls

#for test
def down_imgs_from_album_link(webdriverObj, album_link, imgs_count):
    '''
    从相册链接中获取各图片地址
    :param webdriverObj:
    :param album_link:
    :return: 各图片地址
    '''
    webdriverObj.get(album_link)
    time.sleep(2)

    '''
    打开相册之后，相册的图片是动态生成的，默认只显示一部分，
    需要网下拉滚动条才会生成更多的图片，
    下面的代码是模拟网下拉滚动条到底5次。为了简化这里只是简单的拉5次，
    实际上可以根据照片的数量决定拉几次的。
    '''
    a_elems = webdriverObj.find_elements_by_xpath('//div[@id="J_Photo_fall"]/div[@class="ks-waterfall mm-photoW-cell"]/div/div[@class="mm-photoimg-area"]/a')

    default_imgs_count = len(a_elems)  # 下拉前默认展示的图片数量，下拉一次生成的照片也是这个数量
    if default_imgs_count == 0:
        return []


    pull_count = int(math.ceil(imgs_count / float(default_imgs_count))) + 1  # 计算下拉次数
    # for test
    print 'default count:', default_imgs_count
    print 'pull_count:', pull_count

    for i in range(0, pull_count):
        webdriverObj.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

    a_elems = webdriverObj.find_elements_by_xpath('//div[@id="J_Photo_fall"]/div[@class="ks-waterfall mm-photoW-cell"]/div/div[@class="mm-photoimg-area"]/a')
    print 'a_elems:', len(a_elems)
    href_urls = []
    for x in a_elems:
        url = x.get_attribute('href')
        href_urls.append(url)

    img_urls = []
    for y in href_urls:
        webdriverObj.get(y)

        try:
            WebDriverWait(webdriverObj, 10).until(
                EC.presence_of_element_located((By.ID, 'J_MmBigImg')))
        except selenium.common.exceptions.TimeoutException, e:
            print e
            print 'presence_of_element_located Error'
            continue

        img_elem = webdriverObj.find_element_by_xpath('//img[@id="J_MmBigImg"]')
        img = img_elem.get_attribute('src')
        if img:
            img_urls.append(img)
            download_single_img(img)

    print 'img_urls:', len(img_urls)

    return img_urls

def download_single_img(img_url):
    print img_url
    try:
       urllib.urlretrieve(img_url, './img/' + os.path.basename(img_url))
    except urllib.ContentTooShortError, e:
        print e
        try:  # 再尝试一次下载
            urllib.urlretrieve(img_url, './img/' + os.path.basename(img_url))
        except urllib.ContentTooShortError, e:
            print e
            print 'secondError: ' + img_url

def download_imgs(imgurls):
    '''
    下载图片
    :param imgurls:
    :return:
    '''
    img_dir = './img'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    for x in imgurls:
        download_single_img(x)

def get_model_info_links(webdriverObj, model_list_page_link):
    '''
    从https://mm.taobao.com/json/request_top_list.htm?page=XXX获取模特个人信息页面地址
    '''
    webdriverObj.get(model_list_page_link)
    time.sleep(1)
    model_info_links = []
    info_link_elems = webdriverObj.find_elements_by_xpath('//p[@class="top"]/a[@class="lady-name"]')
    for x in info_link_elems:
        info_link = x.get_attribute('href')
        model_info_links.append(info_link)

    return model_info_links

def get_model_album_home_links(webdriverObj, model_info_link):
    '''
    从模特个人信息页获取相册主页链接
    :param webdriverObj:
    :param model_info_link:模特个人信息页链接
    :return:相册主页链接
    '''
    webdriverObj.get(model_info_link)
    time.sleep(1)
    album_home_links = []
    link_elems = webdriverObj.find_elements_by_xpath('/html/body/div[4]/div[1]/ul/li[1]/span/a')
    for x in link_elems:
        link = x.get_attribute('href')
        album_home_links.append(link)

    return album_home_links

def get_model_list_links(page_num):
    '''
    生成模特列表页，每页10个模特信息。
    max_page最大为4300（准确的值没有详细测试过，大概在4300左右）
    '''

    # https://mm.taobao.com/json/request_top_list.htm?page=4300
    if page_num > 4300:
        page_num = 4300

    if page_num < 1:
        page_num = 1

    base_url = 'https://mm.taobao.com/json/request_top_list.htm?page='
    model_list_links = []
    for x in range(1, page_num+1):
        link = base_url + str(x)
        model_list_links.append(link)

    return model_list_links

if __name__ == '__main__':
    browser = webdriver.Chrome()
    #
    # # for test
    # url_test = 'https://mm.taobao.com/self/album_photo.htm?spm=719.6642053.0.0.CyHHyq&user_id=687471686&album_id=10000702574&album_flag=0'
    # count_test = 45
    # down_imgs_from_album_link(browser, url_test, count_test)
    # input('dfdfdfdfsdf')

    # 只获取前x页模特的相册照片，可根据需要修改page_num的值，
    model_list_links = get_model_list_links(1)

    xCount = -1
    for x in model_list_links:
        model_info_links = get_model_info_links(browser, x)
        xCount += 1
        yCount = -1
        print xCount
        for y in model_info_links:
            album_home_links = get_model_album_home_links(browser, y)
            print 'album_home_links:', album_home_links
            yCount += 1
            zCount = -1
            print xCount, ' ', yCount
            for z in album_home_links:
                links_list = get_model_album_links(browser, z)
                print 'links_list:', links_list
                for item in links_list:
                    link = item['link']
                    count = item['count']
                    down_imgs_from_album_link(browser, link, count)

                # album_links = get_model_album_links(browser, z)
                # zCount += 1
                # iCount = -1
                # print xCount, ' ', yCount, ' ', zCount
                # for i in album_links:
                #     iCount += 1
                #     print 'list_page_num:', xCount, ' ', 'model_num:', yCount,  ' ', 'album_home_num:', zCount,  ' ', 'album_num:', iCount
                #     down_imgs_from_album_link(browser, i)

