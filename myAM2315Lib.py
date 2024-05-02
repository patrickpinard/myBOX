# Auteur  : Patrick Pinard 
# Date    : 4.10.2022
# Objet   : Gestion de la sonde T&H AM2315
# Source  : myAM2315Lib.py
# Version : 1
# -*- coding: utf-8 -*-

#   Clavier MAC :      
#  {} = "alt/option" + "(" ou ")"
#  [] = "alt/option" + "5" ou "6"
#   ~  = "alt/option" + n    
#   \  = Alt + Maj + / 

#!/usr/bin/python


from myLOGLib  import LogEvent, VERBOSE
import AM2315LIB
import time
import traceback


class AM2315(object):
    """
    Classe definissant une sonde de T & H de type AM2315 caracterisé par les méthodes : 
        - read_temperature  : 
        - read_humidity     :  
    """

    def __init__(self):
        """
        Constructeur de la classe AM2315: 
        """

        self.sensor = AM2315LIB.AM2315(powerpin=6)
        if VERBOSE : LogEvent("Création de l'objet AM2315 " )
        

    def read_temperature(self):

        """
        Méthode permettant de lire la température en °C.
        """

        try : 
            t= round(self.sensor.read_temperature(),1)
            return t
        except:
            traceback.print_exc()
            LogEvent("ERREUR lecture température sur sonde H AM2315")
            return 0

    def read_humidity(self):

        """
        Méthode permettant de lire l'humidité de l'air en %HR.
        """

        try : 
            t= round(self.sensor.read_humidity(),1)
            return t
        except:
            traceback.print_exc()
            LogEvent("ERREUR lecture humidité sur sonde AM2315")
            return 0

    


if __name__ == "__main__":

    thsen = AM2315()
    while (1):
        try : 
            print("----  lecture AM2315 ----")
            print ("T   ", thsen.read_temperature())
            print ("H   ", thsen.read_humidity())
            time.sleep(3)
        except:
            traceback.print_exc()
            print ("erreur lecture AM2315")
            break


