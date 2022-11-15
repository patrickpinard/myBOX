# Auteur  : Patrick Pinard 
# Date    : 20.9.2022
# Objet   : Gestion du module Relais 
# Source  : myRelayLib.py
# Version : 1
# -*- coding: utf-8 -*-

#   Clavier MAC :      
#  {} = "alt/option" + "(" ou ")"
#  [] = "alt/option" + "5" ou "6"
#   ~  = "alt/option" + n    
#   \  = Alt + Maj + / 

# VERBOSE = affichage étendu dans fichier log.     
##################################################
#           P26 ----> Relay_Ch1
#			P20 ----> Relay_Ch2
#			P21 ----> Relay_Ch3
##################################################
#!/usr/bin/python


import RPi.GPIO as GPIO
from myLOGLib  import LogEvent, VERBOSE
from time import sleep

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

class RelayBoard(object):
    """
    Classe definissant un module de 3 relais caracterisé par les méthodes : 
        - on  : fermeture du relai 
        - off : ouverture du relai 
    """

    def __init__(self, name):
        """
        Constructeur de la classe RelayBoard: 
        """

        self.name = name     
    
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Relay_Ch1,GPIO.OUT)
        GPIO.setup(Relay_Ch2,GPIO.OUT)
        GPIO.setup(Relay_Ch3,GPIO.OUT)   
        if VERBOSE : LogEvent("Création de l'objet RelayBoard " )
        self.off(1)
        self.off(2)
        self.off(3)     
        self.Relay1_state = False
        self.Relay2_state = False    
        self.Relay3_state = False                                        
        if VERBOSE : LogEvent("Tous les relais en mode ouverts (OFF)." )
                                 
    def __repr__(self):

        """
        Méthode permettant d'afficher les paramètres principaux du relai.
        """

        return "\nRelay Information : \n name : {}".format(self.name )

    def on(self, relayid):

        """
        Méthode permettant de fermer (on) le relai.
        GPIO pin LOW
        relayid = 1,2 ou 3
        """

        if relayid <1 or relayid >3: 
            if VERBOSE : LogEvent("Numéro de relai invalide !  #:" + str(relayid) + " Relayid doit être compris entre 1 et 3."  ) 
            return

        if relayid == 1: 
            GPIO_PIN = Relay_Ch1
            self.Relay1_state = True
        
        if relayid == 2:
            GPIO_PIN = Relay_Ch2
            self.Relay2_state = True
           
        if relayid == 3: 
            GPIO_PIN = Relay_Ch3 
            self.Relay3_state = True    
        
        GPIO.output(GPIO_PIN,GPIO.LOW)

        #if VERBOSE : LogEvent("Relai " + str(relayid) + " activé (ON)."  ) 

        return  

    def off(self, relayid):

        """
        Méthode permettant d'ouvrir (off) le relai.
        GPIO pin HIGH
        relayid = 1,2 ou 3
        """
        if relayid <1 or relayid >3: 
                if VERBOSE : LogEvent("Numéro de relai invalide !  #:" + str(relayid) + " Relayid doit être compris entre 1 et 3."  ) 
                return
                
        if relayid == 1: 
            GPIO_PIN = Relay_Ch1
            self.Relay1_state = False
            
        if relayid == 2:
            GPIO_PIN = Relay_Ch2
            self.Relay2_state = False
            
        if relayid == 3: 
            GPIO_PIN = Relay_Ch3
            self.Relay3_state = False
        
        GPIO.output(GPIO_PIN,GPIO.HIGH)
		
        #if VERBOSE : LogEvent("Relai " + str(relayid) + " désactivé (OFF)."  ) 

        return

    def get_state(self, relayid):

        """
        Méthode permettant de connaitre l'état d'un relai.
        relayid = 1,2 ou 3
        """
        if relayid <1 or relayid >3: 
                if VERBOSE : LogEvent("Numéro de relai invalide !  #:" + str(relayid) + " Relayid doit être compris entre 1 et 3."  ) 
                return 0
                
        if relayid == 1: 
            return self.Relay1_state
            
        if relayid == 2:
            return self.Relay2_state
            
        if relayid == 3: 
            return self.Relay3_state



if __name__ == "__main__":

    LogEvent(" ---- test de la librairie  -----")
    Relay = RelayBoard("relayBoard")
    Relay.on(1)
    Relay.on(2)
    Relay.on(3)
    LogEvent(" Activation (ON) des 3 relais")
    sleep(5)
    Relay.off(1)
    Relay.off(2)
    Relay.off(3)
    LogEvent(" Désactivation (OFF) des 3 relais")
    sleep(1)
    LogEvent("Remise à zéro des GPIO")
    GPIO.cleanup()
    LogEvent(" ---- fin test de la librairie  -----")

