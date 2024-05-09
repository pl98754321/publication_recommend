import requests as rq
import json
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
import datetime
from dotenv import load_dotenv

def get_time():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    time_string = today.strftime("%dD%mM%YY")
    ytime_string = yesterday.strftime("%dD%mM%YY")
    return time_string , ytime_string

def to_csv(result,dt,ref,paperNid,header):
    oldlen = len(dt['id'])
    for id,paper in enumerate(result['search-results']['entry']):
        Nid = paperNid + id + oldlen
        dt['id'].append(Nid)
        dt['link'].append(paper['link'][2]['@href'])
        dt['title'].append(paper['dc:title'])
        dt['publicationName'].append(paper['prism:publicationName'])
        affslist = []
        if 'affiliation' in paper:
            affs = paper['affiliation']
            for aff in affs:
                affslist.append((aff['affilname'] , aff['affiliation-city'] , aff['affiliation-country']))
        dt['affiliation'].append(affslist)
        
        # print(paper['link'][2]['@href'])
        page = rq.get(paper['link'][0]['@href'],headers=header)
        result_ab = page.json()
        #get abstract
        # print("abs",result_ab)
        if 'item' in result_ab['abstracts-retrieval-response']:
            ab = result_ab['abstracts-retrieval-response']['item']['bibrecord']['head']['abstracts']
            #get publication date
            pubdate = result_ab['abstracts-retrieval-response']['item']['bibrecord']['head']['source']['publicationdate']
            dt['abstract'].append(ab)
            dt['publicationDate'].append(pubdate)
            dt['publicationYear'].append(pubdate['year'])
            # print(id,result_ab)
            # get reference count
            if result_ab['abstracts-retrieval-response']['item']['bibrecord']['tail'] != None :
                refcount = result_ab['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']['@refcount']
                dt['ref_count'].append(refcount)
            else:
                dt['ref_count'].append('null')
        
            #reference paper csv
            if result_ab['abstracts-retrieval-response']['item']['bibrecord']['tail'] != None:
                allref = result_ab['abstracts-retrieval-response']['item']['bibrecord']['tail']['bibliography']['reference']
                for j in allref:
                    # print(Nid , j)
                    if type(j) is dict:
                        ref['id'].append(Nid)
                        if 'ref-fulltext' in j:
                            ref['ref_authors'].append(j['ref-fulltext'])
                        else:
                            ref['ref_authors'].append('null')
                        if "ref-publicationyear" in j['ref-info']:
                            ref['ref_publicationyear'].append(j['ref-info']['ref-publicationyear']['@first'])
                        else:
                            ref['ref_publicationyear'].append('null')
                        if 'ref-title' in j['ref-info']:
                            ref['ref_title'].append(j['ref-info']['ref-title']['ref-titletext'])
                        else:
                            ref['ref_title'].append('null')

    return dt,ref

def get_scraping():
    my_path = os.getcwd()
    api_key = '403f16e2d699027ef9f5e9077f6842ad'
    ninja_api_key = 'bG/Q3BLOWdlb0zchs8ezrA==sME0wftYnNrSvxPv'

    # setup the HTTP headers
    header = {"Accept": "application/json", "X-ELS-APIKey": api_key}

    # Break down the variables for the search query
    api_url = "https://api.elsevier.com/content/search/scopus?query="
    pubyear = ['2018','2019','2020','2021','2022','2023','2024']


    time_string, ytime_string = get_time()

    #create folder a day
    day_folder = my_path+'\\research_csv\\'+time_string
    yesterday_folder = my_path+'\\research_csv\\'+ytime_string

    if not os.path.exists(day_folder):
        os.mkdir(day_folder)    

    #yesterday paper info and yesterday ref info
    ypaper_info = pd.DataFrame()
    yref_info = pd.DataFrame()

    if os.path.exists(yesterday_folder):
        if os.path.exists(yesterday_folder+'\\paper_info.csv'):
            ypaper_info = pd.read_csv(yesterday_folder+'\\paper_info.csv',index_col=0)
        if os.path.exists(yesterday_folder+'\\ref_info.csv'):
            yref_info = pd.read_csv(yesterday_folder+'\\ref_info.csv',index_col=0)

    #paper next id and ref next id
    paperNid = len(ypaper_info.index)


    dt = dict()
    dt['id'] = []
    dt['link']= []
    dt['title']= []
    dt['publicationName']= []
    dt['affiliation']= []
    dt['abstract'] = []
    dt['publicationDate'] = []
    dt['ref_count'] = []
    dt['publicationYear'] = []


    ref = dict()
    ref['id'] = []
    ref['ref_authors'] = []
    ref['ref_publicationyear'] = []
    ref['ref_title'] = []


    #publicatino year 2018 and doctype article
    days_fetch = len(os.listdir('.\\research_csv'))-1
    for i in range(len(pubyear)):
        search_query = '%28PUBYEAR%20%3D%20'+pubyear[i]+'%29%20AND%20%28DOCTYPE%28ar%29%29'
        itemperpage = '20'
        response = rq.get(api_url + search_query +"&count="+itemperpage  + "&start=" +str(int(itemperpage) *days_fetch) , headers = header)
        result = (response.json())
        print(result)
        dt, ref = to_csv(result,dt,ref,paperNid,header)
        
    df = pd.DataFrame.from_dict(dt)
    ref_df = pd.DataFrame.from_dict(ref)

    paper_info = df
    paper_info['affil_coor'] = paper_info.apply(lambda x : [] , axis=1)
    coor = dict()
    if os.path.exists(my_path+'\\coor.json'):
        f = open('coor.json')
        coor = json.load(f)
        f.close()
        

    for i in range(0,len(paper_info.index)):
        # print(type(paper_info.loc[i,'affiliation']))
        if isinstance(paper_info.loc[i,'affiliation'] , list):
            aff = paper_info.loc[i,'affiliation']
        else: aff = eval(paper_info.loc[i,'affiliation'])
        if len(aff) > 0:
            for j in aff:
                city = j[1]
                country = j[2]
                if (city is not None) and (country is not None):
                    coor_key = city + ' ' + country
                    if coor_key not in coor:
                        api_url = 'https://api.api-ninjas.com/v1/geocoding?city='
                        response = rq.get(api_url + city + '&country=' + country, headers={'X-Api-Key': ninja_api_key})
                        resjson = response.json()
                        
                        if len(resjson) > 0:
                            coor[coor_key] = str(resjson[0]['latitude']) + " " + str(resjson[0]['longitude'])
                            paper_info.loc[i,'affil_coor'].append(coor[coor_key])
                            # print(city,country,resjson,coor)
                        else:
                            coor[coor_key] = ""
                            paper_info.loc[i,'affil_coor'].append(coor[coor_key])
                    else:
                        paper_info.loc[i,'affil_coor'].append(coor[coor_key])
                else:
                    paper_info.loc[i,'affil_coor'].append('')
        
    with open("coor.json",'w') as coorjson:
        json.dump(coor , coorjson)


    df = pd.concat([ypaper_info , paper_info] , join='inner' ,ignore_index=True)
    ref_df = pd.concat([yref_info , ref_df] , join='inner' , ignore_index=True)

    df.to_csv(day_folder+'\\paper_info.csv')
    ref_df.to_csv(day_folder+'\\ref_info.csv')

    paper_info_file = day_folder+'\\paper_info.csv'
    ref_info_file = day_folder+'\\ref_info.csv'

    return paper_info_file , ref_info_file
