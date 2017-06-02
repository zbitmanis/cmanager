#!/usr/bin/env python3

"""
all AMQP related code is  based on pika Asynchronous consumer example 
all other  
  
https://github.com/pika/pika/blob/master/LICENSE

Copyright (c) 2009-2015, Tony Garnock-Jones, Gavin M. Roy, Pivotal and others.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of the Pika project nor the names of its contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
import math
import time
import pika
import json


from weigher import Weigher, WeigherState 



def math_expr_lab2(args):
    sum_of_pw=0.0    
    for a in args:
        sum_of_pw+=math.pow(float(a),2.0)
    sxy2=math.sqrt(sum_of_pw)
    res=0.5+math.cos(2*sxy2)/(1+sxy2)
    return round(res,2) 

class Scaler:
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'topic'
    QUEUE = 'rpc_queue'
    ROUTING_KEY = 'rpc_queue'
    
    def __init__(self,log_file_name, rnd_file_name ,logger,amqp_url ):
        self.log_file_name = log_file_name 
        self.rnd_file_name = rnd_file_name
        self.logger=logger
        self.daemon=False
        self.lower_limit=0.0
        self.upper_limit=1.0
        self.interval=0.04
        self.pop_size = 8   
        self.osd_count =6
        self.osd_weights_map={'0':0,'1':1,'2':2,'3':3,'4':4,'5':5}

        self.weigher=Weigher(self.logger,"Weighter",self.lower_limit, self.upper_limit, self.interval, self.pop_size, self.osd_count,self.rnd_file_name ,math_expr_lab2 , amqp_url=amqp_url, is_physical_model =False, log_file =self.log_file_name )
        
        
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self.setup_exchange = False  if self.EXCHANGE == '' else False

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()
        time.sleep(30)
        self.logger.info ("joining thread") 
        self.weigher.join() 
        
       
    def connect(self):
        self.logger.info('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)
                                     
    def on_connection_open(self, unused_connection):

        self.logger.info('Connection opened')
        self.logger.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)
        self.open_channel()
    
    def on_connection_closed(self, connection, reply_code, reply_text):

        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)
            
    def reconnect(self):
        self._connection.ioloop.stop()
        if not self._closing:
            self._connection = self.connect()
            self._connection.ioloop.start()
            
    def open_channel(self):
        self.logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.info('Channel opened')
        self._channel = channel
        
        self.logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.exchange_declare(exchange=self.EXCHANGE,
                                       exchange_type=self.EXCHANGE_TYPE)
        self.logger.debug('Declaring queue %s', self.QUEUE )
        self._channel.queue_declare(self.on_queue_declareok,  queue=self.QUEUE)
        
        
    def on_queue_declareok(self, method_frame):

        self.logger.info('Binding %s to %s with %s',
                    self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        self._channel.queue_bind(self.on_bindok, self.QUEUE,
                                 self.EXCHANGE, self.ROUTING_KEY)
                                 
    def on_bindok(self, unused_frame):
        self.logger.info('Queue bound')
        self.start_consuming()
        
    def start_consuming(self):

        self.logger.info('Issuing consumer related RPC commands')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.QUEUE)


    def on_consumer_cancelled(self, method_frame):
        self.logger.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_cancelok(self, unused_frame):

        self.logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()
        
    def on_channel_closed(self, channel, reply_code, reply_text):

        self.logger.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()
        
    def on_message(self, unused_channel, basic_deliver, properties, body):

        response=self.weigher.state
        cmd  = int(body) 
        self.logger.info('body {} '.format(cmd))
        if cmd== 99 :
            self.logger.info('Sending status') 
            resp_dict={'status': self.weigher.state,  'population': self.weigher.current_pop_idx }
            response=json.dumps(resp_dict)
            
        elif cmd ==1 :
            if   self.weigher.state == WeigherState.INIT: 
                self.logger.info('Setarting weigher thread')
                self.weigher.start() 
            self.weigher.state=WeigherState.RUNNING
            response=self.weigher.state    
        elif cmd ==2:
            self.weigher.state=WeigherState.PAUSED
            response=self.weigher.state    
        elif cmd ==4:
            self.weigher.state=WeigherState.RESET
            self.weigher.init_clean_pop()
            self.weigher.reset_weights()
            response=self.weigher.state    
        
            
        self._channel.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         properties.correlation_id),
                     body=str(response))
                     
        self.logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        self.logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

