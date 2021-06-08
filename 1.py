# -*- coding: UTF-8 -*-

import os
from bs4 import BeautifulSoup   #网页解析获取数据
import re   #正则
import urllib.request,urllib.error   #获取网页数据
import xlwt #导出excel
import sqlite3 #进行sqlite数据操作
import json

def main():
    url = 'https://www.audi.cn'
    # 创建目录
    if not os.path.exists('audi_cars/images'):
        os.makedirs('audi_cars/images')

    # 获取所有车型和车型详情的url
    baseUrl = 'https://www.audi.cn/cn/web/zh/models.html'
    soup = getHTml(baseUrl)
#     allCars = soup.find_all('a',{"class":"nm-navigation-header-detail-link"})
    allCarsA = soup.find_all(class_="nm-navigation-header-detail-link")
    cars = []
    for carA in allCarsA:
        car = {}
#         car['name'] = "".join(carA.get_text().split())
        car['name'] = carA.get_text()
        car['detail_url'] = "{}{}".format(url,carA.attrs['href'])
        cars.append(car)
#         break
    # 获取所有车型的装备价格表
    i=0#图片名
    for car in cars:
        # 获取装备价格url
        soup = getHTml(car['detail_url'])
        carDetail = soup.find(class_='nm-intro__icon',href=re.compile("performanceequipment_getequipment.htm"))
        print("{}--{}".format(car['name'],i))
        #没有装备
        if not carDetail:
            continue
        car['equipment_url'] = carDetail['href']
        # 获取装备详情
        equimentHtml = getHTml(carDetail['href'])
        equipment = {}
        #下载装备图片
        pic_img = "{}{}".format('https://contact.audi.cn',equimentHtml.find(class_="pic_img1").attrs['src'])
        urllib_download(pic_img,"{}.jpg".format(i))
        i+=1
        #生成装备data
        equipment['type'] = car['name'].strip()
        equipment['data'] = []
        equipment['data'].append({"col": 1,"name": "●标准装备 o可选装备 P选装包 -不提供","type": "p"})

        # 车型与价格
        typeAndPriceHtml = equimentHtml.find(class_='content_scroll')
        typeAndPriceItems = typeAndPriceHtml.find_all(class_='content_right_div')
        typeAndPriceCol = len(typeAndPriceItems)
        typeValues = []
        priceValues = []
        for item in typeAndPriceItems:
            # 车型名
            typeValue = item.select("span:nth-child(1)")[0].string + item.select("span:nth-child(2)")[0].string
            # 车型价格
            priceValue = item.find("i").string
            typeValues.append(typeValue)
            priceValues.append(priceValue)
        equipment['data'].append({"col": typeAndPriceCol,"name": "车型","value": typeValues})
        equipment['data'].append({"col": typeAndPriceCol,"name": "价格","value": priceValues})


        #技术参数
        techParaHtml = equimentHtml.find(class_='content_scroll2').find(class_='content_box')
        # 标题
        techParaText = techParaHtml.find(class_='content_box_title_text').string
        techPara = {"col": 1,"name": techParaText,"type": "h1","isSelect": False}
        techParaData = []
        # 技术参数下的子项techParaHtml
        techParaContentHtml = techParaHtml.find(class_='content_box_row').div
        while  techParaContentHtml:
            if techParaContentHtml.attrs['class'][0] == 'content_box_title2':
                # 如果是标题
                techParaData.append({"col": 1,"name": techParaContentHtml.string,"type": "h2",})
            else:
                name=techParaContentHtml.find(class_='content_left').get_text().strip()
                value = []
                valueHtmls = techParaContentHtml.find_all(class_='content_right_div')
                valueLen = len(valueHtmls)
                for valueHtml in valueHtmls:
                    value.append(valueHtml.get_text())
                techParaData.append({"col": valueLen,"name": name,"value": value,})

            #寻找下一个兄弟节点
            techParaContentHtml = techParaContentHtml.find_next_sibling('div')
        techPara['data'] = techParaData
        equipment['data'].append(techPara)


        #基本装备
        baseEquipmentHtml = techParaHtml.parent.find_next_sibling('div')
        #标题
        baseEquipmentText = baseEquipmentHtml.find(class_='content_box_title_text').string
        baseEquipment = {"col": 1,"name": baseEquipmentText,"type": "h1","isSelect": False}
        baseEquipmentData = []
        #---pause--
        # 基本装备下的子项baseEquipmentHtml
        baseEquipmentContentHtml = baseEquipmentHtml.find(class_='content_box_hide').div
        while  baseEquipmentContentHtml:
            if baseEquipmentContentHtml.attrs['class'][0] == 'content_box_title2':
                # 如果是标题
                baseEquipmentData.append({"col": 1,"name": baseEquipmentContentHtml.string,"type": "h2",})
            else:
                name=baseEquipmentContentHtml.find(class_='content_left').get_text().strip()
                value = []
                valueHtmls = baseEquipmentContentHtml.find_all(class_='content_right_div')
                valueLen = len(valueHtmls)
                for valueHtml in valueHtmls:
                    value.append(valueHtml.get_text())
                baseEquipmentData.append({"col": valueLen,"name": name,"value": value,})

            #寻找下一个兄弟节点
            baseEquipmentContentHtml = baseEquipmentContentHtml.find_next_sibling('div')
        baseEquipment['data'] = baseEquipmentData
        equipment['data'].append(baseEquipment)


        #选装装备
        selectEquipmentHtml = baseEquipmentHtml.find_next_sibling('div')
        #标题
        selectEquipmentText = selectEquipmentHtml.find(class_='content_box_title_text').string
        selectEquipment = {"col": 1,"name": selectEquipmentText,"type": "h1","isSelect": False}
        selectEquipmentData = []
        #---pause--
        # 基本装备下的子项selectEquipmentHtml
        selectEquipmentContentHtml = selectEquipmentHtml.find(class_='content_box_hide').div
        while  selectEquipmentContentHtml:
            if selectEquipmentContentHtml.attrs['class'][0] == 'content_box_title2':
                # 如果是标题
                selectEquipmentData.append({"col": 1,"name": selectEquipmentContentHtml.string,"type": "h2",})
            else:
                name=selectEquipmentContentHtml.find(class_='content_left').get_text().strip()
                value = []
                valueHtmls = selectEquipmentContentHtml.find_all(class_='content_right_div')
                valueLen = len(valueHtmls)
                for valueHtml in valueHtmls:
                    value.append(valueHtml.get_text())
                selectEquipmentData.append({"col": valueLen,"name": name,"value": value,})

            #寻找下一个兄弟节点
            selectEquipmentContentHtml = selectEquipmentContentHtml.find_next_sibling('div')
        selectEquipment['data'] = selectEquipmentData
        equipment['data'].append(selectEquipment)

        #生成装备数据
        car['equipment'] = equipment
        #js文件名
        jsName =  './audi_cars/'+ equipment['type']+'.js'
        #将装备数据格式化
        jsonEquipment = json.dumps(equipment,indent=4).encode('utf-8').decode('unicode_escape')
        jsFile = (
        """\
const carData = [{0}]

export default {{
    carData
}}
        """).format(jsonEquipment)
        f = open(jsName,'w')
        f.write(jsFile)
        f.close()


#         jsObj = json.dumps(car['equipment'],indent=4).encode('utf-8').decode('unicode_escape')
#     print(cars)

# 爬取网页
def getHTml(baseUrl):
    response = urllib.request.urlopen(baseUrl)
    html_doc = response.read().decode('utf-8')
    soup = BeautifulSoup(html_doc,"html.parser")
    return soup
#下载图片
def urllib_download(img_url,local_name):
    from urllib.request import urlretrieve
    urlretrieve(img_url, './audi_cars/images/' + local_name)

if __name__ == "__main__":
    main()