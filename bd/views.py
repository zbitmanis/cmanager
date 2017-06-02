from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from utils import set_redis_value, make_amqp_call

from chartit import DataPool,Chart
from .models import OsdStats,Osd, GenStats
from .forms import LoginForm,ChangePasswordForm,ReweightOsdForm,ChartForm
import django.contrib.auth as dauth

import cephapi.cephdb as cephdb
from  cephapi.cephapi   import put_osd_reweight,get_prn_df

    

    
def login(request):
    request.session.flush()
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        name=reverse(login)
        try:
            user = dauth.authenticate(username=username,password=password)
            if user is not None:
              if user.is_active:
                dauth.login(request, user)
                request.session['username'] = username
                request.session['admin'] = False
                messages.add_message(request, messages.INFO, _("Login successfully."))
                return redirect(osd_stats)
              else:
                messages.add_message(request, messages.ERROR, _("Disabled"))
            else:
              messages.add_message(request, messages.ERROR, _("Ups"))

        except client.ClientException:
            messages.add_message(request, messages.ERROR, _("Login failed."))

    return render(request,'login.html', {'form': form, },context_instance=RequestContext(request))

def change_password(request ):
    form = ChangePasswordForm(request.POST or None)
    has_errors = False
    if form.is_valid():
        pass
#        oldpassword = form.cleaned_data['oldpassword']
#        password = form.cleaned_data['password']
#        verifypassword = form.cleaned_data['verifypassword']
        
#        if verifypassword != password :
#          has_errors =True
    return render(request,'cpassword.html', {'form': form, },context_instance=RequestContext(request))

def obtain_new_chart_data(request):
  cephdb.refresh_osd_status() 
  return redirect(osd_chart)

def reset(request):
    username = request.session.get('username', None)
    if username is None:
        return redirect(login)
    else:
      response=make_amqp_call(host=settings.AMQP_HOST, user=settings.AMQP_USER, password=settings.AMQP_PASSWORD, signal="reset")
      messages.add_message(request, messages.INFO, _(response))
      return redirect(osd_stats)

def pause(request):
    username = request.session.get('username', None)
    if username is None:
        return redirect(login)
    else:
      response=make_amqp_call(host=settings.AMQP_HOST, user=settings.AMQP_USER, password=settings.AMQP_PASSWORD, signal="pause")
      messages.add_message(request, messages.INFO, _(response))
      return redirect(osd_stats)

def start(request):
    username = request.session.get('username', None)
    if username is None:
        return redirect(login)
    else:
      response=make_amqp_call(host=settings.AMQP_HOST, user=settings.AMQP_USER, password=settings.AMQP_PASSWORD, signal="start")
      messages.add_message(request, messages.INFO, _(response))
      return redirect(osd_stats)

def status(request):
    username = request.session.get('username', None)
    if username is None:
        return redirect(login)
    else:
      response=make_amqp_call(host=settings.AMQP_HOST, user=settings.AMQP_USER, password=settings.AMQP_PASSWORD, signal="status")
      messages.add_message(request, messages.INFO, _(response))
      return redirect(osd_stats)
     
def generation_chart(request,records=None):
  form = ChartForm(request.POST or None)
  data_source=None
  if form.is_valid():
      records = form.cleaned_data['filter_choice']
  
  if not records is None: 
      if int(records) >0:
        data_source=GenStats.objects.all().order_by('-id')[:int(records)]
        form.fields['filter_choice'].initial=int(records)
      else:
        data_source=GenStats.objects.all()
  else:
    data_source=GenStats.objects.all()

  ds_rw = DataPool(
   series=
    [{'options': {
        'source': data_source},
      'terms': [
        'generation',
        'avg',
        'max',
        'sum'
          ]}
     ])

  chart_title="Generation stats"
  cht_gc = Chart(
            datasource = ds_rw, 
            series_options = 
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'generation': [
                        'avg',
                        'max',
                        'sum'
                      ]
                  }}],
            chart_options = 
              {'title': {
                   'text': chart_title },
               'xAxis': {
                    'title': {
                     'text': 'Generation'}}})
  return render(request,'genchart.html',{'charts':cht_gc,'form':form },context_instance=RequestContext(request))
                       
