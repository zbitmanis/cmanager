#!/usr/bin/env python3

import sys 
import re
import json
import math
import redis

import os, sys
#lib_path = os.path.abspath(os.path.join('..', '..', '..', 'lib'))
#sys.path.append(lib_path)

from   . import greq #strType,greq.APIError

class OsdView:
  def __init__(self,osd_id,weight,reweight,size,use,avail,pctuse,var,pgs,optim=0):
    self.id = osd_id
    self.name='osd.'+str(osd_id)
    self.weight = weight
    self.reweight = reweight
    self.size = size
    self.use = use
    self.avail = avail
    self.pctuse = pctuse
    self.var = var
    self.pgs = pgs
    self.optim = optim

def quick_sort(items):
        """ Implementation of quick sort """
        if len(items) > 1:
                pivot_index = len(items) // 2
                smaller_items = []
                larger_items = []
 
                for i, val in enumerate(items):
                        if i != pivot_index:
                                if val < items[pivot_index]:
                                        smaller_items.append(val)
                                else:
                                        larger_items.append(val)
 
                quick_sort(smaller_items)
                quick_sort(larger_items)
                items[:] = smaller_items + [items[pivot_index]] + larger_items


def get_redis_value(key):
    r=redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_value=r.get(key.encode('ascii'))
    if redis_value is None:
      return 0
    else:
      return redis_value

def get_json_perfomance():
   resp=greq.get_perfomance()
   if resp.status_code != 200:
       raise greq.APIError('Cannot fetch all osds: {}'.format(resp.status_code))
        
   res=[]
   print('{}'.format(resp.text))
   rows =resp.text.split('\n')
   idx=0 
   row_headers=[]
   for row in rows:
      if not row.strip() == '':
        row=re.sub(r"^\s+","",row)
        line=re.sub(r"\s+",",",row)
        items=line.split(',')
        if idx == 0:
         row_headers=line.split(',')
        else:
         astr=" "
         j=0
         rdata={}
         for item in line.split(','):
          if item != "":
           try: 
               rdata[row_headers[j]]=item
           except ValueError: 
               pass
           j+=1
         jstr=json.dumps(rdata)
         print (jstr)
        idx+=1     
  
def get_json_pgs():
   payload= {'dumpcontents':'pgs'}
   resp=greq.get_pgs(payload)
   if resp.status_code != 200:
       raise greq.APIError('Cannot fetch all osds: {}'.format(resp.status_code))
   resp_json=resp.json() 
   for item in resp_json['pg_stats']:
     print('{} {}'.format(item['pgid'], item['acting']))
      


def get_df(payload={'output_method':'plain'},print_it=True) :
   resp=greq.get_osd_df(payload=payload)
   if resp.status_code != 200:
       raise greq.APIError('Cannot fetch osd df: {}'.format(resp.status_code))
   rows =resp.text.split('\n')
   idx=0
   row_headers=[]
   result = []
   for row in rows:
      if not row.strip() == '':
        row=re.sub(r"^\s+","",row)
        line=re.sub(r"\s+",",",row)
        items=line.split(',')
        if idx == 0:
         for rh in line.split(','):
            row_headers.append(rh.replace("%","PCT"))
        else:
         astr=" "
         j=0
         rdata={}
         is_footer=False
         for item in line.split(','):
             if not item.isdigit() and j==0:
               is_footer=True
             if not is_footer:
                if item != "":
                 try:
                     svalue=''
                     if "M" in item:
                        svalue=item.replace("M","")
                     elif "k" in item:
                        svalue=item.replace("k","")
                        svalue=int(round(int(svalue)/1024))
                     elif "G" in item:
                        svalue=item.replace("G","")
                        svalue=int(round(int(svalue)/1024))
                     else :
                        svalue=item 
                     svalue_type=greq.strType(svalue)
                     if svalue_type == 'int' : 
                       rdata[row_headers[j]]=int(svalue)
                     elif svalue_type == 'float':  
                       rdata[row_headers[j]]=float(svalue)
                     else:
                       rdata[row_headers[j]]=svalue
                      
                 except ValueError:
                     pass
                 j+=1
            
         if not is_footer:
           result.append(rdata) 
        idx+=1
   if print_it:
     for el in result:
          jstr=json.dumps(el)
          print (jstr)
   return result

