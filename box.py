# Auteur  : Patrick Pinard 
# Date    : 17.11.2022
# Objet   : Box Atelier
# Source  : box.py
# Version : 3.3

#   Clavier MAC :      
#  {} = "alt/option" + "(" ou ")"
#  [] = "alt/option" + "5" ou "6"
#   ~  = "alt/option" + n    
#   \  = Alt + Maj + / 
#   |  = alt/option + 7

# -*- coding: utf-8 -*-

import sys, os
sys.path.extend([f'./{name}' for name in os.listdir(".") if os.path.isdir(name)]) 
import myLCDLib
import myDS18B20Lib
import myRelayLib
import myAM2315Lib
from myLOGLib import LogEvent, eventlog
import myJSONLib
from myExtractLib import json_extract
from time import gmtime, sleep
import calendar
import datetime
from threading import Thread
from myJSONLib import writeJSONtoFile, readJSONfromFile
from flask import Flask, render_template, request, jsonify
import pickle

####### Paramètres généreaux de l'APP ###############

APPNAME             = "Box"
APPDATE             = "17/11/22"
APPVERSION          = "V3.3"
APPAUTHOR           = "Patrick Pinard"
APPPATH             = '/home/pi/box/'
DATAFILENAME        = APPPATH + "data.json"
CONFIG_FILENAME     = APPPATH + "config.json"
ALLDATAFILE         = APPPATH + 'alldata.dta'

####### Création de l'APPLICATION FLASK ###############

app = Flask(__name__)

##### Variables et valeurs par défaut#######

DHT_SENSOR_PIN       = 4                # PIN D4 sur board GrovePi
INTERVAL_LOOP        = 300              # interval de mesure automatique en sec.
INTERVAL_DISPLAY     = 5                # interval d'affichage sur écran OLED et LCD en sec
TMIN                 = 6                # température minimale pour activation chauffage
TMAX                 = 9                # température maximale pour coupure chauffage
HEATER_RELAY         = 1                # numéro du relai pour chauffage commandé par Thermostat
PLUG_RELAY           = 2                # relai pour PLUG commandé par Planificateur 
LIGHT_RELAY          = 3                # relai pour lumière
THERMOSTAT           = False            # thermostat pour chauffage
SCHEDULER            = False            # planificateur pour prise 240V 
SCHEDULER_START      = "00:00"          # heure de démarrage de l'activation de la prise PLUG_RELAY
SCHEDULER_STOP       = "00:00"          # heure d'arrêt de la prise PLUG_RELAY
HEATER               = False            # chauffage 
LIGHT                = False            # lumière
PLUG                 = False            # prise 240V
Te                   = 0                # température extérieure    
Ti                   = 0                # température intérieure
He                   = 0                # humidité extérieure
DATA                 = {}               # dernières données mesurées et paramètres enregistrés
ALL_DATA             = []               # ensemble des mesures et paramètres au format json
LASTREBOOT           = ""               # Date et heure du dernier reboot
USERNAME             = 'ADMIN'
LOCATION             = "Atelier"
ID                   = 0    
DEBUG                = False             # Mode DEBUG pour affichage détails dans eventlog
MAX_ALL_DATA_SIZE    = 1000              # Nombre de mesure gardée en mémoire

#### Info pour LOG file #######

LogEvent("***** " + APPNAME+ " " + APPVERSION + " " + APPAUTHOR + " " + APPDATE + " ******") 
now = datetime.datetime.now()
date = now.strftime("%-d.%-m")  
time = now.strftime("%H:%M:%S")  
dateandtime = date + " à " + time 
LASTREBOOT = dateandtime
LogEvent("Redémarrage le " + str(LASTREBOOT ))

##### Tuple des valeurs #######

time_stamp = calendar.timegm(gmtime())*1000
time_now   = datetime.datetime.now()

