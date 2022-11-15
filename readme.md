# MyBOX 

MyBox est un boitier constitué d'un Raspberry Pi 4 avec 3 relais 240V et 8 ports d'acquisitions analogiques sur lesquels sont connectés des sondes de températures, d'humidité de l'air notamment.
Il permet d'activer différentes prises 240V :
    - lumière
    - chauffage avec themrostat
    - prise avec planfication d'heure d'activation et arrêt

![](/images/mybox.png) 
![](/images/logo.png)

## l'APP myBOX 

![](/images/capteurs.png) 

![](/images/actionneurs.png) 

![](/images/events.png) 

![](/images/events.png) 


## Matériel

## Raspberry PI 4 : 

https://www.pi-shop.ch/raspberry-pi-4-starter-kit-pi-4-8gb

![](/images/raspi.png)

## Boitier : 

https://www.distrelec.ch/fr/boitier-plastique-polycarbonate-couvercle-charniere-transparent-390x167x316mm-ip65-fibox-pc-36-31-enclosure/p/15058771?q=TABLEAU+ELECTRIQUE&pos=3&origPos=3&origPageSize=50&track=true

![](/images/boitier.png)

## Sonde température : 

https://www.pi-shop.ch/waterproof-ds18b20-digital-temperature-sensor-extras

![](/images/ds18b20.jpg)

## Sonde humidité d'air : 

...Sondes AM2315...

![](/images/am2315.png)


## Alimentations 5 & 12  V : 

https://www.galaxus.ch/fr/s1/product/weidmueller-pro-insta-60w-12v-5a-alimentatore-switching-12-vdc-5-a-60-w-60-w-alimentations-pc-15915900?supplier=4867603

https://www.galaxus.ch/fr/s1/product/weidmueller-koppelrelais-10-st-24-vdc-6-relais-8436567?supplier=4909783#gallery-open

![](/images/alim5-12-24V.jpg)


## Module 3 relais : 

![](/images/3relayboard.jpg)

## Convertisseur A/D (ADC) : 

https://www.distrelec.ch/fr/adc-canaux-12-bits-pour-raspberry-pi-seeed-studio-103030280/p/30135129?track=true&no-cache=true&marketingPopup=false

![](/images/ADC.png)

## Montage du tableau

![](/images/mybox.jpg)


## API's

Les API vont permettre de commander le boitier via des requêtes http depuis une APP PWA.

Exemple :

GET   http://mybox.ppdlab.ch/light

retourne le status du relai de lumière au format JSON 
{"LIGHT":false}


URL principale : 
http://mybox.ppdlab.ch

| Verb    |   URL           | Arg     |  Description                                         |
|---------|-----------------|---------|-------------------------------------------------------
| GET     | /main           |  -      | page principale                                      |
| GET     | /light          |  -      | retourne l'état de la lumière (allumé/étient)        |
| GET     | /actionneurs    |  -      | retourne l'état de switches de commandes             |
| GET     | /capteurs       |  -      | retourne les valeurs mesurées (Ti, Te, He)           |
| GET     | /thermostat/auto|  -      | retourne l'état du mode automatique du thermostat    |
| GET     | /thermostat     |  -      | retourne les valeurs et état du thermostat           | 
...


## Interface Web

L'interface web Progressive (PWA) est crée en Flask/Bootrap/Javascript & Ajax. 


