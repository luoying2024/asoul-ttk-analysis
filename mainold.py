# 原始文件......

!pandas
'''
@Description: 简易智能自动化分析每次节奏的主力军
@Author: sikaozhifu - luoying
@Date: 2021-11-19 23:53：42
@LastEditTime: 2021-11-19 23:53：42
@LastEditors: Please set LastEditors
'''
# aka guns
'''
                       `                
   ``  ..`       ``    `       ``       
      .::`    ` .:-   `.      .:-       
       `         `   --`:          ```  
    ``   `:-..``....- `/`-  ``          
       ` `-:` ``       ` :     ...      
          :..        `.  `:    .::.     
 `` -:.    :  `--   .-.....-     `  .:. 
    `.-    : `-`  `.   ``` -`    `  ``  
           :`..`            :        `` 
    `      -          .`    `: `....-.  
  `        `.   `:---/-/     :-.   -.   
 -:- `.....`-    /-/.--/          ..    
 .` --.    `-    `.`              :     
      `-`                        :`     
        -.  `                  `/`      
         `-.-                   /`      
           --                   `:      
           /                     :      
           `                            

'''

# oidaccess with https://www.bilibili.com/read/cv13942139
# bv get with 知乎 https://www.zhihu.com/question/381784377/answer/1099438784
# 数据分析实现与主家：https://github.com/TomoeMami/asoul-ttk-analysis
import pandas as pd
import io
import requests
import re
import time
import math
import json
from datetime import datetime
import os
# import csv

head = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"}
headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
  }
def BV_AV(bv_id):  
    """ BV号还原AV号 """
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    r = 0
    for i in range(6):
        r += tr[bv_id[s[i]]] * 58 ** i
    return (r - add) ^ xor
def add_url(b_oid, b_type):
    """ 拼接url or https://api.bilibili.com/x/v2/reply?&type={}&oid={}&pn={} """
    return_url = f"https://api.bilibili.com/x/v2/reply/main?&type={b_type}&oid={b_oid}&next="
    return return_url
def b32_url(bili_url):
    """ 禁止重定向 获取访问头里的原链接 """
    return requests.get(bili_url, headers=head, allow_redirects=False).headers['location']

def get_bili_id(bili_url):
    """ 判断传入链接的类型,并获取id """
    url_re = b32_url(bili_url) if "b23.tv" in bili_url else bili_url
    list_re = re.split("/", url_re)
    url_text_re = list_re[len(list_re) - 1]
    
    ##### print(url_text_re)  #re 的链接！！
    
    bili_id_tf = [True if tf in url_text_re else False for tf in ["?", "#"]]
    bili_id = re.findall(r".+?[?|#]", url_text_re)[0][:-1] if any(bili_id_tf) else url_text_re
    if bili_id[0:2] == "cv" or len(list(bili_id)) < 9:  # 判断专栏
        bili_id = bili_id[2:] if bili_id[0:2] == "cv" else bili_id
        bili_type = 2
    else:  # 判断动态或视频
        bili_type = 0 if bili_id[0:2] == "BV" else 1
    # print(bili_id) # id在这里
    """ 0.视频 1.动态 2.专栏 """
    return bili_id, bili_type  # id, type
def get_oid_type(bili_id, bili_type):
    """ 获取url里的type值 """
    if bili_type == 0:  # 视频
        b_oid, b_type = (BV_AV(bili_id), 1)
    elif bili_type == 1:  # 动态
        api_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id='
        r1 = requests.get(api_url + str(bili_id), headers=head).json()
        dynamic_type = r1['data']['card']['desc']['type']
        b_oid = r1['data']['card']['desc']['rid'] if int(dynamic_type) == 2 else bili_id
        b_type = 11 if int(dynamic_type) == 2 else 17
    else:  # 专栏
        b_oid, b_type = (bili_id, 12)
    return b_oid, b_type  # oid, type
def mkdir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
    path=path.encode('utf-8')
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False
#repost代表所有转发，post代表动态。
def timestamp_datetime(value):
    format = r'%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    # 经过localtime转换后变成
    # time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt
