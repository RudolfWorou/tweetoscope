## Internal libraries
import argparse, json
from kafka import KafkaProducer, KafkaConsumer
import numpy as np
##External libraries
import logger as Logger
from sklearn.ensemble import RandomForestRegressor
import pickle
## functions

## main


def main():

    ## Logger creation 

    logger = Logger.get_logger('Hawkes Estimator', broker_list='localhost:9092', debug=True)  # the source string (here 'my-node') helps to identify
                                                                                 # in the logger terminal the source that emitted a log message.
    
    ## Topics

    input_topic="samples"
    output_topic="models"

    ## Parser setting up

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--broker-list', type=str, required=True, help="the broker list")
    args = parser.parse_args()  # Parse arguments
    
    ## Consumer of cascade_series
    
    consumer = KafkaConsumer(input_topic,                   # Topic name
    bootstrap_servers = args.broker_list,                        # List of brokers passed from the command line
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),  # How to deserialize the value from a binary buffer
    key_deserializer= lambda v: v.decode()                       # How to deserialize the key (if any) 
    )

    ## Producer of cascade_properties

    producer = KafkaProducer(
    bootstrap_servers = args.broker_list,                     # List of brokers passed from the command line
    value_serializer=lambda v: pickle.dumps(v) # How to serialize the value to a binary buffer
    )


    
    X = [] ## X list
    y  = []  ## y list 

    ### Getting data from the input topic
    for msg in consumer:        # Blocking call waiting for a new message

        logger.info("-------------------------------------------------------------")
        logger.info("-------------------------------------------------------------")
        logger.info("Catch a new sample")

        ### checking that we have a serie for the type
        if(msg.value['type']!='sample'):
            logger.critical("The element catched is not a sample")
            break
        ### retrieving information from the a new message
        X.append( msg.value['X'])
        y.append(msg.value['w'])

        
        logger.info(f"Fit the random forest model")
        n=len(X)
        if (n ==1) or (n< 100 and n %10==0) or (n%100==0):
            model = RandomForestRegressor() ## random forest model
            model.fit(X,y)

        logger.info(f"Ready to send a message to models topic")
        
        output_message = model

        # Send the message to the cascade_properties topic

        producer.send(output_topic, value = output_message) 

        logger.info("Message successfully sent to models topic")
    
    # Flush: force purging intermediate buffers before leaving
    producer.flush()     


if __name__=="__main__":
    main()