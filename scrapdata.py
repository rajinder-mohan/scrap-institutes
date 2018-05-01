from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import sqlite3
from sqlite3 import Error
import os
import re
from bs4 import BeautifulSoup
import json

proxy = {'address': '123.123.123.123:2345',
         'username': 'johnsmith123',
         'password': 'iliketurtles'}


capabilities = dict(DesiredCapabilities.CHROME)
capabilities['proxy'] = {'proxyType': 'MANUAL',
                         'httpProxy': proxy['address'],
                         'ftpProxy': proxy['address'],
                         'sslProxy': proxy['address'],
                         'noProxy': '',
                         'class': "org.openqa.selenium.Proxy",
                         'autodetect': False}

capabilities['proxy']['socksUsername'] = proxy['username']
capabilities['proxy']['socksPassword'] = proxy['password']


chrome_options = webdriver.ChromeOptions()
browser = webdriver.Chrome(chrome_options=chrome_options)
main_url = "https://www.guidetoonlineschools.com/degrees"
program_url_list = []
program_url_list_n = []
err_url = ""
try:
    browser.get(main_url)
    page_source=browser.page_source
    html = BeautifulSoup(page_source,"lxml")
    table = html.find('table',{'class': 'mobile-reflow'})
    trs = table.find_all('tr')
    for tr in trs:
        tr_attrb = tr.attrs
        if "id" not in tr_attrb:
            td = tr.find_all('td')[0]
            anchor_tag = td.find("a")
            href = anchor_tag.attrs['href']
            program_url_list.append(href)
    program_url_list_n = program_url_list[31:]
except Exception as e:
    raise e

