import threading, queue
import re, time, requests, os, lockfile
from readability import Document
#from bs4 import BeautifulSoup
from requests.packages import urllib3
urllib3.disable_warnings()

class ip_port_check(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self._queue = queue
        
    def url_redirects(self,r,url_list):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
##        try:
##            url = requests.get(url, allow_redirects=False, verify=False, timeout=5, headers = headers).headers.get('location')
##        except:
##            pass
##        else:
##            if (url not in url_list) and url:
##                url_list.append(url)
##                self.url_redirects(url,url_list)
##                return url_list
##            else:
##                return url_list

        try:
            url = r.url
        except:
            return url_list
        else:
            if url[-1] == '/':
                url = url[:-1]
                
            if url not in url_list:
                url_list.append(url)
            return url_list

    def lock_file(self,filename,text):
        with open(filename,'a',encoding='utf-8')as f:
            file_lock = lockfile.MkdirFileLock(filename)    
            while(1):
                try:
                    file_lock.acquire()
                except:
                    time.sleep(0.1)
                else:
                    break
            f.write(text)
            file_lock.release()
                    
    def run(self):
        global filename, time_out
        while  not self._queue.empty():
            url = self._queue.get().strip()
            url_list = [url]

            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
            try:
                r = requests.get(url, verify=False, timeout=time_out, headers = headers)
            except:
                if 'https://' not in url:
                    try:
                        r = requests.get(url.replace('http://','https://'), verify=False, timeout=time_out, headers = headers)
                    except:
                        self.lock_file(filename.replace('.txt','.pass.txt'),url+'\n')
                        continue
                else:
                    continue
##            else:
##                if r.status_code//100 > 4:
##                    continue
            
            url_list = self.url_redirects(r,url_list)
##            if url_list:
            try:
                html = r.content
##                if not html:
##                    continue
                url_list.append(Document(html).title())                
                #url_list.append(Document(requests.get(requests.get(url, verify=False, headers = headers).url, verify=False, timeout=10, headers = headers).text).title())
                #url_list.append(BeautifulSoup(requests.get(url, verify=False, timeout=10, headers = headers).text.encode('iso-8859-1').decode('utf-8'), 'lxml').title.string)
            except:
                pass
                
            print(url_list)
            self.lock_file(filename.replace('.txt','.port_link.txt'),str(url_list)+' ['+str(r.status_code)+']\n')
            self.lock_file(filename.replace('.txt','.pass.txt'),url+'\n')
                    


def main():

    domain_list = []
    threads = []
    Queue = queue.Queue()
    #1
##    with open(filename.replace('.txt','.pass.txt'),'r',encoding='utf-8')as f:
##        pass_list = f.readlines()
##        pass_len = len(set(pass_list))
##        
##    with open(filename,'r',encoding='utf-8')as f:
##        task_list_all = f.readlines()
##        task_len = len(set(task_list_all))
##        
##    domain_list = list(set(task_list_all) - set(pass_list))
##    
##    print('任务进度：'+str(pass_len)+'/'+str(task_len)+' '+str(int(pass_len/task_len*10000)/100)+'%')
    
    #2
    with open(filename,'r',encoding='utf-8')as f:
        domain_list = f.readlines()
            
                
    start_time = time.clock()
    for i in domain_list:
        Queue.put(i)

    for i in range(threads_count):
        threads.append(ip_port_check(Queue))	
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    return start_time

if __name__ == '__main__':
    threads_count = 200#线程数
    time_out = 30
    filename = 'C:/Users/liulangmao/Desktop/16992'#文件名

    start_time = main()
    
    end_time = time.clock()
    print ("Cost time is %f" % (end_time - start_time))