def osd_chart(request,records=None):
  form = ChartForm(request.POST or None)
  data_source=None
  if form.is_valid():
      records = form.cleaned_data['filter_choice']
  
  if not records is None: 
      if int(records) >0:
        data_source=OsdStats.objects.all().order_by('-id')[:int(records)]
        form.fields['filter_choice'].initial=int(records)
      else:
        data_source=OsdStats.objects.all()
  else:
    data_source=OsdStats.objects.all()
  ds_rw = DataPool(
     series=
      [{'options': {
          'source': data_source},
        'terms': [
          'obtained_id',
          'reweight_osd0',
          'reweight_osd1',
          'reweight_osd2',
          'reweight_osd3',
          'reweight_osd4',
          'reweight_osd5'
                  ]}
       ])

  ds_pgs = DataPool(
     series=
      [{'options': {
          'source': data_source},
        'terms': [
          'obtained_id',
          'pgs_osd5',
          'pgs_osd4',
          'pgs_osd3',
          'pgs_osd2',
          'pgs_osd1',
          'pgs_osd0'
                  ]}
       ])
  ds_var = DataPool(
     series=
      [{'options': {
          'source': data_source},
        'terms': [
          'obtained_id',
          'var_osd0',
          'var_osd1',
          'var_osd2',
          'var_osd3',
          'var_osd4',
          'var_osd5'
                  ]}
       ])
  ds_pctuse = DataPool(
     series=
      [{'options': {
          'source': data_source},
        'terms': [
          'obtained_id',
          'pctuse_osd0',
          'pctuse_osd1',
          'pctuse_osd2',
          'pctuse_osd3',
          'pctuse_osd4',
          'pctuse_osd5'
                  ]}
       ])
  
  chart_title="Reweight"
  cht_rw = Chart(
          datasource = ds_rw, 
          series_options = 
            [{'options':{
                'type': 'line',
                'stacking': False},
              'terms':{
                'obtained_id': [
                   'reweight_osd0',
                   'reweight_osd1',
                   'reweight_osd2',
                   'reweight_osd3',
                   'reweight_osd4',
                   'reweight_osd5'
                    ]
                }}],
          chart_options = 
            {'title': {
                 'text': chart_title },
             'xAxis': {
                  'title': {
                   'text': 'Data obtained'}}})
  
  chart_title="Placement groups"

  cht_pgs = Chart(
          datasource = ds_pgs, 
          series_options = 
            [{'options':{
                'type': 'line',
                'stacking': False},
              'terms':{
                'obtained_id': [
                   'pgs_osd5',
                   'pgs_osd4',
                   'pgs_osd3',
                   'pgs_osd2',
                   'pgs_osd1',
                   'pgs_osd0'
                    ]
                }}],
          chart_options = 
            {'title': {
                 'text': chart_title },
             'xAxis': {
                  'title': {
                   'text': 'Data obtained'}}})
  chart_title="Variance"
  cht_var = Chart(
          datasource = ds_var, 
          series_options = 
            [{'options':{
                'type': 'column',
                'stacking': False},
              'terms':{
                'obtained_id': [
                   'var_osd0',
                   'var_osd1',
                   'var_osd2',
                   'var_osd3',
                   'var_osd4',
                   'var_osd5'
                    ]
                }}],
          chart_options = 
            {'title': {
                 'text': chart_title },
             'xAxis': {
                  'title': {
                   'text': 'Data obtained'}}})
  chart_title="Usage %"
  cht_pctuse = Chart(
          datasource = ds_pctuse, 
          series_options = 
            [{'options':{
                'type': 'column',
                'stacking': False},
              'terms':{
                'obtained_id': [
                   'pctuse_osd0',
                   'pctuse_osd1',
                   'pctuse_osd2',
                   'pctuse_osd3',
                   'pctuse_osd4',
                   'pctuse_osd5'
                    ]
                }}],
          chart_options = 
            {'title': {
                 'text': chart_title },
             'xAxis': {
                  'title': {
                   'text': 'Data obtained'}}})

  return render(request,'chart.html',{'charts':[cht_rw,cht_pgs,cht_var,cht_pctuse] ,'form':form },context_instance=RequestContext(request))

def reweight_osd(request,osd_id=None,weight=None ):
    username = request.session.get('username', None)
    if username is None:
        return redirect(login)
    else:
      form = ReweightOsdForm(request.POST or None)
      is_valid=False
      if form.is_valid():
          osd_id = form.cleaned_data['osd_id']
          new_weight = form.cleaned_data['new_weight']
          is_valid=True 
          messages.add_message(request, messages.INFO, "valid osd_id  {} weight {} ".format(osd_id,weight))
      if not osd_id is None and not weight is None:
        form.fields['osd_id'].widget.attrs['disabled'] = True
        form.fields['osd_id'].initial=osd_id
        form.fields['new_weight'].initial=weight
        messages.add_message(request, messages.INFO, "not null osd_id  {} weight {} ".format(osd_id,weight))
      


      if is_valid:  
          try:
            put_osd_reweight(osd_id=osd_id,weight=new_weight)
            messages.add_message(request, messages.INFO, _("Reweigth request sent."))
            return redirect(osd_stats)
              
          except Exception as exc:
                  msg = exc.message
                  messages.add_message(request, messages.ERROR, msg)
      return render(request,'reweight.html', {'form': form, 'osd_id':osd_id , 'weight':weight },context_instance=RequestContext(request))

def osd_stats(request):
    username = request.session.get('username', None)
    if username is None:
        return redirect(login)
    else:
      try:
        osds=get_prn_df()
      except Exception as exc:
          msg = "An error ocured while getting osd stats {}" .format(exc.message) 
          messages.add_message(request, messages.ERROR, msg)
          return redirect(login)
      return render(request,'osdview.html', {'osds': osds,'session': request.session,},context_instance=RequestContext(request))
        
def set_osd_criteria(request,osd_id,optim):
  osd=Osd.objects.get(osd_nbr=osd_id)     
  osd.optimisation=optim
  osd.save()
  set_redis_value('osd.'+str(osd_id)+'_optimisation',optim)
  return redirect(osd_stats)

  

