import requests
import re
import json
import os
from requests.exceptions import RequestException
from multiprocessing import Pool
from bs4 import BeautifulSoup
from hashlib import md5
import random
import time
from set_header import set_header
from db import save_img_to_db, save_img_title, select_title, select_this_img

# p = open('./proxy.txt')
# proxy_pool = p.read().split('\n')
# p.close()
#
# u = open('./ua.txt')
# ua = u.read().split('\n')
# u.close()

#h获取分类
def get_free_class ():
    try:
        url = 'http://www.mm131.com'
        response = requests.get(url)
        response.encoding = "gbk"
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            html = soup.select('.nav a')[1:]
            for item in html:
                yield {
                    "text": item.text.strip(),
                    "link": item.get("href"),
                    "class_name_en": item.get('href').split("/")[-2]
                }
        return None
    except Exception as e:
        print('get picture class error')
        print(e)
        return None

#获取每个分类下的所有页码链接
def each_class_page (each_class):
    try:
        url = each_class['link']
        response = requests.get(url)
        response.encoding = "gbk"
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            imgs_pages = soup.select('.main .list-left .page-en')
            pat = re.compile('(.*?)' + ".html", re.S)
            stop_index = int(pat.findall(imgs_pages[-1].get('href').split('_')[-1])[0]) + 1
            pages_index = list(range(2, stop_index))
            list_index = imgs_pages[-1].get('href').split('_')[1]
            urls = [url]
            for item in pages_index:
                urls.append(url + "list_" + list_index + "_" + str(item) + ".html")

            return {
                'name': each_class['text'],
                'urls': urls
            }
        return None
    except Exception as e:
        print('each class page error')
        print(e)
        return None

#每个分类的所有图片列表
def each_class_List (pages_list):
    try:
        imgs_list = []
        for page in pages_list:
            #time.sleep(random.uniform(0, 2))
            response = requests.get(page)
            response.encoding = "gbk"
            if response.status_code == 200:
                print("get page: " + page + " success")
                soup = BeautifulSoup(response.text, 'html.parser')
                a_tags = soup.select(".list-left dd a")
                for a in a_tags:
                    if a.get('class'):
                        continue
                    imgs_list.append(a.get('href'))
        return imgs_list
    except Exceprion as e:
        print('each class list error')
        print(e)
        return None

#所有图片标题、链接
def all_img (urls, class_name, class_name_en):
    images = []
    n = 0
    try:
        for url in urls:
            #time.sleep(random.uniform(0, 2))
            response = requests.get(url)
            response.encoding = "gbk"
            if response.status_code == 200:
                n += 1
                print("get url: " + url + " success")
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.select('.content h5')[0].text.strip()
                pics = []
                total_page_text = soup.select('.content .content-page .page-ch')[0].text
                total = int(re.sub("\D", "", total_page_text))
                img_index_list = list(range(1, total + 1))
                img1_url = soup.select('.content .content-pic img')[0].get('src')
                url_arr = img1_url.split('/')
                prefix = url_arr[-2]
                suffix = url_arr[-1].split('.')[-1]
                for i in img_index_list:
                    pics.append("http://img1.mm131.me/pic/" + prefix + "/" + str(i) + "." + suffix)

                select_title_res = select_title(class_name_en, title)
                if not select_title_res:
                    print('no ' + title + " saved")
                    title_id = save_img_title(class_name_en, class_name, title)
                else:
                    print('this ' + title + ' already saved')
                    title_id = select_title_res[0][0]
                images.append({
                    "title": title,
                    "urls": pics,
                    "title_id": title_id
                })
            if n == 5:
                break
        return images
    except Exception as e:
        print("get all images link error")
        print(e)
        return None

def save_img (class_en, title, dir_name, img_name, content, title_id):
    try:
        print("saving: " + class_en + " " + title +" to ./images/" + dir_name + "/" + img_name)
        dir_path = "./images/" + dir_name
        file_path = dir_path + "/" + img_name
        has_dir = os.path.exists(dir_path)
        if not has_dir:
            os.makedirs(dir_path)
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                f.write(content)
                f.close()
        select_this_img_res = select_this_img(class_en, file_path)
        if not select_this_img_res:
            print('this image no saved')
            save_img_to_db(class_en, file_path, file_path, title_id)
        else:
            print('this image ' + select_this_img_res[0][0] + ' already saved')
    except Exception as e:
        print('save image error')
        print(e)
        return None

def load_image(class_name, class_name_en, img):
    try:
        title = img['title']
        urls = img['urls']
        title_id = img['title_id']
        for url in urls:
            url_arr = url.split('/')
            dir_name = url_arr[-2]
            img_name = url_arr[-1]
            #print("loading: " + class_name + " " + title +" " + url + " to " + dir_name + "/" + img_name)
            response = requests.get(url, headers = set_header(url, class_name_en))
            if response.status_code == 200:
                save_img(class_name_en, title, dir_name, img_name, response.content, title_id)
        return None
    except Exception as e:
        print('load image error')
        print(e)
        return None

def main ():
    pic_class = get_free_class()
    for item in pic_class:
        class_name = item['text']
        class_name_en = item['class_name_en']
        each_class_all_pages = each_class_page(item)
        all_list = each_class_List(each_class_all_pages['urls'])
        all_img_list = all_img(all_list, class_name, class_name_en)
        for img in all_img_list:
            load_image(class_name, class_name_en, img)

if __name__ == '__main__':
    main()
