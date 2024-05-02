#!/usr/bin/env python3

# Auteur    : Patrick Pinard
# Date      : 3.5.2022
# Objet     : gestion des LOG
# Source    : myLOGLib.py
# Version   : 1.1 (augmentation du nombre maximum d'event sauvegardé à 1000)
# Statut    : fonctionne parfaitement

# -*- coding: utf-8 -*-
#   Clavier MAC :
#  {} = "alt/option" + "(" ou ")"
#  [] = "alt/option" + "5" ou "6"
#   ~  = "alt/option" + n
#   \  = Alt + Maj + /

import datetime
import logging

DEBUG = True  # sauvegarde tous les événements dans fichier de log
VERBOSE = False  # mode bavard
PATH = "/home/pi/mybox/"
LOGFILENAME = PATH + "mybox.log"  # fichier de LOG par defaut
LOGLEVEL = DEBUG
FILEMODE = "w"
RELEASE = "V1.0"
events = []
id = 0
MAXSIZE = 1000

# LOG LEVEL = Critical, Error, Warning, Info, Debug, Not Set

logging.basicConfig(
    filename=LOGFILENAME,
    filemode=FILEMODE,
    level=LOGLEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("--- { start logging : " + LOGFILENAME + " } ---")


def LogEvent(message):
    """
    Ecriture de message dans fichier de LOG sur disque.
    Si VERBOSE est activé, copie sur console.
    """
    global id

    now = datetime.datetime.now()
    d = now.strftime("%d.%m.%Y")
    t = now.strftime("%H:%M:%S")
    id = id + 1
    event = {"id": id, "date": d, "time": t, "message": message}
    events.insert(0, event)

    l = len(events)
    if l > MAXSIZE - 1:
        events.pop(l - 1)

    if DEBUG:
        logging.info(message)
    if VERBOSE:
        print(message)
    return


if __name__ == "__main__":

    LogEvent("test de LogEvent " + RELEASE)