def pull(pn,file_dir,target_list):

  for i in target_list: 
        bili_id, bili_type = get_bili_id(i)
        b_oid, b_type = get_oid_type(bili_id, bili_type)
        print('new task--'+b_oid)
        oid = b_oid
        gettype = b_type
        if gettype == 11:
            get_url='https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id=%s' % oid
            response = requests.get(get_url, headers=headers)
            oid = response.json()['data']['card']['desc']['rid']
        comment_url = 'https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type=%s&oid=%s&sort=1' % (gettype,oid)
        response = requests.get(comment_url, headers=headers)
        count = response.json()['data']['page']['count']  # 评论总数
        page_count = math.ceil(int(count) / 20)  # 评论总页数
        print('计算评论总页数为'+str(page_count)+'页，大约需要'+str(page_count*7)+'s....')
        comment_list = []
        #追加模式
        for pn in range(1, page_count + 1):
            print(str(pn)+'页')
            comment_url = 'https://api.bilibili.com/x/v2/reply?pn=%s&type=%s&oid=%s&sort=1' % (pn, gettype,oid)
            time.sleep(0.5)
            response = requests.get(comment_url, headers=headers)
            if('data' in response.json().keys()):
                replies = response.json()['data']['replies']
                if replies is not None:
                  ####
                    n=0
                    tot=0
                  ####  
                    for reply in replies:
                      ####
                        tot=tot+1
                        n=n+1
                        print('处理数'+str(tot)+' -拉取第'+str(n)+'条评论....')
                      ####
                        # reply_id = reply['member']['mid']
                        # reply_name = reply['member']['uname']
                        # reply_time = timestamp_datetime(int(reply['ctime']))  # 评论时间
                        # reply_like = reply['like']  # 评论点赞数
                        # reply_content = reply['content']['message']  # 评论内容
                        reply_info = {
                            'reply_id': reply['member']['mid'],  # 评论者id,
                            'reply_name': reply['member']['uname'],  # 评论者昵称
                            'reply_time': timestamp_datetime(int(reply['ctime'])),  # 评论时间
                            'reply_like': reply['like'],  # 评论点赞数
                            'reply_content': reply['content']['message']  # 评论内容
                        }
                        comment_list.append(reply_info)
                        rcount = reply['rcount']  # 表示回复的评论数
                        # print(str(rcount))
                        page_rcount = math.ceil(int(rcount) / 10)  # 回复评论总页数
                        root = reply['rpid']
                        ####
                        m=0
                        ####
                        for reply_pn in range(1, page_rcount + 1):
                            ####
                            m=m+1
                            tot=tot+1
                            ####
                            print('处理数'+str(tot)+' -拉取第'+str(n)+'条评论中的第'+str(m)+'条子评论..')
                            time.sleep(0.4)
                            reply_url = 'https://api.bilibili.com/x/v2/reply/reply?&pn=%s&type=%s&oid=%s&ps=10&root=%s' % (reply_pn,gettype, oid, root)
                            response = requests.get(reply_url, headers=headers)
                            if('data' in response.json().keys()):
                                rreplies = response.json()['data']['replies']
                                if rreplies is not None:
                                    for reply in rreplies:
                                        # reply_id = reply['member']['mid']  # 评论者id
                                        # reply_name = reply['member']['uname']  # 评论者昵称
                                        # reply_time = timestamp_datetime(int(reply['ctime']))  # 评论时间
                                        # reply_like = reply['like']  # 评论点赞数
                                        # reply_content = reply['content']['message']  # 评论内容
                                        reply_info = {
                                            'reply_id': reply['member']['mid'],  # 评论者id,
                                            'reply_name': reply['member']['uname'],  # 评论者昵称
                                            'reply_time': timestamp_datetime(int(reply['ctime'])),  # 评论时间
                                            'reply_like': reply['like'],  # 评论点赞数
                                            'reply_content': reply['content']['message']  # 评论内容
                                        }
                                        comment_list.append(reply_info)
                    mkdir(file_dir)
                    save_path=file_dir+str(b_oid)+'-4.json' #每中断一次更新一次
                    with open(save_path, "w", encoding='utf-8') as f:
                        json.dump(comment_list, f, ensure_ascii=False, indent=4, separators=(',', ':'))
                    with open(str(pnt), "w", encoding='utf-8') as f:
                        f.write('pn='+str(pn)+'\n')
            

