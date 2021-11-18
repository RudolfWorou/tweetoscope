"""
Train new models of random forests periodically

Input  : - training examples in  

Output : - post models in the topic models

"""
import argparse
import json
from kafka import KafkaConsumer, KafkaProducer
from kafka import TopicPartition
from sklearn.ensemble import RandomForestRegressor
import pickle

from Logger.logger import *