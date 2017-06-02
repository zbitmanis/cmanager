

import redis 
import uuid
import pytz
import random

import pika

from datetime import datetime


class hmfkException(Exception):
  def __init__(self,code,message):
      self.code=code
      self.message=message

class projectsEntity:
  def __init__(self,name='',enabled=False,x_account_bytes_used=0,x_account_container_count=0,x_account_object_count=0,x_timestamp=0):
      tz = pytz.timezone("Europe/Riga")
      self.name=name 
      self.enabled=enabled
      self.x_account_bytes_used=x_account_bytes_used
      self.x_account_object_count=x_account_object_count
      self.x_account_container_count=x_account_container_count
      self.x_timestamp=x_timestamp
      self.date=datetime.fromtimestamp(float(x_timestamp), tz)

class RpcClient(object):
    def __init__(self, host, user, password, queue='rpc_queue'):
        self.credentials = pika.PlainCredentials(user, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=host, credentials = self.credentials))
        self.exchange='message'
        self.queue=queue
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=self.queue,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


def set_redis_value(key,value):
    r=redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set(key.encode('ascii'),value)

def get_redis_value(key):
    r=redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_value=r.get(key.encode('ascii'))
    if redis_value is None:
      return 0
    else:
      return redis_value
    


def receive_gen_stat(host, user, password, queue='bdrq'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host, credentials = pika.PlainCredentials(user, password ) ))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    method_frame, header_frame, body = channel.basic_get(queue = queue)        
    if  method_frame is None or method_frame.NAME == 'Basic.GetEmpty':
        connection.close()
        return None
    else:            
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close() 
        return body

def make_amqp_call(host, user, password, signal):
    if signal =="status":
        rsignal=99
    elif signal =="start":
        rsignal=1
    elif signal =="pause":
        rsignal=2
    elif signal =="reset":
        rsignal=4
    rpc = RpcClient(host, user, password )
    response = rpc.call(rsignal)
    return response
    
    