# first like this


#复制粘贴到此为止

# sys.path.append('/content/drive/My Drive/'+timedate+'/')

def second(file_dir):
    print("开始分析...."+file_dir)
    all_json_list = os.listdir(file_dir)  # get json list
    for single_json in all_json_list:
        if(single_json.endswith('.json')):
            single_data_frame = pd.read_json(os.path.join(file_dir, single_json))
            if single_json == all_json_list[0]:
                all_data_frame = single_data_frame
            else:  # concatenate all json to a single dataframe, ingore index
                all_data_frame = pd.concat([all_data_frame, single_data_frame], ignore_index=True)
    totalreplyers = all_data_frame.drop_duplicates(subset=['reply_name'])
    totalreplys = len(all_data_frame)
    loc=all_data_frame['reply_name'].value_counts()
    
    loc40=loc[:40]
    loc20=loc[:20].keys()
    loc20d=loc[:20]
    lastsave=time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()+28800))

    with open((file_dir+'【'+timedate+'节奏分析】.md').encode('utf-8'),'w',encoding='utf-8') as f:
        f.write('# '+timedate+'节奏分析\n\n')
        f.write('> # **本文件最后更新于'+str(lastsave)+'** \n\n')
        f.write('本次节奏，共有 **'+str(len(totalreplyers))+'** 人参与，发表了 **'+str(totalreplys)+'** 个回复。\n\n\n')
        if int(totalreplys)< 20 :
            num=int(totalreplys)
        else:
            num=20 
        
        if int(len(totalreplyers))< 20 :
            numer=int(len(totalreplyers))
        else:
            numer=20
        
        f.write('# 按照回复次数进行划分，与人数的对应关系如下表所示：\n\n')
        loccount = loc.value_counts(bins=10)
        loccount.name = '人数'
        loccount.index.name = '回复次数'
        f.write(loccount.to_markdown()+'\n\n')
        f.write('# 其中，最活跃的人(<41)相关回复次数如下表所示：\n\n')
        loc40.name = '回复次数'
        loc40.index.name = '昵称'
        f.write(loc40.to_markdown()+'\n\n')
        f.write('## 按照点赞数排序，这'+str(len(totalreplyers))+'人的回复中，被点赞前'+str(num)+'条分别是： \n\n')
        top40 = all_data_frame.loc[all_data_frame['reply_name'].isin(loc40.index)]
        top40likes = top40.sort_values(by='reply_like',ascending=False)
        top40likes20 = top40likes[:20]
        for k in range(num):
            f.write('  **'+top40likes20['reply_name'].iloc[k]+'**  发表于  '+str(top40likes20['reply_time'].iloc[k])+' **'+str(top40likes20['reply_like'].iloc[k])+'** 赞：' +'\n\n')
            f.write('<blockquote> '+top40likes20['reply_content'].iloc[k]+ '</blockquote>\n\n\n')
            f.write('-----\n\n')
        f.write('# 接下来，让我们看看前 '+str(numer)+' 回复者的具体动态：\n\n')
        for i in range(numer):
            person=all_data_frame.loc[all_data_frame['reply_name']==loc20[i]]
            plikes = person.sort_values(by='reply_like',ascending=False)
            plikes5 = plikes[:5]
            f.write('## 第'+str(i+1)+'名： **'+loc20[i]+'** \n\n')
            f.write('TA一共回复了 **'+str(loc20d[i])+'** 条消息，在 **'+str(len(totalreplyers))+'** 人中勇夺第 **'+str(i+1)+'** ！ \n\n')
            if int(loc20d[i])< 5 :
                numm=int(loc20d[i])
            else:
                numm=5
            
            f.write('### 按照点赞数排序，TA回复被点赞前'+str(numm)+'条分别是： \n\n')
            for k in range(numm):
                f.write(' 发表于'+str(plikes5['reply_time'].iloc[k])+' **'+str(plikes5['reply_like'].iloc[k])+'** 赞：' +'\n\n')
                f.write('<blockquote> '+plikes5['reply_content'].iloc[k]+ '</blockquote>\n\n\n')
                f.write('-----\n\n')
        f.write('# 最后，让我们来看一下点赞前'+str(numer)+'的评论：\n\n')   
        ltop20 = all_data_frame.sort_values(by='reply_like',ascending=False)[:20]
        for k in range(numer):
            f.write('  **'+ltop20['reply_name'].iloc[k]+'**  发表于  '+str(ltop20['reply_time'].iloc[k])+'  **'+str(ltop20['reply_like'].iloc[k])+'** 赞：' +'\n')
            f.write('<blockquote> '+ltop20['reply_content'].iloc[k]+ '</blockquote>\n\n\n')
            f.write('-----\n\n')
        f.write('# 特别颁发的奖项\n\n')  
        f.write('## 抛砖引砖奖：\n\n') 
        f.write('在楼中楼里被他人回复最多次。\n\n') 
        rreply = all_data_frame[all_data_frame['reply_content'].str.contains('回复 @.+ ?')]
        rrstars = rreply['reply_content'].str.extract(r'(@.+:)')
        rrstar = rrstars.value_counts()[:10]
        rrstar.name = '回复次数'
        rrstar.index.name = '昵称'
        f.write(rrstar.to_markdown()+'\n\n')    
        f.write('-----\n\n')
        f.write('## 你说你EMOJI呢奖：\n\n') 
        f.write('被使用最多次的B站表情（不含emoji）。\n\n') 
        emotes = all_data_frame[all_data_frame['reply_content'].str.contains('\[.+?\]')]
        emotes = emotes['reply_content'].str.extract(r'(\[.+?\])')
        emote = emotes.value_counts()[:10]
        emote.name = '使用次数'
        emote.index.name = '表情名称'
        f.write(emote.to_markdown()+'\n\n')   
        f.write('-----\n\n')
        f.write('## 谈笑风生奖：\n\n') 
        f.write('发送带表情的评论最多条数。\n\n') 
        pemotes = all_data_frame[all_data_frame['reply_content'].str.contains('\[.+?\]')]
        pemote = pemotes['reply_name'].value_counts()[:10]
        pemote.name = '带表情评论条数'
        pemote.index.name = '昵称'
        f.write(pemote.to_markdown()+'\n\n')   
        f.write('-----\n\n')
        f.write('# 本次数据统计的采样来源：'+'\n\n')
        for i in range(len(target_list)):
          f.write (("> - %s - %s" % (i + 1, target_list[i]))+'\n\n')
        print("分析完毕....")
        '''
        for thread in threads:
            if(thread['mode'] == 'repost' or thread['mode'] == 'post'):
                f.write(' https://t.bilibili.com/'+str(thread['oid'])+'\n\n')
            elif(thread['mode'] == 'cv'):
                f.write(' https://www.bilibili.com/read/cv'+str(thread['oid'])+'\n\n')
            elif(thread['mode'] == 'av'):
                f.write(' https://www.bilibili.com/video/av'+str(thread['oid'])+'\n\n')
        '''
        


