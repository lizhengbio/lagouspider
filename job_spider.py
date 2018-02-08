#coding:utf-8

import urllib2
import cookielib
import urllib
import ssl
import json
import time
import xlsxwriter
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class job_spider:
    def __init__(self):
        self.url = "https://www.lagou.com/jobs/positionAjax.json"
        self.word={"city":"深圳"}
        self.keyword = "python"

    def read_page(self,url,page_num):
        page_headers = {
            'Host':'www.lagou.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Referer':'https://www.lagou.com/jobs/list_Python?px=default&city=%E6%B7%B1%E5%9C%B3',
            'Connection':'keep-alive'
        }
        if page_num == 1:
            boo = 'true'
        else:
            boo = 'false'
        formdata = {
            "first":boo,
            "pn":page_num,
            "kd":self.keyword
        }
        page_data = urllib.urlencode(formdata)
        context = ssl._create_unverified_context()
        req = urllib2.Request(url,data=page_data.encode('utf-8'),headers = page_headers)
        page = urllib2.urlopen(req,context=context).read().decode('utf-8')
        return page

    def read_tag(self,page,tag):
        page_json = json.loads(page)
        print page_json
        page_json =page_json['content']['positionResult']['result']
        page_result = [num for num in range(15)]  # 构造一个容量为15的list占位，用以构造接下来的二维数组
        for i in range(15):
            page_result[i] = []  # 构造二维数组
            for page_tag in tag:
                page_result[i].append(page_json[i].get(page_tag))  # 遍历参数，将它们放置在同一个list当中
            page_result[i][3] = ','.join(page_result[i][3])
        return page_result #返回当前页的招聘信息

    def read_max_page(self,page): #获取当前招聘关键词的最大页数
        page_json = json.loads(page)
        totalcount = page_json['content']['positionResult']['totalCount']
        pageSize = page_json['content']['pageSize']
        if int(totalcount)%int(pageSize) != 0:
            max_page_num = int(totalcount)/int(pageSize) + 1
        else:
            max_page_num = int(totalcount)/int(pageSize)
        return max_page_num

    def save_excel(self,fin_result,tag_name,file_name): #将抓取的招聘信息存储到excel中
        book = xlsxwriter.Workbook(file_name+".xlsx")
        tmp = book.add_worksheet()

        row_num = len(fin_result)
        for i in range(row_num):
            if i == 0:
                tag_pos = 'A1'
                tmp.write_row(tag_pos,tag_name)
            else:
                con_pos = 'A%s' %(i+1)
                content = fin_result[i-1]
                tmp.write_row(con_pos,content)
        book.close()


if __name__ == "__main__":
    city = raw_input("请输入搜索城市：")
    job = job_spider()
    url = job.url
    job.word = {"city":city}
    job.keyword = raw_input("请输入编程语言：")
    word = urllib.urlencode(word)
    newurl = url + "?" + job.word
    fin_result = []
    max_page_num = job.read_max_page(job.read_page(newurl,1))
    tag = ['companyFullName', 'companyShortName', 'district', 'companyLabelList','secondType','companySize','financeStage','industryField','positionAdvantage','salary','workYear']  #这里是需要抓取的标签信息
    tag_name = ['公司全称','公司简称','行政区','公司介绍','二级类别','公司规模','融资阶段','公司领域','职位诱惑','工资','工作年限']
    for page_num in range(1,max_page_num):
        print '**********************正在下载第%s页内容********************' %page_num
        time.sleep(30)
        page = job.read_page(newurl,page_num)
        page_result = job.read_tag(page,tag)
        fin_result.extend(page_result)
    file_name = raw_input('抓取完成，请输入文件名保存：')
    job.save_excel(fin_result,tag_name,file_name)
