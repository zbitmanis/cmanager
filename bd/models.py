from django.db import models
from django.utils import timezone



class OsdStatusManager(models.Manager):
    def create_osdstatus(osd,weight,reweight,size,use,avial,var,pgs):
          osdstatus=self.create(osd=osd,weight=weight,reweight=reweight,size=size,use=use,avial=avial,var=var,pgs=pgs)
          return osdstatus

class OsdManager(models.Manager):
    def create_osd(self,aosd_nbr,descr):
      if not descr is None:
        osd=self.create(osd_nbr=osd_nbr)
      else:  
        osd=self.create(osd_nbr=aosd_nbr)
      return osd

class Osd(models.Model):
  OPTIMISATION_CHOICES = ((0,'Auto'),(1,'Up'),(2,'Down'))
  osd_nbr=models.IntegerField()
  last_active= models.DateTimeField(default=timezone.now)
  descr = models.SlugField(max_length=50)
  status =models.SlugField(max_length=50)
  optimisation = models.IntegerField(choices=OPTIMISATION_CHOICES,default=0)  
  optim_pct = models.IntegerField(default=-1)  
#  objects = OsdManager()

class OsdStatsObtained(models.Model):
  obtained =models.DateTimeField(default=timezone.now)

class OsdStats(models.Model):
  obtained =models.ForeignKey(OsdStatsObtained)
  weight_osd0 = models.DecimalField(max_digits=6, decimal_places=5)
  reweight_osd0 = models.DecimalField(max_digits=6, decimal_places=5)
  size_osd0 =models.IntegerField()
  use_osd0 =models.IntegerField()
  pctuse_osd0 = models.DecimalField(max_digits=6,decimal_places=2)
  avail_osd0 =models.IntegerField()
  var_osd0  = models.DecimalField(max_digits=4, decimal_places=2)
  pgs_osd0=models.IntegerField()
  weight_osd1 = models.DecimalField(max_digits=6, decimal_places=5)
  reweight_osd1 = models.DecimalField(max_digits=6, decimal_places=5)
  size_osd1 =models.IntegerField()
  use_osd1 =models.IntegerField()
  pctuse_osd1 = models.DecimalField(max_digits=6,decimal_places=2)
  avail_osd1 =models.IntegerField()
  var_osd1  = models.DecimalField(max_digits=4, decimal_places=2)
  pgs_osd1=models.IntegerField()
  weight_osd2 = models.DecimalField(max_digits=6, decimal_places=5)
  reweight_osd2 = models.DecimalField(max_digits=6, decimal_places=5)
  size_osd2 =models.IntegerField()
  use_osd2 =models.IntegerField()
  pctuse_osd2 = models.DecimalField(max_digits=6,decimal_places=2)
  avail_osd2 =models.IntegerField()
  var_osd2  = models.DecimalField(max_digits=4, decimal_places=2)
  pgs_osd2=models.IntegerField()
  weight_osd3 = models.DecimalField(max_digits=6, decimal_places=5)
  reweight_osd3 = models.DecimalField(max_digits=6, decimal_places=5)
  size_osd3 =models.IntegerField()
  use_osd3 =models.IntegerField()
  pctuse_osd3 = models.DecimalField(max_digits=6,decimal_places=2)
  avail_osd3 =models.IntegerField()
  var_osd3  = models.DecimalField(max_digits=4, decimal_places=2)
  pgs_osd3=models.IntegerField()
  weight_osd4 = models.DecimalField(max_digits=6, decimal_places=5)
  reweight_osd4 = models.DecimalField(max_digits=6, decimal_places=5)
  size_osd4 =models.IntegerField()
  use_osd4 =models.IntegerField()
  pctuse_osd4 = models.DecimalField(max_digits=6,decimal_places=2)
  avail_osd4 =models.IntegerField()
  var_osd4  = models.DecimalField(max_digits=4, decimal_places=2)
  pgs_osd4=models.IntegerField()
  weight_osd5 = models.DecimalField(max_digits=6, decimal_places=5)
  reweight_osd5 = models.DecimalField(max_digits=6, decimal_places=5)
  size_osd5 =models.IntegerField()
  use_osd5 =models.IntegerField()
  pctuse_osd5 = models.DecimalField(max_digits=6,decimal_places=2)
  avail_osd5 =models.IntegerField()
  var_osd5  = models.DecimalField(max_digits=4, decimal_places=2)
  pgs_osd5=models.IntegerField()



class GenStats(models.Model):
  generation =models.IntegerField()
  attempt =models.IntegerField()
  created =models.DateTimeField(default=timezone.now)
  avg = models.DecimalField(max_digits=6,decimal_places=2)
  max = models.DecimalField(max_digits=6,decimal_places=2)
  sum = models.DecimalField(max_digits=6,decimal_places=2)

