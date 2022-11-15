# Auteur  : Patrick Pinard 
# Date    : 11.10.2022
# Objet   : Gestion de la sonde T&H DHT22 de Grove (Seedstudio)
# Source  : myDHT22Lib.py
# Version : 1
# -*- coding: utf-8 -*-

#   Clavier MAC :      
#  {} = "alt/option" + "(" ou ")"
#  [] = "alt/option" + "5" ou "6"
#   ~  = "alt/option" + n    
#   \  = Alt + Maj + / 

#!/usr/bin/python


import myLOGLib  
import grovepi
import time

DHT_SENSOR_PIN = 4

class DHT22(object):
    """
    Classe definissant une sonde de T & H de type DHT22 caracterisé par les méthodes : 
        - read_temperature  : 
        - read_humidity     :  
    """

    def __init__(self, DHT_SENSOR_PIN):
        """
        Constructeur de la classe DHT22: 
        1 = white
        0 = blue
        """

        self.sensor = grovepi.dht(DHT_SENSOR_PIN,1)
        if myLOGLib.VERBOSE : myLOGLib.LogEvent("Création de l'objet DHT22 " )
        

    def read(self):

        """
        Méthode permettant de lire la température en °C et humidité en %hr
        """

        try:
            T,H = self.sensor  
        except IOError:
            myLOGLib.LogEvent("Erreur lecture DHT22")
            return 0,0
        return T,H


if __name__ == "__main__":

    thsen = DHT22(DHT_SENSOR_PIN)
    while (1):
        try : 
            print("----  lecture DHT22 ----")
            T,H = thsen.read()
            print("T = ", T, "  H = ", H)
            time.sleep(3)
        except OSError as err:
            print ("erreur lecture DHT22 : " + + str(err))
            break