DATA = {        'ID'                : ID,
                'APPNAME'           : APPNAME, 
                'USERNAME'          : USERNAME,
                'APPDATE'           : APPDATE,
                'APPVERSION'        : APPVERSION,
                'APPAUTHOR'         : APPAUTHOR,
                'LASTREBOOT'        : LASTREBOOT,
                "TIMESTAMP"         : time_stamp,
                "DATE"              : time_now.strftime("%d.%m.%Y"),
                "TIME"              : time_now.strftime("%H:%M:%S"),
                "LOCATION"          : LOCATION,
                "Ti"                : Ti,
                "Te"                : Te,
                "He"                : He,
                'INTERVAL_LOOP'     : INTERVAL_LOOP,
                'INTERVAL_DISPLAY'  : INTERVAL_DISPLAY,
                'TMIN'              : TMIN,
                'TMAX'              : TMAX,
                'HEATER'            : HEATER,
                'HEATER_RELAY'      : HEATER_RELAY,
                'THERMOSTAT'        : THERMOSTAT,
                'LIGHT'             : LIGHT ,
                'LIGHT_RELAY'       : LIGHT_RELAY,
                'PLUG'              : PLUG,
                'PLUG_RELAY'        : PLUG_RELAY,
                'SCHEDULER'         : SCHEDULER,
                'SCHEDULER_START'   : SCHEDULER_START,
                'SCHEDULER_STOP'    : SCHEDULER_STOP,
                'DEBUG'             : DEBUG   
            }



#### Création des objects display, senseurs et actionneurs #######

AM2315  = myAM2315Lib.AM2315()                          # Température et Humidité de l'air extérieur
LCD     = myLCDLib.LCD()                                # Ecran LCD dans tableau
DS18B20 = myDS18B20Lib.DS18B20()                        # Température intérieure
RELAY   = myRelayLib.RelayBoard("")                     # Module 3 relais 240V sur Raspberry Pi 4

###### PWA files  #######################################

@app.route("/__service-worker.js", methods=['GET'])
def serviceworker():
        
    return app.send_static_file('__service-worker.js') 

@app.route("/__manifest.json", methods=['GET'])
def manifest():
        
    return app.send_static_file('__manifest.json') 


#### Info générales pour LOG file #######

def DisplayValues():
    
    global ID
    if DATA["DEBUG"] : 
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
    
        LogEvent("Fréquence de lecture capteurs   :  " + str(DATA["INTERVAL_LOOP"]) + " sec.") 
        LogEvent("Fréquence d'affichage écran     :  " + str(DATA["INTERVAL_DISPLAY"]) + " sec.")
        LogEvent("Chauffage   (ON/OFF)            :  " + str(DATA["HEATER"]))
        LogEvent("Thermostat  (ON/OFF)            :  " + str(DATA["THERMOSTAT"]))
        LogEvent("  Température minimum           :  " + str(DATA["TMIN"]) + " °C")
        LogEvent("  Température maximum           :  " + str(DATA["TMAX"]) + " °C")
        LogEvent("Lumière     (ON/OFF)            :  " + str(DATA["LIGHT"]))
        LogEvent("Prise 240V  (ON/OFF)            :  " + str(DATA["PLUG"]))
        LogEvent("Scheduler   (ON/OFF)            :  " + str(DATA["SCHEDULER"]))
        LogEvent("  Scheduler start[hh:mm]        :  " + str(DATA["SCHEDULER_START"]))
        LogEvent("  Scheduler stop [hh:mm]        :  " + str(DATA["SCHEDULER_STOP"]))
        LogEvent("Température extérieure          :  " + str(DATA["Te"]) + " °C")
        LogEvent("Humidité extérieure             :  " + str(DATA["He"]) + " °C")
        LogEvent("Température intérieure          :  " + str(DATA["Ti"]) + " °C")
       

####  AFFICHAGES SUR ECRANS LCD ####