for link in program_url_list_n:
    main_list = []
    institute_urls = []
    time.sleep(1)
    try:
        browser.get(link)
        time.sleep(10)
        browser.execute_script('var aTags = document.getElementsByTagName("a");var searchText = "Show All";var found;for (var i = 0; i < aTags.length; i++) if (aTags[i].textContent == searchText) { found = aTags[i]; found.click(); break;}')
        print("element is clicked check page")
        time.sleep(10)
        page_source=browser.page_source
        html = BeautifulSoup(page_source,"lxml")
        table = html.find('table',{'class': 'school-info'})
        trs = table.find_all('tr',{'class':'colleges'})
        for tr in trs:
            td = tr.find_all('td')[0]
            anchor_tag = td.find("a")
            href = anchor_tag.attrs['href']
            institute_urls.append(href)
    except Exception as e:
        continue
    for scrapurl in institute_urls:

        try:
            full_url = "https://www.guidetoonlineschools.com"+scrapurl
            print(full_url)
            err_url = full_url
            # mobile_url = "https://www.guidetoonlineschools.com/online-schools/bellevue-university?pid=2010"
            # mobile_url = "https://www.guidetoonlineschools.com/online-schools/abraham-lincoln-university?pid=2010"
            # mobile_url = "https://www.guidetoonlineschools.com/online-schools/baker-college-online"
            browser.get(full_url)
            institute_name = ""
            dprogram_list = []
            sub_list = []
            dprogram_dic = {}
            sub_dict = {}
            page_source=browser.page_source
            html = BeautifulSoup(page_source,"lxml")
            try:
                ins_div = html.find('div', {'id': 'lp-wrap'})
                institute_name = ins_div.find('h1').text
            except Exception as e:
                ins_div = html.find('div', {'class': 'landing_page_chain'})
                institute_name = ins_div.find_next('h1').text
            sub_dict["Form Instructions"] = ""
            sub_dict["Additional Information"] = ""
            div_college_content = html.find_all('div',{'class':'college_content'})
            for divs in div_college_content:
                paragraph = divs.find('p')
                attrb_p_dict = paragraph.attrs
                if "class" not in attrb_p_dict:
                    sub_dict["Form Instructions"] = paragraph.text
                else:
                    sub_dict["Additional Information"] = paragraph.text
            sub_dict["title"] = institute_name
            program = ""
            program_div = html.find_all('span', {'class': 'mdl-radio__label'})
            for divs in program_div:
                divtext = divs.text
                divtext = ' '.join(divtext.split())
                if divtext == "All Programs":
                    pass
                else:
                    program = divtext
            
            program = ' '.join(program.split())
            sub_pro = html.find('div',{'class':'college-programs'})
            try:
                data_divs = sub_pro.find_all('div',{'class':'tab_content'})
                if data_divs:
                    sub_list = []
                    for div in data_divs:
                        dprogram_dic = {}
                        newdiv = div.find('div',{'class':'sub-header'})
                        attr_dict = newdiv.attrs
                        if "style" not in attr_dict:
                            div_text = (newdiv.text).strip()
                            level = ""
                            if div_text[-1] == ")":
                                level = (div_text[0:-3]).strip()
                            else:
                                level = div_text
                            
                            dprogram_dic["program"] = program
                            key_value = "other"
                            splitted = level.split(" ")[0]
                            if splitted == "Bachelor's":
                                key_value = "BA"
                                level = "Bachelor's"
                            if splitted == "Master's":
                                key_value = "MA"
                                level = "Master's"
                            if splitted == "Doctoral":
                                key_value = "PHD"
                                level = "Doctorate"
                            if splitted == "Certificate":
                                key_value = "Certificate"
                                level = "Certificate & Diplomas"
                            if splitted == "Diploma":
                                key_value = "Diploma"
                                level = "Certificate & Diplomas"
                            dprogram_dic["degreeLevel"] = level
                            newli = div.find_all('li')
                            dprogram_list = []
                            for li in newli:
                                li_attr_dict = li.attrs 
                                if "style" not in li_attr_dict:
                                    li_text = (li.find("span").text).strip()
                                    append_elmnt = key_value+":"+li_text
                                    dprogram_list.append(append_elmnt)
                            dprogram_dic["programSpecific"] = dprogram_list
                            sub_list.append(dprogram_dic)
                else:
                    data_divs = sub_pro.find_all('ul',{'class':'college-sub-header'})
                    sub_list = []
                    for div in data_divs:
                        dprogram_dic = {}
                        newdiv = div.find('div',{'class':'degree-level'})
                        attr_dict = newdiv.attrs
                        if "style" not in attr_dict:
                            div_text = (newdiv.text).strip()
                            level = ""
                            if div_text[-1] == ")":
                                level = (div_text[0:-3]).strip()
                            else:
                                level = div_text
                            
                            dprogram_dic["program"] = program
                            key_value = "other"
                            splitted = level.split(" ")[0]
                            if splitted == "Bachelor's":
                                key_value = "BA"
                                level = "Bachelor's"
                            if splitted == "Master's":
                                key_value = "MA"
                                level = "Master's"
                            if splitted == "Doctoral":
                                key_value = "PHD"
                                level = "Doctorate"
                            if splitted == "Certificate":
                                key_value = "Certificate"
                                level = "Certificate & Diplomas"
                            if splitted == "Diploma":
                                key_value = "Diploma"
                                level = "Certificate & Diplomas"
                            dprogram_dic["degreeLevel"] = level
                            newli = div.find_all('li')
                            dprogram_list = []
                            for li in newli:
                                li_attr_dict = li.attrs 
                                if "style" not in li_attr_dict:
                                    li_text = (li.find("span").text).strip()
                                    append_elmnt = key_value+":"+li_text
                                    dprogram_list.append(append_elmnt)
                            dprogram_dic["programSpecific"] = dprogram_list
                            sub_list.append(dprogram_dic)
            except Exception as e:
                pass
            sub_dict["degreePrograms"] = sub_list
            main_list.append(sub_dict)
            # print(main_list)
            print(program)
            print(institute_name)
            with open(program+'.txt', 'w+') as file:
                file.write(json.dumps(main_list))
            with open(program+'_count.txt', 'w+') as file:
                file.write(str(len(main_list)))
            time.sleep(2)
        except Exception as r:
            with open('error_urls.txt', 'a+') as file:
                file.write(err_url)
                file.write("\n")
            continue
           
    




