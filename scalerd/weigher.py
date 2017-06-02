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

import math
import time 
import threading
import requests
import json
import pika
import random 
from pika.exceptions import * 

from individuals import Individual 
from population import Population
from weigherstate  import WeigherState
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from  cephapi.cephapi  import put_osd_reweight,get_fitness_df,get_pg_stat


class Weigher (threading.Thread):
#class Weigher ():
    DELAY=5
    def get_rnd(self):
        if self.use_random:
          return (random.random()) 
        else:
          self.current_random_idx+=1
          if self.current_random_idx >=len(self.random_values):
                  self.current_random_idx=0
          return (self.random_values[self.current_random_idx])

    def read_random_values(self):
        with open(self.random_file_name,'r') as f:
                res=[]
                for row in f:
                    res+=row.rstrip('\n').split(' ')    
        f.close()
        r=[]    
        for s in res:
            r.append(float(s))
        return r 
     
    def get_universe_index(self,a_rnd):
        res=math.floor(float(a_rnd*(self.universe_size+1)))
        return res 

    def get_new_memebers(self):
        t_selecion=[]
        while  len(t_selecion) <(self.pop_size*self.osd_count) :
            i=self.get_universe_index(self.get_rnd())
            t_selecion.append(i)   

        #Get initial population 
        src_individuals=[]
        for pi in range(self.pop_size):
            " get touples for population"    
            weights=[]
            for oi in range (self.osd_count):
                xi=t_selecion[pi+oi*self.pop_size]
                #Universe satur tikai vienu svaru tuple
                w=self.universe[xi].weights[0]    
                weights.append((w['weight'],w['idx']))
            ind=Individual(weights,self.byte_size)
            src_individuals.append(ind) 
        return src_individuals
    
    def init_population(self):
        src_individuals=self.get_new_memebers()
        self.current_pop.init_population(src_individuals) 
        
        self.logger.debug (" state {}".format(self.state))
        
        
    def set_weights(self,inds, inspect_ind =False):
        for ind in inds:
            if not inspect_ind or ind.must_recalc:
                self.logger.debug("setting weights for {} ".format(ind.str_binary_rep()))
                if self.is_physical_model:
                    for i,val in enumerate(ind.weights):
                         put_osd_reweight(i,val['weight'])
                    cidx=0
                    pgstat=get_pg_stat()
                    while pgstat['active+clean'] != pgstat['pgs'] and cidx < self.max_cidx :
                        pgstat=get_pg_stat()
                        cidx+=1
                        self.logger.debug("going to sleep for {}.time  {} ".format(cidx,ind.str_binary_rep()))
                        time.sleep(10)
                        
                    ind_stats=get_fitness_df()
                    self.obtain_chart_data()
                    fitness=0 
                    for ist in ind_stats:
                        fitness+=ist['var']*ist['optim'] 
                    ind.fitness=fitness
                else:
                    ind.recalc_fitness()
                    
    
    def select_individuals(self,s_individuals=None):
            ng_individuals=[]
            curr_pop=self.pops[self.current_pop_idx]
            pop_size=self.pop_size

            if s_individuals is None:
                s_individuals=curr_pop.individuals
                
            curr_pop.init_roulette(verbose=False,a_inds=s_individuals)
            max_fit=-9999
            max_ind=None
            max_id=""
            for i in range(len(s_individuals)):
                ind=s_individuals[i]
                if ind.fitness>max_fit:
                    max_fit=ind.fitness
                    max_ind=ind
                    max_id=i
            #elitisms ari X
            t_ind= self.get_ind_copy(max_ind)
            t_ind.fitness=max_ind.fitness
            t_ind.p_id=max_id
            ng_individuals.append(t_ind)
            for i in range(pop_size-1):
                rnd=self.get_rnd()
                idx=curr_pop.get_chosen_idx(rnd)
                t_ind=self.get_ind_copy(s_individuals[idx]) 
                ng_individuals.append(t_ind)
            return ng_individuals
    
    def select_for_crossover(self):
        if self.current_pop_idx >0 and self.continuous_add_new_individuals :
            src_individuals=self.get_new_memebers()
            self.current_pop.init_population(src_individuals,self.current_pop.selection_source)
            self.set_weights(self.current_pop.selection_source)
            self.current_pop.print_ind(self.current_pop.selection_source,prefix="POP {} newin".format(self.current_pop_idx),filename=self.log_file)
            self.current_pop.selection_source=self.current_pop.selection_source+self.current_pop.individuals
            newinds=self.select_individuals(self.current_pop.selection_source)
        else:
            newinds=self.select_individuals()
        self.current_pop.init_population(newinds,self.current_pop.selection)
        
    def refresh_osd():
        pass
        
    def get_ind_copy(self,s_ind):
        weights=[]
        for w in s_ind.weights:
            weights.append((w['weight'],w['idx']))
        ind=Individual(weights,self.byte_size)
        ind.fitness=s_ind.fitness
        return ind    

    def get_empty_pop(self, pop_idx = 0 ):
        pop=Population(self.lower_limit,self.upper_limit,self.interval,self.fitness_func,pop_idx =pop_idx, log_file = self.log_file )
        return pop

    def make_new_pop(self):
        self.set_weights(self.current_pop.final,True)
        newgen=self.select_individuals(self.current_pop.final)
        self.current_pop_idx+=1
        pop=self.get_empty_pop(self.current_pop_idx)
        self.pops.append(pop)
        self.current_pop=self.pops[self.current_pop_idx]
        self.current_pop.pop_idx=self.current_pop_idx
        self.current_pop.init_population(newgen)
        

    def exec_genetic_selection(self):
        self.exec_cross_over()
        self.current_pop.final=self.current_pop.individuals+self.current_pop.childs
        self.exec_mutation()
        
    def exec_cross_over(self):
        curr_pop=self.current_pop 
        it = range(len(curr_pop.selection)//2)

        for i in it:
            ind_a=curr_pop.selection[i*2]
            ind_b=curr_pop.selection[i*2+1]
            rnd_a=self.get_rnd()
            rnd_b=self.get_rnd()
            c_split_point=self.byte_size*self.osd_count//2
            res_a,res_b=curr_pop.cross_over(ind_a,ind_b,rnd_a,rnd_b,c_split_point)
            res_a.must_recalc=True
            res_b.must_recalc=True
            curr_pop.append(res_a,curr_pop.childs)
            curr_pop.append(res_b,curr_pop.childs)
        
        
    def exec_mutation(self):    
        curr_pop=self.current_pop 
        for i in curr_pop.final:
            rnd=self.get_rnd()
            if rnd < self.mutate_prob:
                i.mutate=True

        for i in range(len(curr_pop.final)):
            if curr_pop.final[i].mutate:
                rnd_a=self.get_rnd()
                rnd_b=self.get_rnd()
                m_res=curr_pop.exec_mutation(curr_pop.final[i],(rnd_a,rnd_b),2)
                m_res.must_recalc=True
                curr_pop.set_individual(m_res,i,curr_pop.final)

    def obtain_chart_data(self):
        resp=requests.get(self.chart_url)
        if resp.status_code != 200:
            self.logger.error ("resp.status_code {}".format(resp.status_code))  

    def run(self):
        self.logger.debug ("Starting {} ".format(self.name))
        self.state =  WeigherState.RUNNING
        while True:
            if self.state ==  WeigherState.RUNNING:
                self.set_weights(self.current_pop.individuals)   
                self.send_stats()             
                self.logger.debug ("Going to print ind ")
                self.current_pop.print_ind(prefix="POP {} indiv".format(self.current_pop_idx),log_file=self.log_file)    
                self.select_for_crossover()                                        
                self.current_pop.print_ind(self.current_pop.selection,prefix="POP {} selec".format(self.current_pop_idx),log_file=self.log_file)   
                self.exec_cross_over()
                self.set_weights(self.current_pop.childs,True)                     
                self.current_pop.print_ind(self.current_pop.childs,prefix="POP {} child".format(self.current_pop_idx),log_file=self.log_file)   
                self.current_pop.final=self.current_pop.individuals+self.current_pop.childs
                self.current_pop.print_ind(self.current_pop.final,prefix="POP {} final".format(self.current_pop_idx),log_file=self.log_file)
                self.exec_mutation()
                self.make_new_pop()
                
            self.logger.debug ("Going to sleep for {} ".format(self.delay))
            time.sleep(self.delay)
            
    def get_json_stats(self, shift=0):
        pop_idx=self.current_pop_idx
        if shift <=0 and (self.current_pop_idx +shift) >0:
            pop_idx=  self.current_pop_idx +shift
            sumf,maxf,avgf = self.pops[pop_idx].get_stats()
            stats={'attempt':self.attempt, 'generation':pop_idx, 'avg':avgf,  'max':maxf, 'sum':sumf}   
            self.logger.debug ("Sending stats {} ".format(stats))
            jstats= json.dumps(stats)
            return jstats
        else:  
            return None
            
    def send_stats(self, shift=0):
        jstats=self.get_json_stats(shift)
        if not jstats is  None:
            try:
                connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
                channel = connection.channel()
                channel.queue_declare(queue=self.amqp_queue)
                
                channel.basic_publish(exchange='',
                                      routing_key=self.amqp_queue,
                                      body=jstats)
                self.logger.debug ("Sending amqp msg {} ".format(jstats))
                connection.close()
        
            except AMQPError as ae:
                 self.logger.error(" There was en error while connecting to amq server: {}".format(type(ae).__name__ ))
                 
    def init_clean_pop(self,  pop =None):
            if pop is None:
                pop=Population(self.lower_limit,self.upper_limit,self.interval,self.fitness_func ,pop_idx=0 , log_file = self.log_file)
            self.current_random_idx=0 
            self.pops=[]
            self.pops.append(pop)
            self.current_pop_idx=0
            self.current_pop=self.pops[self.current_pop_idx]
            self.init_population()
            self.state = WeigherState.RESET                             
            self.attempt=self.attempt+1
            
    def reset_weights(self, inds = None ,  weight =1.0):
        if  inds is None:
            inds=self.current_pop.individuals 
        if len(inds) >0: 
            ind =inds[0]
            for i,val in enumerate(ind.weights):
                             put_osd_reweight(i,weight)
        
    def __init__(self,logger,name,l_limit,u_limit,interval, pop_size, osd_count, r_file_name, fitness_func, amqp_url,  amqp_queue='bdrq', is_physical_model = True ,mutate_prob =0.3 , max_cidx =10 , log_file =None):
        threading.Thread.__init__(self)
        self.attempt=0
        self.use_random = self.attempt >0 
        self.name=name
        self.logger=logger
        self.chart_url='http://172.28.57.129:8000/obtain_new_chart_data/'
        self.amqp_url=amqp_url
        self.amqp_queue=amqp_queue
        
        self.lower_limit=l_limit
        self.upper_limit=u_limit
        self.interval=interval
        self.osd_count = osd_count
        self.pop_size = pop_size 
        self.random_file_name= r_file_name
        self.universe=[]
        self.fitness_func=fitness_func
        self.log_file = log_file
        pop=Population(l_limit,u_limit,interval,self.fitness_func ,pop_idx=0 , log_file = self.log_file)
        self.universe=pop.get_universe(3) #universe  precision 
        self.universe_size=len(self.universe)
        self.byte_size=pop.b_size
        self.current_random_idx=0 
        self.random_values=self.read_random_values()
        self.mutate_prob = mutate_prob 
        self.pops=[]
        self.pops.append(pop)
        self.current_pop_idx=0
        self.current_pop=self.pops[self.current_pop_idx]
        self.is_physical_model=is_physical_model
        self.max_cidx = max_cidx
        self.continuous_add_new_individuals=False   
        self.state = WeigherState.INIT
        self.delay=self.DELAY
        self.init_population()  
        

