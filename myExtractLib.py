# Auteur  : Patrick Pinard 
# Date    : 17.1. 2022
# Objet   : Extrait des valeurs d'un dict JSON
# Version : 1.0  

# -*- coding: utf-8 -*-

#   Clavier MAC :      
#  {} = "alt/option" + "(" ou ")"
#  [] = "alt/option" + "5" ou "6"
#   ~  = "alt/option" + n    
#   \  = Alt + Maj + / 
# 

import json

def json_extract(obj, key):
    """ Fonction récursive qui extrait une valeur d'un objet JSON"""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    
    return values

