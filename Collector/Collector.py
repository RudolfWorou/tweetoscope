#!/usr/bin/python3
import argparse                   # To parse command line arguments
import json
from kafka import KafkaConsumer   # Import Kafka consumers
from kafka import KafkaProducer

from Processor import Processor
from Tweet import Tweet
import logger as Logger




def main():

    #[topic]
    # The topic on which to listen for the tweets
    topic_in="tweets"
    # The topic on which to produce the partial series
    out_series="cascade_series"
    # The topic on which to produce the cascade properties
    out_properties="cascade_properties"

    #[times]
    # Times for producing the partial cascades (timestamp)
    T_obs1=300
    T_obs2=600
    T_obs3=1200

    T_obs = [T_obs1, T_obs2,T_obs3]

    # Time to consider the cascade is over (timestamp)
    terminated=1800

    #[cascade]
    # This is the minimal number of tweets an a cascade. A cascade with
    # less tweets is ignored.
    min_cascade_size=10

    ## Logger creation 
    logger = Logger.get_logger('Collector', broker_list='kafka-service:9092', debug=True)  # the source string (here 'my-node') helps to identify
                                                                                    # in the logger terminal the source that emitted a log message.
        
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
      auto_offset_reset="earliest",
      key_deserializer= lambda v: v.decode()                       # How to deserialize the key (if any)
    )

    #Creation d'une carte de processeurs#
    cartes_processeurs = {}

    for msg in consumer:                              
        #On récupère les infos contenus dans un tweet/retweet
        Key = msg.value['tweet_id']
        type_ = msg.value['type']
        source = msg.key
        msge = msg.value['msg']
        t = msg.value['t']
        m = msg.value['m']
        info = msg.value['info']

        #On vérifie si la source existe déjà dans notre carte de processeurs
        source_exist = (source in cartes_processeurs)

        #On vérifie si c'est un nouveau tweet et que la source n'existe pas alors on crée un processeur
        if type_=="tweet" and not source_exist:      
          cartes_processeurs[source] = Processor()
          tweet = Tweet(type_, msge, t, m, source, info)
          (cartes_processeurs[source]).add_tweet(Key, tweet)
        
        elif type_=="tweet" and source_exist:      
          tweet = Tweet(type_, msge, t, m, source, info)
          (cartes_processeurs[source]).add_tweet(Key, tweet)

        elif type_ =="retweet" and source_exist : #tweet or retweet
          tweet = Tweet(type_, msge, t, m, source, info)
          (cartes_processeurs[source]).add_tweet(Key, tweet)  

        elif type_ == "retweet" and not source_exist:
              logger.critical(f"The cascade with id {Key} already has been closed.")
              continue 

        #On vérifie si il y a moyen d'envoyer des cascades partielles
        for i in T_obs :  
          cascades_series = cartes_processeurs[source].get_cascades_series(t,i, min_cascade_size)
          if len(cascades_series) != 0:
            for c in cascades_series :      
              Cle = list(c.keys())[0]
              Valeur = c[Cle]
              producer.send(out_series, key = str(Cle), value = Valeur) # Send a new message to topic
              #logger.info("-------------------------------------------------------------")
              #logger.info("-------------------------------------------------------------")
              #logger.info("A new cascade has been send to topic cascade_series")
        
        #On vérifie si il y a moyen d'envoyer des cascades finies
        cascades_properties = cartes_processeurs[source].get_cascade_properties(t,T_obs, terminated, min_cascade_size)
        if len(cascades_properties) != 0:
          for c in cascades_properties :
            Cle = list(c.keys())[0]
            Valeur = c[Cle]
            producer.send(out_properties, key = str(Cle), value = Valeur ) # Send a new message to topic
                  
            logger.info("-------------------------------------------------------------")
            logger.info("-------------------------------------------------------------")
            logger.info("A new cascade has been send to topic cascade_properties")


    producer.flush() # Flush: force purging intermediate buffers before leaving

if __name__=="__main__":
    main()