def get_prn_df():
    """ 
        Get sorted output 4 web printout 
    """
    osd_status=get_df(print_it=False) 
    osd_stats_list=[{} for x in range(len(osd_status))]
    for cst in osd_status:
      oid=cst['ID']
      osd_stats_list[oid]=cst 
    osds=[]
    for i  in range(len(osd_stats_list)):
      optim=get_redis_value('osd.'+str(osd_stats_list[i]['ID'])+'_optimisation')
      osd=OsdView(osd_id = osd_stats_list[i]['ID'],
              weight = osd_stats_list[i]['WEIGHT'],
              reweight = osd_stats_list[i]['REWEIGHT'],
              size = int(osd_stats_list[i]['SIZE']*1024*1024),
              use = osd_stats_list[i]['USE'] *1024*1024,
              avail = osd_stats_list[i]['AVAIL']*1024*1024,
              pctuse = osd_stats_list[i]['PCTUSE'],
              var = osd_stats_list[i]['VAR'],
              pgs = osd_stats_list[i]['PGS'],
              optim=optim )
      osds.append(osd)  
    return osds

def get_fitness_df():
    """ 
        Get sorted output 4 web printout 
    """
    osd_status=get_df(print_it=False) 
    osd_stats_list=[{} for x in range(len(osd_status))]
    for cst in osd_status:
      oid=cst['ID']
      osd_stats_list[oid]=cst 
    osd_stats=[]
    for i  in range(len(osd_stats_list)):
      optim=get_redis_value('osd.'+str(osd_stats_list[i]['ID'])+'_optimisation')
      var = osd_stats_list[i]['VAR']
      use = osd_stats_list[i]['USE']
      oid=osd_stats_list[i]['ID']
      osd_stats.append({'optim':optim,'var':var,'use':use,'id':oid})
    vl=[]   
    for os in osd_stats:
        vl.append(os['var']) 
    quick_sort(vl)
    
    """ find bigest number for nan replacement """
    maxn=0
    for v in vl:
        if maxn < v and not math.isnan(v):
           maxn=v 
    if maxn ==0 :
        maxn=5    
    s_part=[]
    l_part=[]
    pi=len(vl)//2
    for i, val in enumerate(vl):
        if i<pi:
            s_part.append(val)
        else:    
            l_part.append(val)
    
    for os in osd_stats:
        if math.isnan(os['var']):
            os['var'] = 2*maxn
            os['optim']= 1
        elif os['var'] in l_part:
            os['optim']= 1
        else:
            os['optim']= -1
           
    return osd_stats

    

def put_osd_reweight(osd_id,weight):
   resp=greq.put_osd_reweight(osd_id=osd_id,weight=weight)
   if resp.status_code != 200:
       raise greq.APIError('Cannot set osd weight osd{} weight {}  {}'.format(osd_id,weight,resp.status_code))

def set_reweights(osds,weight):
    for key  in  osds:
        put_osd_reweight(osds[key],weight)

def get_pg_stat():
    """ splits response like v2090241: 544 pgs: 544 active+clean; 10436 kB data, 673 MB used, 53368 MB / 55433 MB avail 
        v2089622: 544 pgs: 1 activating+degraded, 1 activating+remapped, 1 active+remapped+wait_backfill, 9 active+recovery_wait+degraded, 10 activating, 13 peering, 509 active+clean; 
        10436 kB data, 672 MB used, 53368 MB / 55433 MB avail; 41/1547 objects degraded (2.650%); 14/1547 objects misplaced (0.905%); 0 B/s, 1 objects/s recovering
    """
    resp=greq.get_pg_stat()
    if resp.status_code != 200:
        raise greq.APIError('Cannot fetch pg stats df: {}'.format(resp.status_code))
    pgstats={}
    citems=resp.text.split(';')[0].split(':') 
    
    pgitems=citems[1].split(' ')
    pgstats[pgitems[2]]=pgitems[1]
   
    comitems=citems[2].split(',')  
    for item in comitems:
        sitem=item.rstrip().split(' ')
        pgstats[sitem[2]]=sitem[1]
    return pgstats 
    
def obtain_chart_data():
   print ("clall greq obtain data")
   resp=greq.obtain_new_chart_data()
   if resp.status_code != 200:
       raise greq.APIError('Cannot fetch pg stats df: {}'.format(resp.status_code))
    

def get_pg_dump_stuck():
   resp=greq.get_pg_dump_stack()
   if resp.status_code != 200:
       raise greq.APIError('Cannot fetch pg stats df: {}'.format(resp.status_code))
   print (resp.text)  
   rows =resp.text.split('\n')
   
   if len(rows)==1:
        print (rows)
   else:  
       for row in rows:
            print (row) 
          
def main (argv):
#   get_json_perfomance()
#   get_json_pgs()
#   put_osd_reweight(5,0.12)
#   get_df(print_it=True)
    get_pg_dump_stuck()
    print ("pg stats") 
    get_pg_stat()
    get_df(print_it=True)
    get_fitness_df()
    obtain_chart_data() 
    
      #  tl=item.split(' ')
     #print('{} {}'.format(todo_item['id'], todo_item['summary']))
   #for l in res:
     #   print(l) 
  
  

if __name__ == '__main__':
    main(sys.argv)