def LCD_display_state():
    
    global ID, DATA

    try:

        # AFFICHAGE SUR ECRAN LCD DES PARAMETRES ET VALEURS MESUREES
        
        # EVENT ID
        LCD.setText("EVENT: " + str(ID) + "\nTIME : " + str(DATA["TIME"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))
  
        # VALEURS MESUREES EXTERIEURE
        LCD.setText("Te:" + (str(DATA["Te"])) + " Celsius\nHe:" + (str(DATA["He"])) + " %HR")
        sleep(int(DATA["INTERVAL_DISPLAY"]))

        # VALEUR MESUREE INTERIEURE
        LCD.setText("Ti:" + str(DATA["Ti"]) + " Celsius")
        sleep(int(DATA["INTERVAL_DISPLAY"]))

        # THERMOSTAT
        LCD.setText("THERMOSTAT:" + str(DATA["THERMOSTAT"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))
        LCD.setText("THERMOSTAT \nMIN:" + (str(DATA["TMIN"])) + " MAX:" + (str(DATA["TMAX"])))
        sleep(int(DATA["INTERVAL_DISPLAY"]))

        # CHAUFFAGE
        LCD.setText("HEATER:" + str(DATA["HEATER"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))
        
        # LUMIERE
        LCD.setText("LIGHT:" + str(DATA["LIGHT"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))

        # PLANIFICATEUR
        LCD.setText("SCHEDULER:" + str(DATA["SCHEDULER"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))
        LCD.setText("START:" + str(DATA["SCHEDULER_START"]) + "\nSTOP :" + str(DATA["SCHEDULER_STOP"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))


        # PRISE 240V SUR PLANIFICATEUR
        LCD.setText("PLUG:" + str(DATA["PLUG"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))

        # LUMIERE
        LCD.setText("LIGHT:" + str(DATA["LIGHT"]))
        sleep(int(DATA["INTERVAL_DISPLAY"]))

    except OSError as err:
                LogEvent("ERREUR d'affichage sur écran LCD ! Message : " + str(err))

####  SAUVEGARDE & CHARGEMENT DES PARAMETRES DE CONFIGURATIONS ####

def SaveParametersToFile():
    '''
    Sauvegarde des paramètres dans fichier : <CONFIG_FILENAME>
    '''

    config_parameters = {'INTERVAL_LOOP'    : DATA["INTERVAL_LOOP"],
                         'INTERVAL_DISPLAY' : DATA["INTERVAL_DISPLAY"],
                         'THERMOSTAT'       : DATA["THERMOSTAT"],
                         'TMIN'             : DATA["TMIN"],
                         'TMAX'             : DATA["TMAX"],
                         'HEATER_RELAY'     : DATA["HEATER_RELAY"],
                         'HEATER'           : DATA["HEATER"],
                         'SCHEDULER_START'  : DATA["SCHEDULER_START"],
                         'SCHEDULER_STOP'   : DATA["SCHEDULER_STOP"],
                         'SCHEDULER'        : DATA["SCHEDULER"],
                         'LIGHT'            : DATA["LIGHT"],
                         'LIGHT_RELAY'      : DATA["LIGHT_RELAY"],
                         'PLUG'             : DATA["PLUG"],
                         'PLUG_RELAY'       : DATA["PLUG_RELAY"],
                         'DEBUG'            : DATA["DEBUG"] 
                        }

    if DATA["DEBUG"] : LogEvent("DEBUG - Config parameters saved : " + str(config_parameters))

    if writeJSONtoFile(CONFIG_FILENAME, config_parameters):
        
        if DATA["DEBUG"] : LogEvent("Sauvegarde des paramètres de configuration sur fichier : " + CONFIG_FILENAME)
        return
    else: 
        LogEvent("Erreur de sauvegarde des paramètres de configuration sur fichier : " + CONFIG_FILENAME)

    return
    
def LoadParametersFromFile():
    '''
    Chargement des paramètres de configuration depuis fichier : <CONFIG_FILENAME>
    '''
   
    config_parameters = []
    
    validConfig, config_parameters = readJSONfromFile(CONFIG_FILENAME)

    if validConfig :     
        LogEvent("Chargement des paramètres de configuration depuis fichier : " + CONFIG_FILENAME)
                
        DATA["INTERVAL_LOOP"]    = int(config_parameters['INTERVAL_LOOP'])
        DATA["INTERVAL_DISPLAY"] = int(config_parameters['INTERVAL_DISPLAY'])
        DATA["TMIN"]             = float(config_parameters['TMIN'])
        DATA["TMAX"]             = float(config_parameters['TMAX'])
        DATA["HEATER_RELAY"]     = int(config_parameters['HEATER_RELAY'])
        DATA["HEATER"]           = config_parameters['HEATER']
        DATA["THERMOSTAT"]       = config_parameters['THERMOSTAT']
        DATA["SCHEDULER"]        = config_parameters['SCHEDULER']
        DATA["SCHEDULER_START"]  = config_parameters["SCHEDULER_START"]
        DATA["SCHEDULER_STOP"]   = config_parameters["SCHEDULER_STOP"]     
        DATA["LIGHT"]            = config_parameters["LIGHT"]     
        DATA["LIGHT_RELAY"]      = int(config_parameters["LIGHT_RELAY"])
        DATA["PLUG"]             = config_parameters["PLUG"]     
        DATA["PLUG_RELAY"]       = int(config_parameters["PLUG_RELAY"])
        DATA["DEBUG"]            = bool(config_parameters['DEBUG'])
       
        if DATA["DEBUG"] :  LogEvent("DEBUG - Config Parameters loaded : " + str(config_parameters))  
        
    else: 
        LogEvent("Fichier inexistant, chargement des paramètres de configuration par défaut.")

    return

def SaveState():

    global ALL_DATA

    GMT = gmtime()
    time_stamp = calendar.timegm(GMT)*1000
    state = {   'ID'                : ID,
                'APPNAME'           : APPNAME, 
                'USERNAME'          : USERNAME,
                'APPDATE'           : APPDATE,
                'APPVERSION'        : APPVERSION,
                'APPAUTHOR'         : APPAUTHOR,
                'LASTREBOOT'        : LASTREBOOT,
                "TIMESTAMP"         : time_stamp,
                "DATE"              : DATA["DATE"], 
                "TIME"              : DATA["TIME"], 
                "LOCATION"          : LOCATION,
                "Ti"                : DATA["Ti"],
                "Te"                : DATA["Te"],
                "He"                : DATA["He"],
                'INTERVAL_LOOP'     : DATA["INTERVAL_LOOP"],
                'INTERVAL_DISPLAY'  : DATA["INTERVAL_DISPLAY"],
                'TMIN'              : DATA["TMIN"],
                'TMAX'              : DATA["TMAX"],
                'HEATER'            : DATA["HEATER"],
                'HEATER_RELAY'      : DATA["HEATER_RELAY"],
                'THERMOSTAT'        : DATA["THERMOSTAT"],
                'LIGHT'             : DATA["LIGHT"] ,
                'LIGHT_RELAY'       : DATA["LIGHT_RELAY"],
                'PLUG'              : DATA["PLUG"],
                'PLUG_RELAY'        : DATA["PLUG_RELAY"],
                'SCHEDULER'         : DATA["SCHEDULER"],
                'SCHEDULER_START'   : DATA["SCHEDULER_START"],
                'SCHEDULER_STOP'    : DATA["SCHEDULER_STOP"],
                'DEBUG'             : DATA["DEBUG"]     
            }
    
    
    ALL_DATA.append(state)

    l = len(ALL_DATA)
    if l > MAX_ALL_DATA_SIZE-1: 
        ALL_DATA.pop(0)

    
    if DATA["DEBUG"] : 
        LogEvent("DEBUG : Etat sauvegardé : " + str(state))
        LogEvent("Nombre de mesures enregistrées : " + str(l))

    myJSONLib.writeJSONtoFile(DATAFILENAME, ALL_DATA)

##### THREADS #######

class Display (Thread):

   def __init__(self, threadID, name):
      Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      
   def run(self):
    LogEvent("Thread " + self.name + " started") 
    LCD.setText(APPNAME+ " " + APPVERSION + "\nLecture ...")
    sleep(int(DATA["INTERVAL_DISPLAY"]))
    while True : 
            try:
                LCD_display_state()
            except OSError as err:
                LogEvent("ERREUR : thread DISPLAY ! Message : " + str(err))

class Loop (Thread):
    
    def __init__(self, threadID, name):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        global DATA
        err = 0
        LogEvent("Thread " + self.name + "    started")       
        while True:     
            waiting = True
            i=0                   
            try :  
                ReadSensorsValues()
                SetThermostat() 
                DisplayValues()
                SaveState()
                SaveData()
                while waiting:
                    i= i+1
                    if i<int(DATA["INTERVAL_LOOP"]):
                        sleep(1)
                    else:
                        waiting = False        
            except OSError as err:
                LogEvent("ERREUR : thread Loop ! Message : " + str(err))      
                err = err + 1
                if err > 3 :
                    LogEvent("ERREURS MULTIPLES ! STOP THREAD LOOP")  
                    break         

class FlaskApp (Thread):

   def __init__(self, threadID, name):
      Thread.__init__(self)
      self.threadID = threadID
      self.name = name
   def run(self): 
      try:
        #app.run(host='0.0.0.0', port = 80, debug=False, ssl_context=('cert.pem', 'key.pem'))        
        app.run(host='0.0.0.0', port = 80, debug=False)   
        LogEvent("FlaskApp Thread started") 
      except OSError as err:
        LogEvent("ERREUR : thread FlaskApp ! Message : " + str(err))


class Scheduler (Thread):

   def __init__(self, threadID, name):
      Thread.__init__(self)
      self.threadID = threadID
      self.name = name
   
   def run(self): 
    
      global DATA, ID
      
      LogEvent("Thread " + self.name + " started")       

      try: 
       
        while True: 
            if DATA['SCHEDULER']:
                #  format "SCHEDULER_START": "01:00"
                HH_START = int(DATA["SCHEDULER_START"][0:2])
                MM_START = int(DATA["SCHEDULER_START"][3:5])
                HH_STOP  = int(DATA["SCHEDULER_STOP"][0:2])
                MM_STOP  = int(DATA["SCHEDULER_STOP"][3:5])
                
                if DATA["DEBUG"] : 
                    LogEvent("DEBUG : HH_START : " + str(HH_START))
                    LogEvent("DEBUG : MM_START : " + str(MM_START))
                    LogEvent("DEBUG : HH_STOP  : " + str(HH_STOP))
                    LogEvent("DEBUG : MM_STOP  : " + str(MM_STOP))

                time_now   = datetime.datetime.now()
                time_now   = time_now.replace(second=0, microsecond=0) 
                time_start = now.replace(hour=HH_START, minute=MM_START, second=0, microsecond=0) 
                time_stop  = now.replace(hour=HH_STOP, minute=MM_STOP, second=0, microsecond=0 ) 
                
                if DATA["DEBUG"] : 
                    LogEvent("DEBUG : time_now   : " + str(time_now))
                    LogEvent("DEBUG : time_start : " + str(time_start))
                    LogEvent("DEBUG : time_stop  : " + str(time_stop))
                    LogEvent("DEBUG : time_start == time_now ?  : " + str(time_start==time_now))

                if time_start == time_now:
                    if not DATA['PLUG']: 
                        # il est l'heure d'enclencher la prise 240V 
                        ID = ID + 1
                        separator = "--- EVENT ID : " + str(ID) + " ----"
                        LogEvent(separator) 
                        DATA['PLUG'] = True 
                        RELAY.on(DATA['PLUG_RELAY']) 
                        LogEvent("Planificateur : prise 240V enclenchée.")
                    
                if time_stop == time_now:
                    if DATA['PLUG']: 
                        # il est l'heure de déclencher la prise 240V
                        ID = ID + 1
                        separator = "--- EVENT ID : " + str(ID) + " ----"
                        LogEvent(separator) 
                        DATA['PLUG'] = False 
                        RELAY.off(DATA['PLUG_RELAY']) 
                        LogEvent("Planificateur : prise 240V déclenchée.")   
                    
                sleep(30)

      except OSError as err:
        LogEvent("ERREUR : thread Scheduler ! Message : " + str(err))


##### LECTURE DES CAPTEURS ET ETATS #######

def ReadSensorsValues():
    '''
    lecture de l'ensemble des capteurs 
    '''
    global  DATA, ID
    
    DATA["Ti"]          = round(DS18B20.read(),1)
    DATA["Te"]          = round(AM2315.read_temperature(),1)
    DATA["He"]          = round(AM2315.read_humidity(),1)  

    time_now   = datetime.datetime.now()
    DATA["DATE"]        = time_now.strftime("%d.%m.%Y")     
    DATA["TIME"]        = time_now.strftime("%H:%M:%S")
    
    if True : #DATA["DEBUG"] : 
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
        #LogEvent("Mesure du " + str(DATA["DATE"]) + " à " + str(DATA["TIME"]))
        LogEvent("Température extérieure    :  " + str(DATA["Te"]) + " °C")
        LogEvent("Température intérieure    :  " + str(DATA["Ti"]) + " °C")
        LogEvent("Humidité extérieure       :  " + str(DATA["He"]) + " %HR")
    return 


def SetThermostat():
    '''
    Thermostat
    '''
    global  DATA, ID
            
    
    if DATA["THERMOSTAT"] :
        if float(DATA["Ti"]) <= float(DATA["TMIN"]) : 
            RELAY.on(DATA["HEATER_RELAY"]) 
            if not DATA["HEATER"]:
                ID = ID + 1
                separator = "--- EVENT ID : " + str(ID) + " ----"
                LogEvent(separator) 
                LogEvent("Chauffage activé via thermostat. Température < " + str(DATA["TMIN"]) + "°C")
            DATA["HEATER"] = True 
                            
        if float(DATA["Ti"]) >= float(DATA["TMAX"]) : 
            RELAY.off(DATA["HEATER_RELAY"]) 
            if DATA["HEATER"]:
                ID = ID + 1
                separator = "--- EVENT ID : " + str(ID) + " ----"
                LogEvent(separator) 
                LogEvent("Chauffage désactivé via thermostat. Température >=" + str(DATA["TMAX"]) + "°C")
            DATA["HEATER"] = False
    return 

def SaveData():

    # Sauvegarde des données enregistrées sur disque

    try: 
        with open(ALLDATAFILE , 'wb') as file:
            pickle.dump(ALL_DATA, file)
    except IOError as e:
        LogEvent("Erreur: {0}".format(e))

    if DATA["DEBUG"] : LogEvent("Sauvegarde des mesures enregistrées terminée.")
    
def LoadData():

    # Chargement des données enregistrées sur disque 

    global ALL_DATA

    if os.path.isfile(ALLDATAFILE ):
        LogEvent("Fichier de sauvegarde des mesures : " + ALLDATAFILE + " disponible." )
    
        try: 
            with open(ALLDATAFILE , 'rb') as file:
                ALL_DATA = pickle.load(file)
        except OSError as err:
            LogEvent("Erreur: {0}".format(err))
       
        LogEvent("Chargement des mesures sauvegardées terminé." )
    else:
        LogEvent("Fichier de sauvegarde des mesures inexistant." )
    return   


####################   API   ############################

@app.route("/index", methods=["GET"])
@app.route("/", methods=["GET"])
def home():
    '''
    Retourne la page principale : capteurs.html
    '''
  
    return render_template('capteurs.html', **DATA) 


@app.route("/actionneurs", methods=['GET'])
def actionneurs():
    '''
    Affichage des actionneurs
    '''
    
    return render_template('actionneurs.html', **DATA) 

@app.route("/capteurs", methods=['GET'])
def capteurs():
    '''
    Affichage des mesures principales dans la vue dashboard
    '''
    
    return render_template('capteurs.html', **DATA) 

@app.route("/graph", methods=['GET'])
def graph():
    '''
    Affichage de l'ensemble des graphiques 
    '''
    

    Ts = json_extract(ALL_DATA,"TIMESTAMP")
    He = json_extract(ALL_DATA,"He")
    Te = json_extract(ALL_DATA,"Te")
    Ti = json_extract(ALL_DATA,"Ti")
    R1 = json_extract(ALL_DATA,"HEATER")
    R2 = json_extract(ALL_DATA,"PLUG")
    R3 = json_extract(ALL_DATA,"LIGHT")

    data1 = []
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    data6 = []
    i=0

    for ts, he, te, ti, r1, r2, r3 in zip(Ts, He, Te, Ti, R1, R2, R3):

            data1.append([ts, (he)])
            data2.append([ts, (te)])
            data3.append([ts, (ti)])

            if r1:
                data4.append([ts, 1])
            else:
                data4.append([ts, 0])

            if r2:
                data5.append([ts, 1])
            else:
                data5.append([ts, 0])

            if r3:
                data6.append([ts, 1])
            else:
                data6.append([ts, 0])
            
            i=i+1
       
    return render_template('graph.html', data1=data1, data2=data2,data3=data3, data4=data4, data5=data5,data6=data6, **DATA)
    
    

@app.route("/shutdown", methods=['POST'])
def shutdown():
    '''
    Shutdown Raspberry PI 4.
    '''
    global ID
    if request.method == "POST":
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
        LogEvent("Shutdown ...  bye bye !")
        os.system('sudo halt')
    return jsonify('Shutdown en cours...', 204)   
   

@app.route("/reboot", methods=['POST'])
def reboot():
    '''
    Reboot Raspberry PI 4
    '''
    global ID
    if request.method == "POST":
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
        LogEvent("Reboot ... see you soon !")
        os.system('sudo reboot')
    return jsonify('Reboot en cours...', 204)
    

@app.route("/events", methods=['GET'])
def events():
    '''
    Affichage de la page des événements enregistrés.
    '''
    
    return render_template('events.html', **DATA, eventlog=eventlog)      


@app.route("/thermostat", methods=['GET'])
def thermostat():
    '''
    Retourne la configuration du Thermostat avec températures minimales et maximales définies
    Requête API sous forme : 
    http://box.ppdlab.ch/thermostat
   ''' 
    
    resp = {"Thermostat" : DATA["THERMOSTAT"],
         "TMIN" : DATA["TMIN"],
         "TMAX" : DATA["TMAX"]
        } 

    return jsonify(resp) 

@app.route("/thermostat/auto", methods=['POST','GET'])
def thermostat_auto_mode():
    '''
    POST : mode thermostat automatique
    Requête API sous forme : 
    http://box.ppdlab.ch/thermostat/auto
   ''' 
    
    global DATA, ID

    if request.method == "POST":
        state = (request.form.get('state'))
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
    
        if state=="true":
            DATA["THERMOSTAT"] = True
            LogEvent("Thermostat mode auto activé.")
        elif state=="false":
            DATA["THERMOSTAT"] = False
            LogEvent("Thermostat mode auto désactivé.")
        
        SaveState()
        SaveParametersToFile()   
        return render_template('actionneurs.html', **DATA) 
        
        
    if request.method == "GET":
        resp = "Mode automatique du thermostat : " + str(DATA["THERMOSTAT"])
        LogEvent(resp)
        return jsonify(resp) 


@app.route("/light", methods=['POST','GET'])
def light():
    '''
    POST : allumer/éteindre la lampe sur le relai #LIGHT_RELAY
    Requête API sous forme : 
    http://box.ppdlab.ch/light?state=true
   ''' 
    
    global DATA, ID

    if request.method == "POST":
        state = (request.form.get('state'))
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
        
        if state=="true":
            DATA['LIGHT'] = True
            # allumer la lampe !
            RELAY.on(DATA['LIGHT_RELAY']) 
            LogEvent("Lampe allumée.")
        elif state=="false":
            DATA['LIGHT'] = False
            # éteindre la lampe !
            RELAY.off(DATA['LIGHT_RELAY']) 
            LogEvent("Lampe éteinte.")
        
        SaveState()
        return render_template('actionneurs.html', **DATA) 

    if request.method == "GET":
        resp = {'Lampe': DATA['LIGHT']}
        LogEvent(resp)
        return jsonify(resp)


@app.route("/debug_mode", methods=['POST','GET'])
def debug_mode():
    '''
    POST : mode debug
    Requête API sous forme : 
    http://box.ppdlab.ch/debug?state=true
   ''' 
    
    global DATA, ID

    if request.method == "POST":
        state = (request.form.get('state'))
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
        
        if state=="true":
            DATA['DEBUG'] = True
            LogEvent("Mode DEBUG activé.")
        elif state=="false":
            DATA['DEBUG'] = False
            LogEvent("Mode DEBUG désactivé.")
        
        SaveState()
        return ('', 204)

    if request.method == "GET":
        resp = {'Mode DEBUG': DATA['DEBUG']}
        LogEvent(resp)
        return jsonify(resp)


@app.route("/heater", methods=['POST','GET'])
def heater():
    '''
    POST : allumer / éteindre le chauffage sur le relai #HEATER_RELAY
    Requête API sous forme : 
    http://box.ppdlab.ch/heater?state=true
   ''' 
    
    global DATA, ID

    if request.method == "POST":
        state = (request.form.get('state'))
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
        
        if state=="true":
            DATA['HEATER'] = True
            # allumer chauffage
            RELAY.on(DATA['HEATER_RELAY']) 
            LogEvent("Chauffage allumé.")
        elif state=="false":
            DATA['HEATER'] = False
            # éteindre chauffage
            RELAY.off(DATA['HEATER_RELAY']) 
            LogEvent("Chauffage éteinte.")
        
        SaveState()
        return render_template('actionneurs.html', **DATA) 

    if request.method == "GET":
        resp = {'Chauffage': DATA['HEATER']}
        LogEvent(resp)
        return jsonify(resp)


@app.route("/scheduler", methods=['POST','GET'])
def scheduler():
    '''
    POST : allumer / éteindre en fonction de certaines heures le relai #PLUG_RELAY
    Requête API sous forme : 
    http://box.ppdlab.ch/scheduler?state=true
   ''' 
    
    global DATA, ID

    if request.method == "POST":
        state = (request.form.get('state'))
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
       
        if state=="true":
            DATA['SCHEDULER'] = True
            LogEvent("Planificateur activé.")
        elif state=="false":
            DATA['SCHEDULER']= False
            LogEvent("Planificateur désactivé.")
        
        SaveState()
        return render_template('actionneurs.html', **DATA) 

    if request.method == "GET":
        resp = {'SCHEDULER       ': DATA['SCHEDULER'],
                'SCHEDULER START ': DATA['SCHEDULER_START'],
                'SCHEDULER STOP  ': DATA['SCHEDULER_STOP']}
        LogEvent(resp)
        return jsonify(resp)

@app.route("/plug", methods=['POST','GET'])
def plug():
    '''
    POST : allumer / éteindre  le relai #PLUG_RELAY
    Requête API sous forme : 
    http://box.ppdlab.ch/PLUG_RELAY?state=true
   ''' 
    
    global DATA, ID

    if request.method == "POST":
        state = (request.form.get('state'))
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 
        
        if state=="true":
            DATA['PLUG'] = True 
            RELAY.on(DATA['PLUG_RELAY']) 
            LogEvent("Prise 240V enclenchée.")

        elif state=="false":
            DATA['PLUG'] = False 
            RELAY.off(DATA['PLUG_RELAY']) 
            LogEvent("Prise 240V déclenchée.")
        
        SaveState()
        return render_template('actionneurs.html', **DATA) 

    if request.method == "GET":
        resp = {'PLUG ': DATA['PLUG']}
        LogEvent(resp)
        return jsonify(resp)


@app.route("/saveparameters", methods=['POST'])
def saveparameters():
    '''
    Sauvegarde des paramètres de configuration 
    '''
    global DATA, ID
        
    if request.method == "POST":
        
        ID = ID + 1
        separator = "--- EVENT ID : " + str(ID) + " ----"
        LogEvent(separator) 

        DATA["TMIN"]            = int(request.form.get("TMIN"))
        DATA["TMAX"]            = int(request.form.get("TMAX"))
        DATA["INTERVAL_LOOP"]   = int(request.form.get("INTERVAL_LOOP"))
        DATA["INTERVAL_DISPLAY"]= int(request.form.get("INTERVAL_DISPLAY"))  
        DATA["SCHEDULER_START"] = (request.form.get("SCHEDULER_START"))
        DATA["SCHEDULER_STOP"]  = (request.form.get("SCHEDULER_STOP"))       
        
        LogEvent("Changements des paramètres de configuration : ")
        LogEvent("Fréquence de lecture capteurs :  " + str(DATA["INTERVAL_LOOP"]) + " sec.") 
        LogEvent("Fréquence d'affichage écran   :  " + str(DATA["INTERVAL_DISPLAY"]) + " sec.")
        LogEvent("Température minimum           :  " + str(DATA["TMIN"]) + " °C")
        LogEvent("Température maximum           :  " + str(DATA["TMAX"]) + " °C")
        LogEvent("Scheduler Start               :  " + str(DATA["SCHEDULER_START"]))
        LogEvent("Scheduler Stop                :  " + str(DATA["SCHEDULER_STOP"]))
        LogEvent("Debug mode                    :  " + str(DATA["DEBUG"]))
        
        SaveState()
        SaveParametersToFile()

    return render_template('parameters.html', **DATA) 

@app.route("/getparameters", methods=['GET'])
def getparameters():
    '''
    Affichage des paramètres de configuration 
    '''
   
    return jsonify(DATA)


@app.route("/parameters", methods=['GET'])
def parameters():
    '''
    Affichage des paramètres de configuration 
    '''

    return render_template('parameters.html', **DATA) 

####################   fin API   ############################

if __name__ == '__main__': 
     
    app.secret_key = os.urandom(12)
    LoadData()
    LoadParametersFromFile()
    
    thread1 = Display(1, "DISPLAY")
    thread2 = Loop(2, "LOOP")
    thread3 = FlaskApp(3, "FLASKAPP")
    thread4 = Scheduler(4, "SCHEDULER")
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()







