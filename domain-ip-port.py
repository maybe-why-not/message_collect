import threading, queue
#from subprocess import Popen,PIPE 
import re, time, requests, os, lockfile, socket
 
class nmapscan(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self._queue = queue

    def file_lock(self,filename,content):
        with open(filename,'a+',encoding='utf-8') as f1:
            file_lock = lockfile.MkdirFileLock(filename)    
            while(1):
                try:
                    file_lock.acquire()
                except:
                    time.sleep(0.1)
                else:
                    break
            f1.write(content)
            file_lock.release()
 
    def run(self):
        while  not self._queue.empty():
            i = self._queue.get()
            global domain_suffix, filename, huace_ip_list, ip_list
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}

            i2 = i
            i = i.replace('http://','').replace('https://','').split(':',1)[0].split('/',1)[0]
            domain = i

#取域名文件夹名
            try:
                if i.split('.')[-2] in domain_suffix:
                    if len(i.split('.')) == 2:
                        folder = i.split('.')[-2] + '.' + i.split('.')[-1]
                    else:
                        if i.split('.')[-3] == 'www':
                            folder = i.split('.')[-2] + '.' + i.split('.')[-1]
                        else:
                            folder = i.split('.')[-3] + '.' + i.split('.')[-2] + '.' + i.split('.')[-1]
                else:
                    if not re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', i):
                        folder = i.split('.')[-2] + '.' + i.split('.')[-1]
                    else:
                        folder = i
            except:
                print('错误 '+i)
                continue
#ip确认
            if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', i):
                ip = i
            else:
##                command = 'ping -n 1 ' + i
##                try:
##                    ip = re.search(r'\[(.*?)\]',os.popen(command).read()).group(0).strip('[]')
                try:
                    ip = socket.gethostbyname(i)
                except:
                    self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_流程记录.txt','[IP not found] '+i2+'\n')
                    print('[IP not found] '+i2)
                    continue

            self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_ip-domain.txt',folder+'\t\t'+ip+'\t\t'+i2+'\n')

            if ip not in ip_list:
                ip_list.append(ip)
                self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_ip.txt',ip+'\n')

#状态码确认
            try: 
                r = requests.get(i2, headers = headers, timeout = 30)#, proxies={'http':'http://x.x.95.35:9001'})
            except:
                try:
                    if 'http://' in i2:
                        i3 = i2.replace('http://','https://')
                    else:
                        i3 = i2.replace('https://','http://')
                    r = requests.get(i3, headers = headers, timeout = 30)
                except:
                    print ('[待确认：timeout or refuse or reset] ' + i3)
                    self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_流程记录.txt','[待确认：timeout or refuse or reset] ' + i2+'\n')
                else:
                    print ('[' + str(r.status_code) + '] ' + i3)
                    self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_流程记录.txt','[' + str(r.status_code) + '] ' + i3+'\n')
                    if (r.status_code != 302) and (r.status_code != 200):
                        continue
            else:
                print ('[' + str(r.status_code) + '] ' + i2)
                self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_流程记录.txt','[' + str(r.status_code) + '] ' + i2+'\n')
                if (r.status_code != 302) and (r.status_code != 200):
                    continue

            self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_domain.txt',i2+'\n')

            if ip not in huace_ip_list:
                huace_ip_list.append(ip)
                self.file_lock('output'+('/'+filename.replace('.txt',''))*2+'_huace_ip.txt',ip+'\n')


def main():

    threads = []
    Queue = queue.Queue()
    with open('domain_suffix.txt','r')as f:
        domain_suffix_list = f.readlines()
        for i in domain_suffix_list:
            domain_suffix.append(i.strip())
    with open(filename,'r',encoding='utf-8')as f:
        domain_link = f.readlines()
    start_time = time.clock()
    for i in domain_link:
        i = i.strip()
        Queue.put(i)

    for i in range(threads_count):
        threads.append(nmapscan(Queue))	
    for i in threads:
        i.start()
    for i in threads:
        i.join()

    cwd = os.getcwd()+'\\output'+('\\'+filename.replace('.txt',''))*2
    print('nmap.exe -Pn -T3 -sV -sS -p- --min-hostgroup 20 -iL '+cwd+'_ip.txt'+' -oN '+cwd+'_nmap.txt')
    print('nmap.exe -Pn -T3 -sV -sS -p- --min-hostgroup 20 -iL '+cwd+'_huace_ip.txt'+' -oN '+cwd+'_huace_nmap.txt')
    print('----------域名分类完毕---------')
    with open(filename,'a+',encoding='utf-8') as f1:
        f1.write('\nnmap.exe -Pn -T3 -sV -sS -p- --min-hostgroup 20 -iL '+cwd+'_ip.txt'+' -oN '+cwd+'_nmap.txt\n')#--allports
        f1.write('\nnmap.exe -Pn -T3 -sV -sS -p- --min-hostgroup 20 -iL '+cwd+'_huace_ip.txt'+' -oN '+cwd+'_huace_nmap.txt')
    return start_time

if __name__ == '__main__':
    threads_count = 200
    filename = 'x.txt'
    
    ip_list = []    
    huace_ip_list = []
    domain_suffix = []

    if not(os.path.exists('output/'+filename.replace('.txt',''))):
        os.makedirs('output/'+filename.replace('.txt',''))
    with open('output'+('/'+filename.replace('.txt',''))*2+'_link.txt','a+',encoding='utf-8') as f1:
        pass
    with open('output'+('/'+filename.replace('.txt',''))*2+'_sql_test_pass.txt','a+',encoding='utf-8') as f1:
        pass
    
    start_time = main()
    
    end_time = time.clock()
    print ("Cost time is %f" % (end_time - start_time))
