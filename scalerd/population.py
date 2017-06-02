
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

from individuals import Individual 
from datetime import datetime



class Population:
    def get_individual_bin_size(self,a_min,a_max,a_int):
         i_size=1+(float(a_max)-float(a_min))/float(a_int)
         res=0
         for i in range(16):
            l_limit=2**i
            u_limit=2**(i+1)
            if i_size >l_limit and i_size <= u_limit:
                res=i+1
                break
         return res

    def init_population(self,src_individuals,dst_inds=None):
        if dst_inds is None:
            dst_inds=self.individuals
        for ind in src_individuals:
            weights=[]
            for w in ind.weights:
                weights.append((w['weight'],w['idx']))
            t_ind=Individual(weights,ind.byte_size) 
            t_ind.fitness_func=self.fitness_func
            t_ind.fitness=ind.fitness
                #t_ind.recalc_fitness()
            self.append(t_ind,dst_inds)

    def encode_value(self,a_value):
        k=int((float(a_value)-(self.l_limit))*(2**self.b_size-1)/(self.u_limit-self.l_limit))
        return k
    
    def decode_value(self,a_value):
        x=self.l_limit+int(a_value)*(self.u_limit-self.l_limit)/float(2**self.b_size-1)
        return x

    def get_universe(self,ngigits=2):
        v_size=2**self.b_size
        res=[Individual]*v_size
        for i in range(v_size):
            x=round(self.decode_value(i),ngigits)
            res[i]=Individual([(x,i)],self.b_size)
        return res

    def get_individual_from_br(self,ab_rep):
        i=0
        j=0
        b_rep=[]
        weights=[]
        tind=Individual([(0,0)],self.b_size)

        for b in ab_rep:
            if i == j*self.b_size:
                if j != 0 :
                    xk=tind.d_convert(b_rep,self.b_size)
                    x=round(self.decode_value(xk),2)
                    weights.append((x,xk))      
                b_rep=[]
                j+=1
            b_rep.append(b)
            i+=1
        xk=tind.d_convert(b_rep,self.b_size)
        x=round(self.decode_value(xk),2)
        weights.append((x,xk))      
          

        ind=Individual(weights,self.b_size)
        return ind

    def append(self,a_ind,a_list=None):
        if a_list is None:
            a_list=self.individuals
        a_ind.fitness_func=self.fitness_func
       # a_ind.recalc_fitness()
        a_list.append(a_ind)
        self.size+=1

    def set_individual(self,a_ind,index,a_list=None):
        if a_list is None:
            a_list=self.individuals
        a_ind.fitness_func=self.fitness_func
