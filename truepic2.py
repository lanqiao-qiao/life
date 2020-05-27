import requests
import urllib.request
import re
from lxml import etree
import csv
import os
import threading

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
s=''
pa=int(10)
use_url=''
use_name=''
pic_name=[]
pic_url=[]
cap_name=[]
cap_url=[]
use_path=''
use_path2=''
all=int(0)

def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print( path + ' 创建成功')
        return True
    else:
        print('目录已存在')
        return False

def get_which_pic():
    print("输入搜索的漫画的名称(支持模糊查询):")
    str=input()
    pr={"q":str}
    url="https://www.2animx.com/search-index?searchType=1"
    response=requests.get(url,headers=header,params=pr)
    global use_url
    use_url=response.url
    html=response.text
    tree=etree.HTML(html)
    page = tree.xpath("/html/body/div[2]/div[5]/font[2]/text()")
    global pa
    if int(page[0])==0:
        print("无搜索结果，按任意键返回重试")
        input()
        get_which_pic()
    pa = int(page[0]) // 30 + 1
    print("搜索结果 "+page[0]+" 条，共 ",pa," 页。")

def get_all_pic():
    for i in range(1,pa+1):
        #print(i)
        print("检索中，当前 ",i," / ",pa)
        pr={"page":str(i)}
        response = requests.get(use_url, headers=header, params=pr)
        html = response.text
        tree = etree.HTML(html)
        #print(response.url)
        p = tree.xpath("/html/body/div[3]/div[2]/ul/li/a/@title")
        u = tree.xpath("/html/body/div[3]/div[2]/ul/li/a/@href")
        global pic_name,pic_url
        for i in range(len(p)):
            p[i].strip()
            pic_name.append(p[i])
            pic_url.append(u[i])

def choice_pic():
    print("请选择浏览漫画信息方式：")
    print("1.在命令行中查看(推荐搜索结果少时)")
    print("2.生成csv文件来查看")
    print("3.生成txt文件来查看")
    print("4.我全都要")
    c=input()
    if c=="1":
        print_one()
    if c=="2":
        print_two()
    if c=="3":
        print_three()
    if c=="4":
        print_one()
        print_two()
        print_three()

def print_one():
    for i in range(len(pic_name)):
        print(str(i+1)+": "+pic_name[i])
    choice()

def print_two():
    with open("D://a动漫列表.csv","w",newline="",encoding='utf_8_sig') as f:
        w=csv.writer(f)
        w.writerow(['序号','名字'])
        for i in range(len(pic_name)):
            w.writerow([str(i+1),pic_name[i]])
        f.close()

def print_three():
    with open("D://a动漫列表.txt","w") as f:
        for i in range(len(pic_name)):
            f.write(str(i+1)+"  "+pic_name[i]+'\n')

def choice():
    print("请输入所选择的序号：")
    a=int(input())-1
    global use_url,use_name
    use_url=pic_url[a]
    use_name=pic_name[a]

def get_chapter():
    response=requests.get(use_url,headers=header)
    html=response.text
    tree=etree.HTML(html)
    global cap_url,cap_name
    cap_name=tree.xpath('/html/body/div[2]/div[6]/div[1]/div/div[4]/div[2]/div[1]/div[5]/div[1]/ul/li/a/text()')
    cap_url=tree.xpath('/html/body/div[2]/div[6]/div[1]/div/div[4]/div[2]/div[1]/div[5]/div[1]/ul/li/a/@href')
    global all
    all=len(cap_name)
    print("共找到 ",len(cap_name),"章节")
    with open("D://a章节.txt","w",encoding='utf-8') as f:
        for i in range(len(cap_name)):
            f.write(str(i+1)+": "+cap_name[i]+'\n')
    print('\n'+"已存储到D盘 a章节.txt中"+'\n')
    print("是否在命令行中展示？输入0不展示")
    if input()!='0':
        for i in range(len(cap_name)):
            print(str(i+1)+"  "+cap_name[i])

def choice_download():
    print("是否要下载这本漫画？ (0不同意，程序结束)(同意既在D://apic//漫画名 路径下存放下载章节)")
    if input()!="0":
        path="D://apic//"+use_name
        global use_path,use_path2
        use_path=path
        use_path2=path
        #print(path)
        mkdir(path)
    else:
        return None
    print("请选择下载方式")
    print("1.下载单章")
    print("2.下载全本")
    print("3.下载部分章节")
    pp=input()
    if pp=="1":
        download_one()
    if pp=="2":
        download_two()
    if pp=="3":
        download_three()

def download_one():
    print("输入要下载的章节序号")
    a=int(input())
    global use_url
    use_url = cap_url[a - 1]
    response=requests.get(use_url,headers=header)
    html=response.text
    pattern='第 1 / (.*?)頁'
    p=re.compile(pattern).findall(html)
    global pa
    pa=int(p[0])
    global use_path
    use_path += "//" + cap_name[a - 1].strip()
    mkdir(use_path)
    print("选择下载方式")
    print("1.单线程下载.(稳定性强)")
    print("2.多线程下载.(速度快)")
    if input()=='1':
        download_one_one()
    else:
        download_one_two()

def download_one_one():
    global pa
    for i in range(1,pa+1):
        url=use_url+"-p-"+str(i)
        download_pic1(url,i)
        print("当前进度",i," / ",pa)

def download_one_two():
    global pa
    for i in range(1, pa + 1):
        url = use_url + "-p-" + str(i)
        t=threading.Thread(target=download_pic1,args=(url,i,))
        t.start()
        print("当前进度", i, " / ", pa)
        t.join()

def download_two():
    global pa
    global use_path
    path = use_path
    for i in range(1, all+1):
        use_path = path
        t = threading.Thread(target=download_three_one, args=(i,))
        t.start()
        t.join()

def download_three():
    print("输入起始章节序号")
    a=int(input())
    print("输入终止章节序号")
    b=int(input())
    global use_path
    path=use_path
    for i in range(a,b+1):
        use_path=path
        t=threading.Thread(target=download_three_one,args=(i,))
        t.start()
        t.join()

def download_three_one(i):
    global use_url
    use_url = cap_url[i - 1]
    response = requests.get(use_url, headers=header)
    html = response.text
    pattern = '第 1 / (.*?)頁'
    p = re.compile(pattern).findall(html)
    global pa
    pa = int(p[0])
    global use_path
    use_path += "//" + cap_name[i - 1].strip()
    mkdir(use_path)
    download_one_two()

def download_pic1(url,i):
    try:
        response=requests.get(url,headers=header,timeout=20)
        html=response.text
        tree=etree.HTML(html)
        picurl = tree.xpath('//*[@id="ComicPic"]/@src')
        imagname = use_path + "//" + str(i) + ".jpg"
        print(picurl[0])
        response2 = requests.get(picurl[0], headers=header)
        with open(imagname, 'wb') as f:
            f.write(response2.content)
    except Exception as e:
        print("出现错误"+str(e))
        print('重新下载')
        download_pic1(url, i)

get_which_pic()
get_all_pic()
choice_pic()
get_chapter()
choice_download()
print("下载结束")
