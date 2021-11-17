from typing import Collection
from Tweet import Tweet
from Cascade import Cascade

class Processor :

    def __init__(self) :
        
        #collection de cascades associant id de la cascade et la cascade ;)
        self.collection = {}
    
    @property
    def get_collection(self):
        return self.collection
    
    def add_tweet(self, key, tweet):
        type_ = tweet.type
        if type_ == "tweet" : 
            cascade = Cascade(tweet.type, key, tweet.msg, [(tweet.time, tweet.magnitude)])
            self.collection[key] = cascade
        else :
            if key in self.collection :
                self.collection[key].tweets.append((tweet.time, tweet.magnitude))
    
    def get_cascades_series(self, T_obs, min_cascade_size):
        resultat = []
        
        for C, V in self.collection.items() :
            Dt = V.tweets[len(V.tweets)-1][0] - V.tweets[0][0]
            if min_cascade_size <= len(V.tweets) and Dt >= T_obs :
                Key = None
                Value = {}
                Value['type'] = 'serie'
                Value['cid'] = V.cid
                Value['msg'] = V.msg
                Value['T_obs'] = T_obs
                Value['tweets'] = V.tweets

                r = {}
                r[Key] = Value
                resultat.append(r)        
        return resultat
    
    def get_cascade_properties(self,tActuel, T_obs, termined, min_cascade_size):

        resultat = []
        A_supprimer = []
        

        for K, V in self.collection.items() :
            Dt = tActuel - V.tweets[len(V.tweets)-1][0] 
            if min_cascade_size <= len(V.tweets) and Dt >= termined:
                Key = T_obs
                Value = {}
                Value['type'] = 'size'
                Value['cid'] = V.cid
                Value['n_tot'] = len(V.tweets)
                Value['t_end'] = V.tweets[len(V.tweets)-1][0]

                r = {}
                r[Key] = Value
                resultat.append(r)
                A_supprimer.append(K)
        
        for j in A_supprimer:
            del self.collection[j]

        return resultat