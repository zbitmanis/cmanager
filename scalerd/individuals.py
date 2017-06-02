#!/usr/bin/env python3 


"""
   Copyright 2017 Andris Zbitkovskis

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import sys
import math 
from types import *

class Individual:
    def d_convert (self,bin_number,byte_size=None):
        if byte_size is None:
            byte_size=self.byte_size    
        res=0;
        for i in reversed(range(byte_size)):
            res+=2**(byte_size-i-1)*bin_number[i]
        return res   

    def b_convert (self,dec_number,byte_size=None):
        if byte_size is None:
            byte_size=self.byte_size    
        
        i=byte_size-1
        res=[0]*byte_size
        dec_number = int(dec_number)
        while dec_number > 0:
            rem = dec_number % 2
            res[i] = rem
            i-=1
            dec_number = dec_number // 2
        return res


    def set_i(self,aw,idx):
        w,k =aw
        self.weights[idx]['weight']=w
        self.weights[idx]['idx']=k
        self.weights[idx]['binary']=self.b_convert(k)
    
    def theoretical_fitness(sefl,args):
        sum_of_pw=0.0
        for a in args:
            sum_of_pw+=math.pow(float(a),2.0)
        sxy2=math.sqrt(sum_of_pw)
        res=0.5+math.cos(2*sxy2)/(1+sxy2)
        return round(res,2)

    def str_binary_rep(self):
        res=""
        i=0
        for b in self.b_rep:
            if i%self.byte_size ==0  and i !=0 :
                res+=" "
            res+=str(b)
            i+=1
        return res 
            
    def recalc_fitness(self):
        wargs=[]
        for w in self.weights:
            wargs.append(w['weight'])
        #self.fitness=self.fitness_func(wargs)
        self.fitness=self.theoretical_fitness(wargs)
 
    def __init__(self,aweights,byte_size):
        self.b_rep=[]
        self.byte_size=byte_size
        self.weights = [{} for x in range(len(aweights))]
        i=0 
        for w, k  in aweights:
            self.weights[i]['weight']=w
            self.weights[i]['idx']=k
            self.weights[i]['binary']=self.b_convert(k)
            i+=1
            self.size=i
            
        for w in self.weights:
            self.b_rep+=w['binary']
        self.fitness=0
        self.mutate=False
        self.must_recalc=False
            


def main(argv):
    w=[(0.2,3) , (0.0,4) ,(0.4,8) ]    
    ind =  Individual (w,5)
    sbr=ind.str_binary_rep()
    print (sbr) 

if __name__ == '__main__':
    main(sys.argv)


