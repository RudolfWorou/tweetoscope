"""
Imput  : - parameters from Hawkes estimator
         - windows length
         - random forest model from topic model - take the last model with its associated window length
         - cascade size from collector

Output : - prediction post in alert topic
         - periodic training example to the learner int topic samples
         - prediction error in topic stats
"""