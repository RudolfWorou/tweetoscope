#include <memory>
#include <tweetoscopeCollectorParams.hpp>
#include <Tweet_class.cpp>
#include <map>
#include <memory>
#include <queue>
#include <boost/heap/binomial_heap.hpp>

using namespace boost::heap;

string Cascade;

using ref = std::shared_ptr<Cascade>;
using priority_queue = binomial_heap<ref, compare<element_ref_comparator>>;

bool element_ref_comparator::operator()(ref op1, ref op2) const;
ref make_cascade(std::string type,
                 std::string cid,
                 std::string msg,
                 int T_obs,
                 std::vector<std::array<double, 2>> tweets);
ref make_cascade(const Cascade &c);

struct Cascade
{
    std::string type;
    std::string cid;
    std::string msg;
    int T_obs;
    std::vector<std::array<double, 2>> tweets; //Représente (t,m)
};

class Processor
{
private:
    //Collection1
    priority_queue::handle_type queue_file_d_attente;

    //Collection2
    std::map<tweetoscope::timestamp, std::queue<std::weak_ptr<ref>>> fifo_collection2;

    /*

    Collection3 

    agit comme une table de symboles, de sorte que
    l'obtention de l'instance de la cascade à partir de son identifiant est facile.
    
    */

    std::map<std::string idef, std::weak_ptr<ref>> collection3;

public:
    /*
    
    Ajoute une nouvelle cascade ou un nouveau tweet(retweet) dans un processus connaissant sa source
    
    */

    void add_tweet_in_cascade(std::string key, int T_obs, int T_obs2 int min_cascade_size, int termined, tweetoscope::tweet &t)
    {

        auto source = t.source;
        auto type = t.type;
        auto msg = t.msg;
        auto m = t.magnitude;
        auto t = t.time;
        auto info = t.info;

        if (type == "tweet")
        {
            std::vector<std::array<double, 2>> tweets;
            tweets.push_back({t, m});
            auto ref1 = make_cascade(type, key, msg, T_obs, tweets);
            queue_file_d_attente.push(ref1);

            fifo_collection2[T_obs].enqueue(ref1);
            fifo_collection2[T_obs2].enqueue(ref1);
            collection3[key] = ref1;
        }
        else
        {
            //C'est un retweet
            bool cascade_exist = !(collection3.find(key) == collection3.end());

            if (cascade_exist)
            {
                auto cascade = collection3[key];
                cascade.tweets.push_back({t, m});
                fifo_collection2[T_obs].enqueue(cascade);
                fifo_collection2[T_obs2].enqueue(cascade);
            }
        }
    }

    /*
    
    Retourne les cascades partielles à envoyer.
    
    */

    std::vector<Cascade> cascade_partielles(int T_obs)
    {
        std::vector<Cascade> resultat;
        for (auto &c : fifo_collection2[T_obs])
        {
            auto v = c.(tweets.end() - 1).first() - c.(tweets.begin() - 1).first();
            if (min_cascade_size <= c.tweets.size() && v >= T_obs)
            {
                Cascade d{c.type, c.cid, c.msg, c.T_obs, c.tweets};
                resultat.push_back(d);
            }
        }
        return resultat;
    }

    /*
    
    Retourne les cascades finales à envoyer.
    
    */
    std::vector<Cascade> cascades_termine(int termined, int min_cascade_size)
    {
        std::vector<Cascade> resultat;
        for (auto &c : queue_file_d_attente)
        {
            if (min_cascade_size <= c.tweets.size() && (c.(tweets.end() - 1).first() - termined) >= termined)
            {
                Cascade d{c.type, c.cid, c.msg, c.T_obs, c.tweets};
                resultat.push_back(d);
                queue_file_d_attente.erase(c);
            }
        }
        return resultat;
    }
};

/*
Les fonctions qui n'appartiennent pas à la classe Processor

                            ||
                            ||
                            ||
                            \/

*/

bool element_ref_comparator::operator()(ref op1, ref op2) const
{
    return *op1->(tweets.end() - 1).first() > *op2->(tweets.end() - 1).first();
}

ref make_cascade(std::string type,
                 std::string cid,
                 std::string msg,
                 int T_obs,
                 std::vector<std::array<double, 2>> tweets)
{
    return std::make_shared<Cascade>(type, cid, msg, T_obs, tweets);
}

ref make_cascade(const Cascade &c)
{
    return std::make_shared<Cascade>(c.type, c.cid, c.msg, c.T_obs, c.tweets);
}
