#!/usr/bin/env python3

#import time
import pika
import threading

class Consumer (threading.Thread):
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'topic'
    QUEUE = 'rpc_queue'
    ROUTING_KEY = 'rpc_queue'
    
    def __init__(self, amqp_url, logger, weigher):
        self.logger=logger
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self.weigher=weigher
        threading.Thread.__init__(self)
        self.setup_exchange = False  if self.EXCHANGE == '' else False
    
    def  run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()
        self.logger.info ("After ioloop") 
        
    
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

        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:

            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
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

