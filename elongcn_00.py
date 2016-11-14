# -*- coding: utf-8 -*-#
'''
# writen by jingjun.gu@qq.com
#    copyright by 2013-2013
#
# function:
#    1.scan the non-auto bid from www.
#    2.alarm user
#    3.open one new table in default web-browser
'''


import cStringIO
import getopt
import re
import time
import urllib2
import subprocess
import sys
from datetime import datetime
import winsound
import webbrowser

PROXY_USE = 0
BID_URL = 'http://www.eloancn.com/loan/loadAllTender.action?index=1&sidx=publisheddate&sord=desc'
BID_VER = '00'

REF_PRICE = 20
MAX_PRICE = 99

g_para1 = 'none'
g_para2 = 0
g_para3 = 0
g_para4 = 0
g_para5 = 0
g_his_para1 = 'none'
g_his_para2 = 0
g_his_para3 = 0
g_his_para4 = 0
g_his_para5 = 0


g_link = 'none'
g_open = 0

MEDIA_FILE = 'audio.wav'

def get_first_bid():

    global g_para1, g_para2, g_para3, g_para4, g_para5

    g_para1 = 'none'
    g_para2 = 0
    g_para3 = 0
    g_para4 = 0
    g_para5 = 0
    
    if PROXY_USE:
        proxy_support = urllib2.ProxyHandler({"http":"http://10.144.1.10:8080"})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

    try:
        content = urllib2.urlopen(BID_URL).read()
    except:
        print 'HTTP ERR',
        return g_his_para2

    buf = cStringIO.StringIO(content)
    state = 0

    '''
    <a href="http://www.eloancn.com:80/loan/loandetail.action?tenderid=11351" title="点击查看标详情" class="lend_link" target="_blank">二次贷款。。。</a>
    ￥70,000.00 利率: 
    20.00%
    期限: 10个月
    进度: 100.0%&nbsp;&nbsp;
    '''

    #http://www.herodai.com/touzi/detail.html?borrowid=1046
    
    ore = re.compile(u'.+?tenderid=(\d+)', re.X)
    i=0
    for line in buf:
        line = line.strip('\n\r')
        linecn = line.decode('utf8')  
        i = i + 1
        om = ore.match(linecn)
        if om:
            if (state == 0):
                g_para1 = om.group(1)
                #print linecn,'--------',i,':',g_para1
                state = 1
                ore = re.compile(u'.+?(\d+).00%', re.X)   
            elif (state == 1):
                g_para2 = om.group(1)
                #print linecn,'--------',i,':',g_para2
                state = 2
                ore = re.compile(u'.+?(\d+)个月', re.X)               
            elif (state == 2):
                g_para3 = om.group(1)
                #print linecn,'--------',i,':',g_para3
                state = 3
                ore = re.compile(u'.*进度: .+?(\d+)', re.X)
            elif (state == 3):
                g_para4 = om.group(1)
                #print linecn,'--------',i,':',g_para4
                state = 0
                ore = re.compile(u'.+?tenderid=(\d+)', re.X)
                break               
    buf.close()   
    return 0
    
def notify():
    
    #subprocess.Popen([MEDIA_PLAYER, MEDIA_FILE])
    
    global g_open, g_para5

    try:
        winsound.PlaySound(MEDIA_FILE, winsound.SND_ASYNC)
    except:
        print 'winsound exception\n\r'

    print 'FOUND!!\n\r'

    if (g_open == 0):
        try:
            res = webbrowser.open_new_tab("http://www.eloancn.com:80/loan/loandetail.action?tenderid="+g_para1)
            if (res == true):
                g_open = 1
            else:
                res = webbrowser.open_new("http://www.eloancn.com:80/loan/loandetail.action?tenderid="+g_para1)
                if (res == true):
                    g_open = 1                    
        except:
            print 'webbrowser exception\n\r'
            g_open = 1;
    return           
 

def monitor_bid():

    global g_interval
    global g_para1, g_para2, g_para3, g_para4
    global g_his_para1, g_his_para2, g_his_para3, g_his_para4
    global g_open

    while (1):
        
        result = get_first_bid()

        if (g_para1 <> g_his_para1) or (g_para2 <> g_his_para2) or (g_para3 <> g_his_para3) or (g_para4<> g_his_para4) or (g_para5 <> g_his_para5):
            now = datetime.now()
            print '\n\rTIME:', now.hour,':',now.minute,':',now.second, '(', 'link=', g_para1, g_para2, g_para3, g_para4, ')'
            g_his_para1 = g_para1
            g_his_para2 = g_para2
            g_his_para3 = g_para3
            g_his_para4 = g_para4
            g_his_para5 = g_para5
        else:
            print '.',

        if ( int(g_para2) == 20) and ( int(g_para3) < 4) and ( int(g_para4) < 100):
            g_interval = 5
            notify()
        else:
            g_interval = 1
            g_open = 0
            
        time.sleep(g_interval)
   

def usage():
    print \
    '''
    usage: monitor_mac_price.py [options] Options:
    -i interval: 1 seconds by default.
    -l last: 24H by default.
    -h: Print this usage.
    '''

if __name__ == '__main__':

    print "monitor started "+BID_URL+" "+BID_VER
    
    g_interval = 1
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:l:h')
    except getopt.GetoptError, err:
        sys.exit(1)

    for opt, val in opts:
        if opt == '-i':
            MONI_INTERVAL = int(val)
        elif opt == '-l':
            MONI_PEROID = int(val)
        elif opt == '-h':
            usage()
            sys.exit()

    monitor_bid()
