#!/usr/bin/python3

import argparse                   # To parse command line arguments
import json                       # To parse and dump JSON
from kafka import KafkaConsumer   # Import Kafka consumer
from kafka import KafkaProducer
from Processor import Processor
import _thread
import time
from Tweet import Tweet
from Cascade import Cascade

#Parametres
brokers="localhost:2181"

#[topic]
# The topic on which to listen for the tweets
topic_in="tweets"
# The topic on which to produce the partial series
out_series="cascade_series"
# The topic on which to produce the cascade properties
out_properties="cascade_properties"

#[times]
# Times for producing the partial cascades (timestamp)
T_obs1=600
T_obs2=1200

# Time to consider the cascade is over (timestamp)
terminated=1800

#[cascade]
# This is the minimal number of tweets an a cascade. A cascade with
# less tweets is ignored.
min_cascade_size=10

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--broker-list', type=str, required=True, help="the broker list")
args = parser.parse_args()  # Parse arguments

#Le producer
producer = KafkaProducer(
  bootstrap_servers = args.broker_list,                     # List of brokers passed from the command line
  value_serializer=lambda v: json.dumps(v).encode('utf-8'), # How to serialize the value to a binary buffer
  key_serializer=str.encode                                 # How to serialize the key
)

#Le consumer
consumer = KafkaConsumer(topic_in,                   # Topic name
  bootstrap_servers = args.broker_list,                        # List of brokers passed from the command line
  value_deserializer=lambda v: json.loads(v.decode('utf-8')),  # How to deserialize the value from a binary buffer
  key_deserializer= lambda v: v.decode()                       # How to deserialize the key (if any)
)

#Creation d'une carte de processeurs
cartes_processeurs = {}

def Consumer(params, temps):

  for msg in params:                            # Blocking call waiting for a new message
    
      Key = msg.key
      type = msg.value['type']
      source = msg.value['tweet_id']
      msge = msg.value['msg']
      t = msg.value['t']
      m = msg.value['m']
      info = msg.value['info']

      source_exist = (source in cartes_processeurs)

      if type=="tweet" and not source_exist:      
        cartes_processeurs[source] = Processor()
        tweet = Tweet(type, msge, t, m, source, info)
        (cartes_processeurs[source]).add_tweet(Key, tweet)
      
      elif source_exist : #tweet or retweet
        tweet = Tweet(type, msge, t, m, source, info)
        (cartes_processeurs[source]).add_tweet(Key, tweet)   
  time.sleep(temps)

def Producer(params, temps) :

  for K, V in cartes_processeurs:
    cascades_series1 = V.get_cascades_series(T_obs1, min_cascade_size)
    if len(cascades_series1) != 0:
        for c in cascades_series1 :
              for Cle, Valeur in c:
                  params.send('cascades_series', key = Cle, value = Valeur) # Send a new message to topic

    cascades_series2 = V.get_cascades_series(T_obs2, min_cascade_size)
    if len(cascades_series2) != 0:
        for c in cascades_series1 :
              for Cle, Valeur in c:
                  params.send('cascades_series', key = Cle, value = Valeur) # Send a new message to topic
  

    cascades_properties1 = V.get_cascades_properties(T_obs1, terminated, min_cascade_size)
    if len(cascades_properties1) != 0:
        for c in cascades_properties1 :
              for Cle, Valeur in c:
                  params.send('cascades_properties', key = Cle, value = Valeur) # Send a new message to topic

    cascades_properties2 = V.get_cascades_properties(T_obs2, terminated, min_cascade_size)
    if len(cascades_properties2) != 0:
        for c in cascades_properties2 :
              for Cle, Valeur in c:
                  params.send('cascades_properties', key = Cle, value = Valeur) # Send a new message to topic

  
  time.sleep(temps)    
  params.flush() # Flush: force purging intermediate buffers before leaving

# Create two threads as follows
try:
   _thread.start_new_thread(Consumer, (consumer,1, ) )
   _thread.start_new_thread(Producer, (producer,2, ) )
except:
   print ("Error: unable to start thread")

while 1:
    pass


