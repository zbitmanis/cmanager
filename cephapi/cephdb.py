#!/usr/bin/env python

import  cephapi 

import sys
import math
import json 


from django.conf import settings
from bd.models import  OsdStatsObtained,OsdStats, GenStats
from bd.utils import receive_gen_stat 

def decode_stats(osd_id,stats_name,maxvar):
  pass

def refresh_osd_status():
  osd_status=cephapi.get_df()
  osdlen=len(osd_status)
  osd_stats_list=[{} for x in range(osdlen)]
  osd_vars=[0 for x in range(osdlen)]
  max_var = 0
  
  for cst in osd_status:
      if  not math.isnan(cst['VAR']) and  max_var < cst['VAR'] :
          max_var = cst['VAR']  
        
  for cst in osd_status:
      oid=cst['ID']
      if  math.isnan(cst['VAR']):
        cst['PCTUSE'] =0 
        cst['VAR'] =2 * max_var
  
      osd_stats_list[oid]=cst

  oso=OsdStatsObtained.objects.create()
  oso.save()
  ostats=OsdStats.objects.create( obtained = oso,
                                  weight_osd0 = osd_stats_list[0]['WEIGHT'],
                                  reweight_osd0 = osd_stats_list[0]['REWEIGHT'],
                                  size_osd0 = osd_stats_list[0]['SIZE'],
                                  use_osd0 = osd_stats_list[0]['USE'],
                                  pctuse_osd0 = osd_stats_list[0]['PCTUSE'],
                                  avail_osd0 = osd_stats_list[0]['AVAIL'],
                                  var_osd0  = osd_stats_list[0]['VAR'],
                                  pgs_osd0= osd_stats_list[0]['PGS'],
                                  weight_osd1 = osd_stats_list[1]['WEIGHT'],
                                  reweight_osd1 = osd_stats_list[1]['REWEIGHT'],
                                  size_osd1 = osd_stats_list[1]['SIZE'],
                                  use_osd1 = osd_stats_list[1]['USE'],
                                  pctuse_osd1 = osd_stats_list[1]['PCTUSE'],
                                  avail_osd1 = osd_stats_list[1]['AVAIL'],
                                  var_osd1  = osd_stats_list[1]['VAR'],
                                  pgs_osd1= osd_stats_list[1]['PGS'],
                                  weight_osd2 = osd_stats_list[2]['WEIGHT'],
                                  reweight_osd2 = osd_stats_list[2]['REWEIGHT'],
                                  size_osd2 = osd_stats_list[2]['SIZE'],
                                  use_osd2 = osd_stats_list[2]['USE'],
                                  pctuse_osd2 = osd_stats_list[2]['PCTUSE'],
                                  avail_osd2 = osd_stats_list[2]['AVAIL'],
                                  var_osd2  = osd_stats_list[2]['VAR'],
                                  pgs_osd2= osd_stats_list[2]['PGS'],
                                  weight_osd3 = osd_stats_list[3]['WEIGHT'],
                                  reweight_osd3 = osd_stats_list[3]['REWEIGHT'],
                                  size_osd3 = osd_stats_list[3]['SIZE'],
                                  use_osd3 = osd_stats_list[3]['USE'],
                                  pctuse_osd3 = osd_stats_list[3]['PCTUSE'],
                                  avail_osd3 = osd_stats_list[3]['AVAIL'],
                                  var_osd3  = osd_stats_list[3]['VAR'],
                                  pgs_osd3= osd_stats_list[3]['PGS'],
                                  weight_osd4 = osd_stats_list[4]['WEIGHT'],
                                  reweight_osd4 = osd_stats_list[4]['REWEIGHT'],
                                  size_osd4 = osd_stats_list[4]['SIZE'],
                                  use_osd4 = osd_stats_list[4]['USE'],
                                  pctuse_osd4 = osd_stats_list[4]['PCTUSE'],
                                  avail_osd4 = osd_stats_list[4]['AVAIL'],
                                  var_osd4  = osd_stats_list[4]['VAR'],
                                  pgs_osd4= osd_stats_list[4]['PGS'],
                                  weight_osd5 = osd_stats_list[5]['WEIGHT'],
                                  reweight_osd5 = osd_stats_list[5]['REWEIGHT'],
                                  size_osd5 = osd_stats_list[5]['SIZE'],
                                  use_osd5 = osd_stats_list[5]['USE'],
                                  pctuse_osd5 = osd_stats_list[5]['PCTUSE'],
                                  avail_osd5 = osd_stats_list[5]['AVAIL'],
                                  var_osd5  = osd_stats_list[5]['VAR'],
                                  pgs_osd5= osd_stats_list[5]['PGS'] )
 
  ostats.save() 
  refresh_generation_stats(attempt = 1)


def refresh_generation_stats(attempt  ,host=settings.AMQP_HOST, user=settings.AMQP_USER, password=settings.AMQP_PASSWORD):
   res= receive_gen_stat(host, user, password)
   while not res is None:
        jresult=json.loads(res)
        gstats=GenStats.objects.create(generation= jresult['generation'],
                                                            avg=jresult['avg'], 
                                                            max=jresult['max'], 
                                                            sum=jresult['sum'] ,
                                                            attempt=jresult['attempt'])
        gstats.save()
        res= receive_gen_stat(host, user, password)
 

 
