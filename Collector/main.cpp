#include "tweetoscopeCollectorParams.hpp"
#include <iostream>
#include <ostream>
#include <cppkafka/cppkafka.h>
#include <Processor.hpp>

int main(int argc, char *argv[])
{

  if (argc != 2)
  {
    std::cout << "Usage : " << argv[0] << " <config-filename>" << std::endl;
    return 0;
  }
  tweetoscope::params::collector params(argv[1]);
  std::cout << std::endl
            << "Parameters : " << std::endl
            << "----------" << std::endl
            << std::endl
            << params << std::endl
            << std::endl;

  auto brokers = params.kafka.brokers;
  auto in = params.topic.in;
  auto out_series = params.topic.out_series;
  auto out_properties = params.topic.out_properties;
  auto time1_obs = params.times.observation;
  auto time2_obs = params.times.observation2;
  auto terminated = params.times.terminated;
  auto min_cascade_size = params.cascade.min_cascade_size;

  //Creons le processeur
  Processor processeur;

  // Create the config
  cppkafka::Configuration config = {
      {"bootstrap.servers", brokers},
      {"auto.offset.reset", "earliest"},
      {"group.id", "myOwnPrivateCppGroup"}};

  // Create the consumer
  cppkafka::Consumer consumer(config);
  consumer.subscribe({in});

  // Create the producer
  cppkafka::Producer producer(config);
  cppkafka::MessageBuilder builder1(out_series);
  cppkafka::MessageBuilder builder2(out_properties);

  // Create a map of Processor
  std::map<tweetoscope::source::idf, Processor> cartes_Processeur;

  while (true)
  {
    auto msg = consumer.poll();
    if (msg && !msg.get_error())
    {
      tweetoscope::tweet twt;
      auto key = std::to_string(tweetoscope::cascade::idf(std::stoi(msg.get_key())));
      auto istr = std::istringstream(std::string(msg.get_payload()));
      istr >> twt;

      if (cartes_Processeur.find(twt.source) == cartes_Processeur.end())
      {
        //source not found

        //We create a processor and add tweet in a cascade
        Processor p;
        p.add_tweet_in_cascade(key, time1_obs, time2_obs, min_cascade_size, terminated, twt);

        cartes_Processeur.insert(std::pair<tweetoscope::source::idf, Processor>(twt.source, p));
      }
      else
      {
        //source was found

        //Add tweet in a cascade
        cartes_Processeur[twt.source].add_tweet_in_cascade(key, time1_obs, time2_obs, min_cascade_size, terminated, twt);
      }

      std::vector<Cascade> Cascades_partielles;
      std::vector<Cascade> Cascades_finies;

      map<string, int>::iterator it;

      for (it = symbolTable.begin(); it != symbolTable.end(); it++)
      {
        std::cout << it->first // string (key)
                  << ':'
                  << it->second // string's value
                  << std::endl;
      }

      for (auto &it : cartes_Processeur.begin(); it != cartes_Processeur.end(); it++)
      {
        Cascades_partielles(push_back((it->second).cascade_partielles(time1_obs)));
        Cascades_partielles(push_back((it->second).cascade_partielles(time2_obs)));
        Cascades_finies.push_back((it->second).cascades_termine(terminated, min_cascade_size));
      }

      std::ostringstream ostr1;
      std::ostringstream ostr2;

      std::string message1{twt.str()};
      std::string message2{twt.str()};

      builder1.key(key);
      builder1.payload(message1);

      builder2.key(key);
      builder2.payload(message2);

      try
      {
        if (time1_obs - twt.time >= 0) //Premiere fenetre d observation, on envoie
        {
          producer.produce(builder1);
        }
        else if (time2_obs - twt.time = > 0) //Deuxieme fenetre d observation, on envoie
        {
          producer.produce(builder1);
        }

        if (terminated - twt.time <= 0) //On suppose que la cascade est terminéee
        {
          producer.produce(builder2);
        }
      }
      catch (const cppkafka::HandleException &e)
      {
        std::ostringstream ostr2;
        ostr2 << e.what();
        std::string error{ostr2.str()};
        if (error.compare("Queue full") != 0)
        {
          std::chrono::milliseconds timeout(3000);
          producer.flush(timeout);
          producer.produce(builder);
        }
        else
        {
          std::cout << "something went wrong: " << e.what() << std::endl;
        }
      }
      std::chrono::milliseconds timespan(1000);
      std::this_thread::sleep_for(timespan);
    }
  }

  return 0;
}
