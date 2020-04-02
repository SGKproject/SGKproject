# -*- coding: utf-8 -*-
import pika
import sys
import pickle
import random
import time

conn_params = pika.ConnectionParameters('localhost', 5680)
connection = pika.BlockingConnection(conn_params)
channel = connection.channel()

channel.queue_declare(queue='in_queue', 
					arguments={'x-message-ttl':60000},
					durable=True)

for i in range(100):
	z={random.choice(['big','small','medium']):random.choice(range(10))}
	channel.basic_publish(exchange='',routing_key='in_queue',
			  body=(pickle.dumps(z, 0)).decode(),
			  properties = pika.BasicProperties(
			  	delivery_mode=2
			  	))
	print("Greeting sent")
	time.sleep(2)

connection.close()