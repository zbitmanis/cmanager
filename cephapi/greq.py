import requests

class APIError(Exception):

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)

def strType(var):
    try:
        if int(var) == float(var):
            return 'int'
    except:
        try:
            float(var)
            return 'float'
        except:
            return 'str'

def _url(request):
   baseurl='http://172.28.57.97:5000/api/v0.1/'
   return baseurl+request

def _durl(request):
   baseurl='http://172.28.57.129:8000'
   return baseurl+request

def get_perfomance():
  rurl=_url('osd/perf')
  print (" url {} ".format (rurl))
  return requests.get(rurl)

def get_pgs():
  rurl=_url('osd/perf')
  print (" url {} ".format (rurl))
  return requests.get(rurl)

def get_pgs(payload):
  rurl=_url('pg/dump_json')
  return requests.get(rurl,params=payload)

def get_pg_stat():
  rurl=_url('pg/stat')
#  print (" url {} ".format (rurl))
  return requests.get(rurl)

def get_pg_stat():
  rurl=_url('pg/stat')
  return requests.get(rurl)

def get_pg_dump_stack():
  rurl=_url('pg/dump_stuck')
  return requests.get(rurl)

def get_osd_df(payload={'output_method':'plain'}):
   #http://localhost:5000/api/v0.1/osd/df?output_method=plain
  rurl=_url('osd/df')
  return requests.get(rurl,params=payload)

def put_osd_reweight(osd_id,weight):
  data={'id':osd_id,  'weight':weight }  
  rurl=_url('osd/reweight'+'?id='+str(osd_id)+'&weight='+str(weight))
  return requests.put(rurl,data={})

def obtain_new_chart_data():
  rurl=_durl('/obtain_new_chart_data/')
  return requests.get(rurl)

def osd_out(osd_id):
 rurl=_url('osd/out?id='+str(osd_id))
 return requests.put(rurl,data={})

def osd_in(osd_id):
 rurl=_url('osd/in?id='+str(osd_id))
 return requests.put(rurl,data={})

