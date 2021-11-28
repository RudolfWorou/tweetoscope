#!/usr/bin/python3

import argparse                   # To parse command line arguments
import json                       # To parse and dump JSON
from kafka import KafkaConsumer   # Import Kafka consumer

import logger as Logger

def main():

    # The topic on which to listen the tweets with the highest predicted popularities
    topic_in="stats"
    
    ## Logger creation 
    logger = Logger.get_logger('Monitor', broker_list='localhost:9092', debug=True)  # the source string (here 'my-node') helps to identify
                                                                                    # in the logger terminal the source that emitted a log message.
        
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--broker-list', type=str, required=True, help="the broker list")
    args = parser.parse_args()  # Parse arguments

    #Le consumer
    consumer = KafkaConsumer(topic_in,                   # Topic name
      bootstrap_servers = args.broker_list,                        # List of brokers passed from the command line
      value_deserializer=lambda v: json.loads(v.decode('utf-8')),  # How to deserialize the value from a binary buffer
      auto_offset_reset="earliest",
      key_deserializer= lambda v: v.decode()                       # How to deserialize the key (if any)
    )

    for msg in consumer:                            # Blocking call waiting for a new message  
        
        cid = msg.value['cid']
        type_ = msg.value['type']
        T_obs = msg.value['T_obs']
        ARE_ = msg.value['ARE']
                    
        logger.info("-------------------------------------------------------------")
        logger.info("-------------------------------------------------------------")
        logger.info("Refresh statistics about performance of our system")
        logger.info(f"cid = {cid}, T_obs = {T_obs}, ARE = {ARE_},  type = {type_}")


if __name__=="__main__":
    main()



