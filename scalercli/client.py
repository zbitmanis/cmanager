#!/usr/bin/env python
import pika
import uuid
import argparse
import ConfigParser


class RClient(object):
    def __init__(self,host,user,password):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=host, credentials = pika.PlainCredentials(user, password)))

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
        self.channel.basic_publish(exchange='message',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


configParser = ConfigParser.RawConfigParser()   
configFilePath = '/etc/scaler.cfg'
configParser.read(configFilePath)


host=configParser.get('amqp', 'host')
user=configParser.get('amqp', 'user')
password=configParser.get('amqp', 'password')


rpc = RClient(host, user,password )

parser = argparse.ArgumentParser(description=" Rpc Scaler daemon")
parser.add_argument('-s', '--signal', default='status')
args = parser.parse_args()

signal=0
if args.signal =="status":
    signal=99
elif args.signal =="start":
    signal=1
elif args.signal =="pause":
    signal=2
elif args.signal =="reset":
    signal=4
print(" [x] Requesting {} {}".format(args.signal, signal))
response = rpc.call(signal)
print(" [.] Got %s" % response)

