#!/usr/bin/python3

import argparse                   # To parse command line arguments
import json, sys, time                       # To parse and dump JSON
from kafka import KafkaConsumer   # Import Kafka consumer

import logger as Logger


def main():

    # The topic on which to listen the tweets with the highest predicted popularities
    topic_in="alerts"
    
    ## Logger creation 
    logger = Logger.get_logger('Dashboard', broker_list='localhost:9092', debug=True)  # the source string (here 'my-node') helps to identify
                                                                                    # in the logger terminal the source that emitted a log message.
        
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--broker-list', type=str, required=True, help="the broker list")
    parser.add_argument('--K', type=str, required=True, help="the number K of hottest cascades to display")
    args = parser.parse_args()  # Parse arguments

    #Le consumer
    consumer = KafkaConsumer(topic_in,                   # Topic name
      bootstrap_servers = args.broker_list,                        # List of brokers passed from the command line
      value_deserializer=lambda v: json.loads(v.decode('utf-8')),  # How to deserialize the value from a binary buffer
      key_deserializer= lambda v: v.decode()                       # How to deserialize the key (if any)
    )
    hottest_cascades = []
    print(f"Here are the {args.K}-hottest tweets")
    
    for msg in consumer:                            # Blocking call waiting for a new message  
        
        
        cid = msg.value['cid']
        type_ = msg.value['type']
        T_obs = msg.value['T_obs']
        message = msg.value['msg']
        n_tot = msg.value['n_tot']
        if len(hottest_cascades)< int(args.K):
            hottest_cascades.append((cid,T_obs,message,n_tot))
            
        else:
            hottest_cascades.append((cid,T_obs,message,n_tot))
            hottest_cascades.sort(key=lambda x:x[3])
            hottest_cascades.pop()

        goback = "\033[F" * int(args.K)
        for i in range(int(args.K)):
            
            try:
                cascade  = hottest_cascades[i]
                sys.stdout.write(f"The estimated cascade size is {cascade[3]} for the tweet with id {cascade[0]},an observation windows of {cascade[1]} and the message {cascade[2]}  \n")
            except:
                sys.stdout.write(f"Waiting for {i+1}-hottest tweet \n")

        sys.stdout.write(f"{goback}")
		


if __name__=="__main__":
    main()



