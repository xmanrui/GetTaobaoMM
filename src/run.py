# -*- coding: utf-8 -*-

from selenium import webdriver
import time
import urllib
import os

def get_model_album_links(webdriverObj, album_home_link):
    '''
    从相册主页中获取各相册的链接
    :param webdriverObj:
    :param album_home_link:
    :return: 各相册的链接
    '''
    webdriverObj.get(album_home_link)
    aElements = webdriverObj.find_elements_by_xpath('//div[@class="mm-photo-list clearfix"]/div/div/h4/a')
    albumLinks = []
    for x in aElements:
        link = x.get_attribute('href')
        albumLinks.append(link)
    return albumLinks


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
        print x
        try:
            urllib.urlretrieve(x, './img/' + os.path.basename(x))
        except urllib.ContentTooShortError, e:
            print e
            try: # 再尝试一次下载
                urllib.urlretrieve(x, './img/' + os.path.basename(x))
            except urllib.ContentTooShortError, e:
                print e
                print 'secondError: ' + x

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

    # 只获取前3页模特的相册照片，可根据需要修改page_num的值，
    model_list_links = get_model_list_links(3)

    xCount = -1
    for x in model_list_links:
        model_info_links = get_model_info_links(browser, x)
        xCount += 1
        yCount = -1
        print xCount
        for y in model_info_links:
            album_home_links = get_model_album_home_links(browser, y)
            yCount += 1
            zCount = -1
            print xCount, ' ', yCount
            for z in album_home_links:
                album_links = get_model_album_links(browser, z)
                zCount += 1
                iCount = -1
                print xCount, ' ', yCount, ' ', zCount
                for i in album_links:
                    iCount += 1
                    print xCount, ' ', yCount,  ' ', zCount,  ' ', iCount
                    imgurls = get_imgurls_from_album_link(browser, i)
                    download_imgs(imgurls)




