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
    //std::map<tweetoscope::timestamp, std::weak_ptr<ref>> fifo_collection2;

    //Collection3
    //std::map<tweetoscope::source::idf, std::weak_ptr<ref>> collection3;

public:
    std::vector<Cascade> add_tweet_in_cascade(std::string key, int T_obs, int T_obs2 int min_cascade_size, int termined, tweetoscope::tweet &t)
    {
        auto source = t.source;
        auto type = t.type;
        auto msg = t.msg;
        auto m = t.magnitude;
        auto t = t.time;
        auto info = t.info;

        if (queue_file_d_attente.size() == 0)
        {
            std::vector<std::array<double, 2>> tweets;
            tweets.push_back({t, m});
            auto ref1 = make_cascade(type, key, msg, T_obs, tweets);
            queue_file_d_attente.push(ref1);

            /*fifo_collection2[T_obs] = ref1;
            fifo_collection2[T_obs2] = ref1;
            collection3[source] = ref1;*/
        }
        else
        {
            for (auto &c : queue_file_d_attente)
            {
                if (c.cid == key)
                {
                    c.tweets.push_back({t, m});
                    /*fifo_collection2[T_obs] = c;
                    fifo_collection2[T_obs2] = c;
                    collection3[source] = c;*/
                    break;
                }
            }
        }

        return cascades_termine(termined, min_cascade_size, t);
    }

    std::vector<Cascade> cascade_partielles(int T_obs)
    {
        std::vector<Cascade> resultat;
        for (auto &c : fifo_collection2)
        {
            if (min_cascade_size <= c.tweets.size() && c.(tweets.end() - 1).first() >= T_obs)
            {
                Cascade d{c.type, c.cid, c.msg, c.T_obs, c.tweets};
                resultat.push_back(d);
            }
        }
        return resultat;
    }

    std::vector<Cascade> cascades_termine(int termined, int min_cascade_size, int temps)
    {
        std::vector<Cascade> resultat;
        for (auto &c : queue_file_d_attente)
        {
            if (min_cascade_size <= c.tweets.size() && (temps - c.(tweets.end() - 1).first()) >= termined)
            {
                Cascade d{c.type, c.cid, c.msg, c.T_obs, c.tweets};
                resultat.push_back(d);
                queue_file_d_attente.erase(c);
            }
        }
        return resultat;
    }
};

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
