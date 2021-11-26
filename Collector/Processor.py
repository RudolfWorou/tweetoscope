'''
La classe processeur sert à gérer dans une collection (map) dont la clé correspond à l'identifiant
du tweet et la valeur le tweet d'une personne X et tous ses retweets.
'''
from Cascade import Cascade
class Processor :

    def __init__(self) :
        
        #collection de cascades dont : key : id_tweet et value : tweet initial et tous les retweets correspondant
        self.collection = {}
    
    #Méthode servant à rajouter un re-tweet dans la cascade correspondant
    def add_tweet(self, key, tweet):

        type_ = tweet.type
        if type_ == "tweet" : 
            cascade = Cascade(tweet.type, key, tweet.msg, [(tweet.time, tweet.magnitude)])
            self.collection[key] = cascade
        else :
            if key in self.collection :
                self.collection[key].tweets.append((tweet.time, tweet.magnitude))
    
    #Méthode servant à récupérer toutes les cascades après un temps d'observation donné
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
    
    #Méthode servant de récupérer toutes les cascades supposées terminées
    def get_cascade_properties(self,tActuel, T_obs, termined, min_cascade_size):

        resultat = []
        A_supprimer = []
        
        for K, V in self.collection.items() :
            Dt = tActuel - V.tweets[len(V.tweets)-1][0] 
            if min_cascade_size <= len(V.tweets) and Dt >= termined:
                Value = {}
                Value['type'] = 'size'
                Value['cid'] = V.cid
                Value['n_tot'] = len(V.tweets)
                Value['t_end'] = V.tweets[len(V.tweets)-1][0]

                r = {}
                for Key in T_obs : 
                    r[Key] = Value
                resultat.append(r)
                A_supprimer.append(K)
        
        for j in A_supprimer:
            del self.collection[j]

        return resultat

    @property
    def get_collection(self):
        return self.collection