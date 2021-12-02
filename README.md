# Tweetoscope

This project is part of the software Application engineering class given in Mathematics and Data Science Major and supervised by Virginie Galtier. Tweetoscope is a tool used to predict the popularity of artificially generated tweets.

## Core architecture

![architecture](https://pennerath.pages.centralesupelec.fr/tweetoscope/graphviz-images/ead74cb4077631acad74606a761525fe2a3228c1.svg)

The red boxes are processings step, which are dockerised. The ellipses represent kafka topics and the white boxes are optional visual tools not implemented in this project.

- The tweet generator is written in C++ and simulates real time tweets and retweets
- The tweet collector uses the tweets topic and groups tweets into cascades
- The Hawkes estimator estimates the parameters of a Hawkes process given its partial time series
- The predictor predict the popularity of tweets given the parameters given by the estimator
- The learner collects training sample and train a random forest used for prediction by the predictor
- The dashboard displays the 10-hottests tweets
- The monitor displays the performance of the system

## Launch the application on minikube

Minikube can be downloaded from [here](https://minikube.sigs.k8s.io/docs/start/). <br>
In order to deploy the application on minikube the only requirement is the yml files [minikube_deploiement_zookeper_kafka.yml](https://gitlab-student.centralesupelec.fr/tweetos-buddies/tweetoscope/-/blob/c6911c6f19e38dc0cd659a8b9161104e9d736e24/Deploiement/minikube/minikube_deploiement_zookeper_kafka.yml) and [minikube_deploiement_code.yml](https://gitlab-student.centralesupelec.fr/tweetos-buddies/tweetoscope/-/blob/c6911c6f19e38dc0cd659a8b9161104e9d736e24/Deploiement/minikube/minikube_deploiement_code.yml).

```
minikube start
kubectl apply -f .\minikube_deploiement_zookeper_kafka.yml
kubectl apply -f .\minikube_deploiement_code.yml
```

The 10 hottests tweets can be seen in the dashboard logs.

## Launch the application on cluster

Le déploiement du projet a été fait sur les clusters de l'école CentraleSupélec. <br>
Nous avons utilisé Kubernetes pour le faire. <br>
Le dossier Deploiement au niveau de la racine du projet contient les deux fichiers permettant de déployer le projet et vous n'aurez pas à le télécharger car il se trouve déjà sur le cluster de l'école. <br>
Nous avons travaillé sur le cluster ayant pour identifiant cpusdi1_36 en utilisant l'application DCE qui peut être téléchargé sur le site : https://tutos.metz.centralesupelec.fr/TPs/Dcejs/index.html
<br>
Après avoir suivi toutes les consignes, une fois sur le cluster de l'école (cpusdi1_36) faites :

```
cd coucou #Ce dossier contient les deux fichiers qui se trouvent dans le dossier Deploiement
ssh ic45
kubectl -n cpusdi1-36-ns apply -f .\deploiement_zookeper_kafka.yml
kubectl -n cpusdi1-36-ns apply -f .\deploiement_code.yml

kubectl -n cpusdi1-36-ns get pods -o wide #Voir tous les pods qui viennent d'être créés.
kubectl -n cpusdi1-36-ns -f logs NOM_DU_POD #Pour voir les logs du pod
```

## Students

- Oussama El M'Tili <br>
- Divin Kimala <br>
- Akiyo Worou <br>
