# Auteur  : Patrick Pinard 
# Date    : 19.4.2022
# Objet   : sondes de température, humidité et anémomètre.
# Source  : mySensorsLib.py
# Version : 1.2  (ajout capteur humidité air SparkFin HIH-4030=
# Changes : revue code pour accès aux fichiers des sondes DS18B20 car lib DS18B20 -> erreur

# -*- coding: utf-8 -*-

#   Clavier MAC :      
#  {} = "alt/option" + "(" ou ")"
#  [] = "alt/option" + "5" ou "6"
#   ~  = "alt/option" + n    
#   \  = Alt + Maj + / 

VERBOSE = False     # affichage de tous des log 

from myLOGLib  import LogEvent
import glob, time
import traceback


class DS18B20(object):

    """
    Classe pour sondes de températures de type DS18B20 : 
    Emplacement des fichiers : /sys/bus/w1/devices/28*/w1_slave
    """

    def __init__(self):
        """
        Constructeur de la classe sonde de températures : 

        - name  : nom de la sonde 
        - id : identifiant de la sonde (0 : interne ou 1:externe)
        - unit : l'unité de mesure (string, par defaut °Celsius)
        - type : type de sonde (i.e : DS18B20)
        
        """
                
        LogEvent("Création de l'objet DS18B20" )

        self.id   = 1
        self.name = "sondes de température de l'air"                                                 
        self.type = "DS18B20" 
        self.unit = '°Celsius'
        self.values = []

                                                     
                                         
    def __repr__(self):

        """
        Méthode permettant d'afficher les paramètres principaux d'une sonde de température.
        """

        return "\nSensor Information : \n name   : {}\n type   : {}\n   id   : {}\n unit   : {} \n value  : {} ".format(self.name, self.type, self.id, self.unit, self.value)
    
    def read(self):

        """
        Méthode permettant de lire la température de la sonde DS18B20.
        Retourne la température dans une liste sous self.values et 
        la température de la première sonde détectée.
        """

        routes_capteurs = glob.glob("/sys/bus/w1/devices/28*/w1_slave")
        t = []

        # les sondes sont crées avec identifiant unique de type 28-3c01d0750cbe 
        # -> ../../../devices/w1_bus_master1/28-3c01d0750cbe
        # et l'autre identifiant : 28-3c01e0763559 
        # glob permet de retourner la liste des répertoires avec le prefix demandé 

        if len(routes_capteurs) > 0 :
            c = 1  #nombre de routes = nombre de capteurs
            for capteur in routes_capteurs :

                # fichier w1_slave contient le relevé de température

                try:
                    file = open(capteur)
                    content = file.read()
                    file.close()
                except : 
                    raise LogEvent("ERREUR : lecture du fichier températures : " + (capteur))

                # contenu texte du fichier du type : 
                # 6c 01 55 05 7f a5 81 66 56 : crc=56 YES
                # 6c 01 55 05 7f a5 81 66 56 t=22750

                try:
                    line = content.split("\n")[1]
                    temperature = line.split(" ")[9]
                except : 
                    raise LogEvent("ERREUR : lecture du contenu fichier de températures : " + (content)) 
                temperature = float(temperature[2:]) / 1000
                t.append(round(temperature,2))
                c += 1
        else :
            LogEvent("ERREUR : Aucune sonde détectée. Vérifier les branchements.")
        self.values = t
        return t[0]
            

   
if __name__ == "__main__":

    T = DS18B20()
    print(" --- lecture de la température sur sonde DS18B20  toutes les 5 secondes ---")
    while True:
        try : 
            t = T.read()[0]
            print("Température [°C]: ", t)
            LogEvent("Température [°C]: " + str(t))
            time.sleep(5)
        except:
            traceback.print_exc()
            print ("erreur lecture sonde DS18B20")
            break
   