if __name__ == "__main__":
    # 目标链接配置
    target_list = [] 
    target_list.append('https://www.bilibili.com/read/cv14018730') 
    target_list.append('https://www.bilibili.com/read/cv14017996') 
    target_list.append('https://www.bilibili.com/read/cv13698060')
    targetnow = True
    
    # 时间拼接判定
    date01 = datetime.today()
    if targetnow:
      playnow='d-'+str(date01.hour)+'h-'+str(date01.minute)+'m'
      print("当前为：即时分析模式！")
    else:
      playnow=''

    timedate=str(date01.year)+'-'+str(date01.month)+'-'+str(date01.day)+playnow

    # 目录设置区域（注意配置）
    file_dir = './content/drive/My Drive/'+timedate+'/'
    # pn value there
    # filedir = './content/drive/My Drive/'+timedate+'/' # all use file_dir
    pnt = './content/drive/My Drive/pn.txt' # write pn to this path~

    # 执行区
    isExists=os.path.exists(file_dir)
    if not isExists:
      print("创建new任务,拉取数据中....")
      pull(pnt,file_dir,target_list)
      second(file_dir)
    else:
      print("防止重复请求，正在重新分析旧数据.... 如需要启用即时分析，请更改targetnow为True否则为False.....")
      second(file_dir)

    
