## Internal libraries
import argparse, json
from kafka import KafkaProducer, KafkaConsumer,TopicPartition
import logger as Logger
import pickle



def main():

    ## Logger creation 
    logger = Logger.get_logger('Predictor', broker_list='kafka-service:9092', debug=True)  # the source string (here 'my-node') helps to identify
                                                                                 # in the logger terminal the source that emitted a log message.
    
    ## Topics
    input_topic_1 = "cascade_properties"
    input_topic_2="models"
    output_topic_1="samples"
    output_topic_2 = "alerts"
    output_topic_3 = "stats"

    ## Parser setting up
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--broker-list', type=str, required=True, help="the broker list")
    parser.add_argument('--observation-window', type=str, required=True, help="Observation window which can take the values : 300/600/1200")
    args = parser.parse_args()  # Parse arguments
   
    
    ## Consumer of cascade_series
    consumer_1 = KafkaConsumer(input_topic_1,
    bootstrap_servers = args.broker_list,                        # List of brokers passed from the command line
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),  # How to deserialize the value from a binary buffer
    auto_offset_reset="earliest",
    key_deserializer= lambda v: v.decode()                        # How to deserialize the key (if any)
    #group_id="PropertiesConsumerGroup-{}".format(args.observation_window)
    )

    #consumer_1.assign([TopicPartition(input_topic_1, key_dic[args.observation_window])])


    consumer_2 = KafkaConsumer(input_topic_2,                   # Topic name
    bootstrap_servers = args.broker_list,                        # List of brokers passed from the command line
    value_deserializer=lambda v: pickle.loads(v),  # How to deserialize the value from a binary buffer
    auto_offset_reset="earliest",
    #group_id = "ModelsConsumerGroup-{}".format(args.observation_window),   
    consumer_timeout_ms=10000
    )
                                
    ## Producer of cascade_properties

    producer = KafkaProducer(
    bootstrap_servers = args.broker_list,                     # List of brokers passed from the command line
    value_serializer=lambda v: json.dumps(v).encode('utf-8'), # How to serialize the value to a binary buffer
    key_serializer=  lambda v: json.dumps(v).encode('utf-8')                                 # How to serialize the key
    )


    ### Prior model parameters : Negative Power law

    alpha=  2.4
    mu=10
    ### 
    N_TOT={}## dictionnary with cid as keys and n_tot as values 
    msg_params={}            ##dictionary with cid as keys and msg params as value

    ### Getting data from the input topic
    for msg in consumer_1:        # Blocking call waiting for a new message
        
        T_obs = int(msg.key)
        
        #print(T_obs,msg.key, T_obs!=int(args.observation_window) )
        if T_obs!=int(args.observation_window):
            continue
        #
        ### checking that we have a parameters for the type
        if(msg.value['type']=='parameters'):
            
            #T_obs = msg.key
            cid = msg.value['cid']
            p,beta = tuple(msg.value['params'])
            n_supp = msg.value['n_supp']
            n_obs =  msg.value['n_obs']

            n_star = msg.value['n_star']
            G1= msg.value['G1']
            #logger.info("Catch a new message of type parameters where T_obs is : " + str(T_obs) + " And cid is :" +str (cid))
            if cid in N_TOT.keys():
                n_tot = N_TOT[cid]
            else:
                msg_params[cid] = msg
                continue
        elif (msg.value['type']=='size'):
            n_tot = msg.value['n_tot']
            cid = msg.value['cid']
            N_TOT[cid] = n_tot
            logger.info("Catch a new message of type size where T_obs is : " + str(T_obs) + " ,cid is :" +str(cid) + " and n_tot is :" +str(n_tot))
            if cid in msg_params:
                this_msg = msg_params[cid]
                p,beta = tuple(this_msg.value['params'])
                n_supp = this_msg.value['n_supp']
                n_obs =  this_msg.value['n_obs']

                n_star = this_msg.value['n_star']
                G1= this_msg.value['G1']
            else:
                logger.debug("Message of type parameters isn't received yet. T_obs is : " + str(T_obs) + " And cid is :" +str (cid))
                continue
        if G1==0:
            #logger.critical('G1 is equals to zero')   
            G1=0.000001
            w = (n_tot - n_obs)*(1-n_star)/G1
            X=[p,n_star,G1]
        else:
            w = (n_tot - n_obs)*(1-n_star)/G1
            X=[p,n_star,G1]

        samples = {                                              
        'type': 'sample',
        'cid': cid,
        'X': X,
        'w': w,                         
        }
        logger.info("Sending messages to samples where T_obs is : " + str(T_obs) + " and cid is :" +str (cid))
        producer.send(output_topic_1, key = T_obs, value = samples)
        logger.info("Message successfully sent to samples")

        for msg_2 in consumer_2:
            model = msg_2.value
        
        w_pred = model.predict([X])[0] #On ignore ce qui vient du random forest (si le résultat n'est pas correct)
        #w_pred = w
        n_pred = n_obs+w_pred*(G1/(1-n_star))

        ARE = abs(n_pred - n_tot) / n_tot

        alerts ={
            'type' : 'alert',
            'cid' :cid,
            'msg' : 'blah blah',
            'T_obs' : T_obs,
            'n_tot' : n_pred,
            }

        stats={
                'type': 'stat',
                'cid': cid,
                'T_obs': T_obs,
                'ARE': ARE                       
                }
        logger.info("Sending messages to alerts and stats where T_obs is : " + str(T_obs) + " and cid is :" +str (cid))

        producer.send(output_topic_2, key = None, value = alerts)    
        producer.send(output_topic_3, key = None, value = stats)

        logger.info("Message successfully sent to alerts and stats")
    producer.flush()     


if __name__=="__main__":
    main()
