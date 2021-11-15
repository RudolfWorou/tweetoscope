import argparse                   # To parse command line arguments
import json                       # To parse and dump JSON
from kafka import KafkaConsumer   # Import Kafka consumer

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
consumer = KafkaConsumer('tweets',                   # Topic name
  bootstrap_servers = args.broker_list,                        # List of brokers passed from the command line
  value_deserializer=lambda v: json.loads(v.decode('utf-8')),  # How to deserialize the value from a binary buffer
  key_deserializer= lambda v: v.decode()                       # How to deserialize the key (if any)
)

for msg in consumer:                            # Blocking call waiting for a new message
    print (f"msg: ({msg.key}, {msg.value})")    # Write key and payload of the received message


msg = {
    'dst': 'Metz',
    'temp': 2,
    'type': 'rain',
    'comment': 'Nothing special'
}
for _ in range(3):
    producer.send('cascades_series', key = msg['dst'], value = msg) # Send a new message to topic
    producer.send('cascades_properties', key = msg['dst'], value = msg) # Send a new message to topic
    
producer.flush() # Flush: force purging intermediate buffers before leaving