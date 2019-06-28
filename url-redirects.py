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
                    
    def run(self):
        global filename
        while  not self._queue.empty():
            url = self._queue.get()
            if 'tcpwrapped' in url:
                time_out = 3
                url = url.replace('tcpwrapped','')
            else:
                time_out = 15
            url_list = [url]

            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
            try:
                r = requests.get(url, verify=False, timeout=time_out, headers = headers)#, proxies={'http':'http://42.51.42.201:808'})
            except:
                if 'https' not in url:
                    try:
                        r = requests.get(url.replace('http','https'), verify=False, timeout=time_out, headers = headers)
                    except:
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
            with open(filename.replace('nmap','port_link'),'a',encoding='utf-8')as f:
                file_lock = lockfile.MkdirFileLock(filename.replace('nmap','port_link'))    
                while(1):
                    try:
                        file_lock.acquire()
                    except:
                        time.sleep(0.1)
                    else:
                        break
                f.write(str(url_list)+' ['+str(r.status_code)+']\n')
                file_lock.release()
                    


def main():

    ip_port_list = []
    threads = []
    Queue = queue.Queue()
    with open(filename,'r',encoding='utf-8')as f:
        context = f.readlines()
##    with open(filename.replace('nmap','ip-domain'),'r',encoding='utf-8')as f:
##        domain = f.readlines()

    for line in context:
        ip = re.findall('Nmap scan report for (.*?) \((.*?)\)\n',line)
        ip2 = re.findall('Nmap scan report for (.*?)\n',line)
            
        if ip:
            old_ip = ip[0][1]
        elif ip2:
            old_ip = ip2[0]
            
        port = re.findall('(.*?)\/tcp',line)
        if port:
##            for i in domain:
##                if old_ip in i:
##                    old_domain = i.split('/')[2]
##                    break
            
            if '443'in port[0]:
                ip_port = 'https://'+old_ip+':'+port[0]
##                domain_port = 'https://'+old_domain+':'+port[0]
            else:
                ip_port = 'http://'+old_ip+':'+port[0]
##                domain_port = 'http://'+old_domain+':'+port[0]
            if 'tcpwrapped' in line:
                ip_port = ip_port + 'tcpwrapped'
##                domain_port = ip_domain + 'tcpwrapped'
            ip_port_list.append(ip_port)
##            ip_port_list.append(domain_port)
            
##    print(len(ip_port_list))
    start_time = time.clock()
    for i in ip_port_list:
        Queue.put(i)

    for i in range(threads_count):
        threads.append(ip_port_check(Queue))	
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    return start_time

if __name__ == '__main__':
    threads_count = 200
    filename = 'output/x/x_nmap.txt'

    start_time = main()
    
    end_time = time.clock()
    print ("Cost time is %f" % (end_time - start_time))