#        a_ind.recalc_fitness()
        a_list[index]=a_ind

    def append_by_br(self,ab_rep):
        ind=self.get_individual_from_br(ab_rep)
        ind.fitness_func=self.fitness_func
        #ind.recalc_fitness()
        self.individuals.append(ind)
        self.size+=1
    
    def set_individual_by_br(self,ab_rep,index):
        ind=self.get_individual_from_br(ab_rep)
        ind.fitness_func=self.fitness_func
        ind.recalc_fitness()
        self.individuals[index]=ind 

    def get_stats(self,inds=None):
        if inds is None:
            inds=self.individuals
        avgf=0
        maxf=0
        sumf=0
        c=0
        
        for i in inds:
            if i.fitness>maxf:
                maxf=i.fitness 
            sumf+=i.fitness
            c+=1
        avgf=sumf/c
        avgf=round(avgf,4)
        maxf=round(maxf,4)
        sumf=round(sumf,4)
        return (sumf,maxf,avgf)

    def get_neo(self):
        maxf=0
        for i in self.individuals:
            if i.fitness>maxf:
                maxf=i.fitness 
                one=i
        return one

    def get_sum_fitness(self,a_inds):
        res=0    
        for i in a_inds:
             res+=i.fitness
        return res

    def init_roulette(self,verbose=False,a_inds=None):
        if a_inds is None:
           a_inds=self.individuals
        sumf=self.get_sum_fitness(a_inds)
        l=len(a_inds)
        ipos=0.0
        for i in range(l-1):
            ipos+= round(a_inds[i].fitness/sumf,4)
            self.possibilities.append(ipos)
        self.possibilities.append(1.0)
        self.init_population(a_inds,self.rndselection)
        for ri in range(len(self.rndselection)):
            i=self.rndselection[ri]

    def get_chosen_idx(self,a_rnd):
        i=0 
        while (a_rnd>self.possibilities[i]):
            i+=1
        return i
   
    def get_equal_intervals(self,a_byte_lenght):
            # japarbauda n+byte 
        v_interval=1.0/a_byte_lenght
        res=[]
        for i in range(a_byte_lenght):
           res.append(i*v_interval) 
        res.append(1.0)
        return res 
 
    def get_cross_point(self,a_rnd,a_pCnt,verbose=False): 
        interval=self.get_equal_intervals(a_pCnt)
        if verbose:
            print ("Cross_point probabilities:")
            for pi in range(len(interval)-1):
                print (" {} ".format(round(interval[pi],4)),end='')
            print (" ")
        i=0
        if ( a_rnd!=0 ):
            while not ( interval[i] <a_rnd <= interval[i+1] ):
                i+=1 
        return i+1   
   
    def get_mutation_point(self,a_rnd,a_byte_length,verbose=False): 
        interval=self.get_equal_intervals(a_byte_length)
            
        i=0
        if ( a_rnd!=0 ):
            while not ( interval[i] <a_rnd <= interval[i+1] ):
                i+=1 
        return i     

    def get_cross_points(self,a_rnd_a,a_rnd_b,a_pCnt,verbose=False):
        point_a=self.get_cross_point(a_rnd_a,a_pCnt,verbose)
        point_b=a_pCnt+self.get_cross_point(a_rnd_b,a_pCnt-1,verbose)
        return (point_a,point_b)

    def cross_over(self,a_ind_a,a_ind_b,a_rnd_a,a_rnd_b,a_pCnt,verbose=False):
        point_a,point_b=self.get_cross_points(a_rnd_a,a_rnd_b,a_pCnt,verbose)
        res_a=[]
        res_b=[]
        for i in range(len(a_ind_a.b_rep)):
            if i < point_a or i >= point_b:
                res_a.append(a_ind_a.b_rep[i])
                res_b.append(a_ind_b.b_rep[i])
            else:
                res_a.append(a_ind_b.b_rep[i])
                res_b.append(a_ind_a.b_rep[i])
        ind_rA=self.get_individual_from_br(res_a)
        ind_rB=self.get_individual_from_br(res_b)
        if verbose:
            r1=a_ind_a.sb_rep()
            r2=a_ind_b.sb_rep()
            print("{} Cpoint {}({})  {}({}) => {}".format(r1,point_a,round(a_rnd_a,4),point_b,round(a_rnd_b,4),ind_rA.sb_rep()))
            print("{} Cpoint {}({})  {}({}) => {}".format(r2,point_a,round(a_rnd_a,4),point_b,round(a_rnd_b,4),ind_rB.sb_rep()))
        return (ind_rA,ind_rB)  

    def exec_mutation(self,ind,a_rNumbers,a_mutation_point_cnt,verbose=False): 
        m_points=[]
        w_length=len(ind.b_rep)
        res_bR=[]
        for i in range(a_mutation_point_cnt):
           rnd=a_rNumbers[i]
           point=self.get_mutation_point (rnd,w_length,i==0 and verbose)
           m_points.append( point)
           if verbose: 
               print ("mpoint {} ({}) ".format(point,round(rnd,4)),end='')
        
        if verbose: 
            print (" ")
        for i in range(w_length):
            if i in m_points:
                if ind.b_rep[i] == 0:
                  res_bR.append(1)
                else:
                  res_bR.append(0)
            else:    
                res_bR.append(ind.b_rep[i])
        ind_r=self.get_individual_from_br(res_bR)
        return ind_r

    def print_ind(self,inds=None,prefix="",delimiter='\t',log_file=None):
       if inds is None:
            inds=self.individuals
       prefix="[{}]: {}:\t".format(datetime.now().time(),prefix)
       print_strings=[]
    
       header=prefix+"Fitness" 
       for hi in range(len(inds[0].weights)): 
           header+="{}W{}{}WI{}".format(delimiter,hi,delimiter,hi,hi)
       header+=delimiter+"Wbin" 
       print_strings.append(header) 
        
       for ri in range(len(inds)):
            i=inds[ri]   
            data=prefix+"{}".format(i.fitness)
            for hi in range(len(i.weights)): 
                w= i.weights[hi]   
                data+="{}{}{}{}".format(delimiter,w['weight'],delimiter,w['idx'])
            data+="{}{}".format(delimiter,i.str_binary_rep())
            print_strings.append(data)
       sumf,maxf,avgf = self.get_stats(inds)
       print_strings.append( "{}SUM/MAX/AVG: {}/{}/{}".format(prefix,sumf,maxf,avgf) )

       if log_file is None:
            [self.logger.debug(ps) for ps in print_strings]
       else:
            #log_file=open(filename,'a')
            [log_file.write(ps+'\n') for ps in print_strings]
            #log_file.close()

    def __init__(self,al_limit,au_limit,a_interval,a_fitness_func,pop_idx , log_file):
        self.individuals=[]
        self.possibilities=[]
        self.rndselection=[]
        self.selection=[]
        self.selection_source=[]
        self.childs=[]
        self.u_limit=float(au_limit)  
        self.l_limit=float(al_limit)  
        self.interval=float(a_interval)
        self.b_size=self.get_individual_bin_size(al_limit,au_limit,a_interval)
        self.fitness_func=a_fitness_func
        self.fitness=0
        self.final=[]
        self.size=0
        self.pop_idx = pop_idx
        self.log_file = log_file
