# -*- coding: utf-8 -*-
"""
Created on Aout 2024
@authors : Rachel Honnert (TA74)

Ce script crée fabrique un fichier csv avec les données de Températures, d'humidité, de vitesse et de direction du vent , de vitesse de la sonde. 

Utilisation :
    python MakeCSV_SerieRS.py 

Il fonctionne en python3.12 et a besoin des librairies :
    - calendar
    - calendar
    - datetime
    - importlib
    - numpy
    - pandas
    - locale
    - matplotlib
    - sys
    - tkinter
    -.FreeSimpleGUI ou à défaut PySimpleGUI
    - logging
    - subprocess 
    - codecs
"""

# Chargement des librairies
import calendar
import datetime
import importlib
import numpy as np
import pandas as pd
import locale
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import os
from pandas.plotting import register_matplotlib_converters
import sys
import subprocess
from tkinter import *
import codecs
import csv

# Complément pour les librairies
pd.set_option('mode.chained_assignment',None)
register_matplotlib_converters()
#
#logging.basicConfig( filename="py_log.log",filemode="w")
############# DEFINITION DES FONCTIONS #############

def T_meteofrance(date):
  liste_noire = ['tvd170207.2257xx','tvd170206.2241xx','tvd170205.2259xx','tvd170204.2302xx','tvd170203.2252xx','tvd110911.2326xx', 'tvd000601.0022xx','tvd020826.2310xx','tvd020908.0739xx','tvd070813.2320xx','tvd070818.2301xx','tvd080915.0757xx','tvd080915.1134xx', 'tvd080917.1304xx','tvd080923.1505xx','tvd080930.0948xx','tvd020630.2315xx','tvd020903.2304xx','tvd020904.2315xx','tvd030607.2258xx', 'tvd030616.2336xx','tvd030616.2312xx','tvd030620.2308xx','tvd030712.2254xx','tvd030805.2250xx','tvd030916.0809xx','tvd040625.2252xx', 'tvd040625.2325xx','tvd040626.2255xx','tvd040626.2316xx','tvd040627.2303xx','tvd030920.2248xx','tvd040701.0402xx','tvd040717.0519xx', 'tvd030617.2307xx','tvd150830.2243xx','tvd040808.2252xx','tvd040810.2301xx','tvd040816.2303xx','tvd110802.2354xx','tvd040809.2251xx', 'tvd070818.2301xx']

  # CETTE FONCTION RÉCUPÈRE LES DONNÉES MÉTÉOFRANCE CORRESPONDANT À LA DATE EN ENTRÉE #########
  # ELLE RENVOIE UNE LISTE CONTENANT L'ALTITUDE, LA PRESSION ET LA TEMPÉRATURE MESURÉES PAR LE BALLON MÉTÉOFRANCE #########

  data = [[],[],[],[],[],[],[]]
  if is_before_full(date, '19-11-2019')=='Apres':
      data = T_meteofrance_cor(date)

#  else:
#      # RECONSTRUCTION DU CHEMIN D'ACCÈS AUX FICHIERS MÉTÉOFRANCE #########
#      jour = date[:2]
#      mois = date[3:5]
#      annee = date[6:10]
#      chemin="//mtoservice/Labos/LIDAR/COR/"
#      print(chemin)
#      folder_mf = os.listdir(chemin)
#      if annee not in folder_mf:
#        print("Il n'y a pas de mesure météo france pour cette année!")
#        return 0
#      dossier = os.listdir(chemin+annee)
#      radical_fichier_mf = 'DD' + annee + mois + jour+"00"
#      if [f for f in dossier if radical_fichier_mf in f] == []: # Si le dossier est vide, on affiche un message signalant qu'il n'y a pas de mesure pour cette date #########
#        print("Il n'y a pas de mesure météo france pour cette date")
#        return 0
#      elif [f for f in dossier if radical_fichier_mf in f][0] in liste_noire:
#        return 0
#      # OUVERTURE ET LECTURE DU FICHIER MÉTÉOFRANCE #########
#      else:
#        file_sizes = [os.path.getsize(chemin+'/'+f) for f in dossier if radical_fichier_mf in f]
#        ind_f = file_sizes.index(max(file_sizes))
#        nom_fichier_meteofrance = [f for f in dossier if radical_fichier_mf in f][ind_f]
#        fichier_mf = codecs.open(chemin+'/'+nom_fichier_meteofrance, encoding = 'latin1')
#        lines = fichier_mf.readlines()
#        # AU SEIN DES FICHIERS MÉTÉOFRANCE, SEULS LES LIGNES COMMENÇANT PAR UN "B" NOUS INTÉRESSENT ICI #########
#        lines_B = []
#        for l in lines:
#          if l[0] == 'B':
#            temp = l.replace('\r\n', '').split(' ')
#            lines_B.append([k for k in temp if not(k == '')])
#        # LA STRUCTURE DES FICHIERS VARIANT SELON L'ANNÉE ET LA VERSION DE MÉTÉOFRANCE, IL FAUT RÉCUPÉRER LE NUMÉRO DE VERSION POUR EN DÉDUIRE LES INDICES OÙ TROUVER ALT, P ET T
#        version_fichier = lines[0].replace('\r\n', '')
#        version_fichier = version_fichier.replace('\n','')
#        if version_fichier == 'V 12' or version_fichier == 'V 11' or version_fichier == 'V 10.1' or version_fichier == 'V 6.5' or version_fichier == 'V 7.0' or version_fichier == 'V 9.0':
#          ind_alt_b = 2
#          ind_P_b = 3
#          ind_T_b = 4
#        elif version_fichier == 'V 13' or version_fichier == 'V 14':
#          ind_alt_b = 9
#          ind_P_b = 2
#          ind_T_b = 3
#          test = lines[1].replace('\r\n', '')
#          test = test.replace('\n', '')
#          if test[0] == 'A':
#            ind_alt_b = 2
#            ind_P_b = 3
#            ind_T_b = 4
#        # UNE FOIS LES INDICES PARAMÉTRÉS, IL NE RESTE PLUS QU'À STOCKER LES DONNÉES DANS UNE LISTE, APPELÉE ICI "DATA" 
#        data[0] = [float(lines_B[i][ind_alt_b])/1000 for i in range(len(lines_B))]
#        data[1] = [float(lines_B[i][ind_P_b]) for i in range(len(lines_B))]
#        data[2] = [float(lines_B[i][ind_T_b]) + 273.15 for i in range(len(lines_B))]  

  return data

def T_meteofrance_cor(date):
    # CETTE FONCTION RÉCUPÈRE LES DONNÉES MÉTÉOFRANCE CORRESPONDANT À LA DATE EN ENTRÉE 
    # ELLE RENVOIE UNE LISTE CONTENANT L'ALTITUDE, LA PRESSION ET LA TEMPÉRATURE MESURÉES PAR LE BALLON MÉTÉOFRANCE
    # RECONSTRUCTION DU CHEMIN D'ACCÈS AUX FICHIERS MÉTÉOFRANCE
    jour = date[:2]
    mois = date[3:5]
    annee = date[6:10]
    chemin=os.path.join("//mtoservice/Labos/LIDAR/COR/",annee) # CHEMIN D'ACCÈS AUX DONNÉES MÉTÉOFRANCE
    dossier = sorted([f for f in os.listdir(chemin) if '.cor' in f])
    radical_fichier_mf = 'DD' + annee + mois + jour
    if [f for f in dossier if radical_fichier_mf in f] == []: # Si le dossier est vide, on affiche un message signalant qu'il n'y a pas de mesure pour cette date 
        print("Il n'y a pas de mesure météo france pour cette date")
        return 0
    # OUVERTURE ET LECTURE DU FICHIER MÉTÉOFRANCE 
    else:
        print(date)
        nom_fichier_meteofrance = [f for f in dossier if radical_fichier_mf in f][0]
        fichier_mf = codecs.open(chemin+'/'+nom_fichier_meteofrance, encoding = 'latin1')
        lines = fichier_mf.readlines()
        alt,P,T,U,FF,DD,As = [], [], [], [], [], [], [] # je recupère l'altitude, la pression, la température, l'humidité, vent ff et direction, vitesse ascendente
        for i in range(1, len(lines)):
            tmp = lines[i].replace('\n', '').replace('\r', '').replace(';', '\t').split('\t')
            buffer_alt = 0 ## pour éviter de prendre en compte la redescente du ballon, qui est dans les .cor
            if len(tmp) > 1 and float(tmp[1]) > buffer_alt:
                alt.append(float(tmp[1])/1000)
                P.append(float(tmp[12]))
                T.append(float(tmp[10])+273.15)
                U.append(float(tmp[11]))          # humidité relative en %
                FF.append(float(tmp[7]))          # force du vent
                DD.append(float(tmp[8]))          # direction du vent
                As.append(float(tmp[6]))          # vitesse ascentionnelle en m/s ? 
                buffer_alt = float(tmp[1])
        return [alt,P,T,U,FF,DD,As]

def lecture_rs(date):
  # Florent Tence : date sous forme DD-MM-AAAA
  jour = date[:2]
  mois = date[3:5]
  annee = date[6:10]
  #print(emplacement_rs)
  dossier = sorted([f for f in os.listdir(emplacement_rs) if '.cor' in f]) # list tous les .cor du fichier
  radical_fichier_mf = 'DD' + annee + mois + jour # je recherche le fichier du jour en question 
  #print(dossier)
  #print(radical_fichier_mf)
  alt,P,T,U,FF,DD,As = [], [], [], [], [], [], [] # je recupère l'altitude, la pression, la température, l'humidité, vent ff et direction, vitesse ascendente
  if [f for f in dossier if radical_fichier_mf in f] == []: # Si le dossier est vide, on affiche un message signalant qu'il n'y a pas de mesure pour cette date
    sg.popup_ok("Il n'y a pas de mesure météo france pour cette date", title="Erreur", keep_on_top=True)
  else:
    # Ouverture et lecture du fichier de RS
    nom_fichier_meteofrance = [f for f in dossier if radical_fichier_mf in f][-1] # on prend le dernier lancer de la journée
    print(nom_fichier_meteofrance)
    fichier_mf = codecs.open(emplacement_rs+'/'+nom_fichier_meteofrance,encoding = 'latin1')
    print(fichier_mf)
    lines = fichier_mf.readlines()
     
    for i in range(1, len(lines)):
      tmp = lines[i].replace('\n', '').replace('\r','').replace(';', '\t').split('\t')
      if len(tmp) > 1:
        alt.append(float(tmp[1])/1000)
        P.append(float(tmp[12]))          # Pression atmosphérique hPa
        #T.append(float(tmp[10])+273.15)   # Température en K 
        T.append(float(tmp[10]))   # Température en °C 
        U.append(float(tmp[11]))          # humidité relative en %
        FF.append(float(tmp[7]))          # force du vent
        DD.append(float(tmp[8]))          # direction du vent
        As.append(float(tmp[6]))          # vitesse ascentionnelle en m/s ? 
  return [alt,P,T,U,FF,DD,As] # il me retourne une liste de valeurs

def is_before_full(date1, date2): ## dates au format jour/mois/annee
    if int(date1[6:10]) > int(date2[6:10]):
        verdict = 'Apres'
    elif int(date1[6:10]) < int(date2[6:10]):
        verdict = 'Avant'
    elif int(date1[6:10]) == int(date2[6:10]):    
        if int(date1[3:5]) > int(date2[3:5]):
            verdict = 'Apres'
        elif int(date1[3:5]) < int(date2[3:5]):
            verdict = 'Avant'
        elif int(date1[3:5]) == int(date2[3:5]):
            if int(date1[:2]) > int(date2[:2]):
                verdict = 'Apres'
            elif int(date1[:2]) < int(date2[:2]):
                verdict = 'Avant'
            elif int(date1[:2]) == int(date2[:2]):
                verdict = 'Meme jour'
    return verdict

def jour_davant_dapres(date):    
    if date[:5]=='31-12':
        date_apres = '01-01-'+str(int(date[6:10])+1)
        date_avant = '30'+date[2:10]

    elif date[:5]=='01-01':
        date_apres = '02-01'+date[5:10]
        date_avant = '31-12-'+str(int(date[6:10])-1)
        
    elif date[:2]=='31' and date[3:5] in ['01', '03', '05', '07', '08', '10']:
        if len(str(int(date[3:5])+1))==1:
            date_apres = '01-0' + str(int(date[3:5])+1) + date[5:10]
            date_avant = '30'+date[2:10]
        elif len(str(int(date[3:5])+1))==2:
            date_apres = '01-' + str(int(date[3:5])+1) + date[5:10]
            date_avant = '30'+date[2:10]
            
    elif date[:2]=='30' and date[3:5] in ['04', '06', '09', '11']:
        if len(str(int(date[3:5])+1))==1:
            date_apres = '01-0'+str(int(date[3:5])+1)+date[5:10]
            date_avant = '29'+date[2:10]
        elif len(str(int(date[3:5])+1))==2:
            date_apres = '01-'+str(int(date[3:5])+1)+date[5:10]
            date_avant = '29'+date[2:10]
            
    elif date[:5]=='29-02':
        date_apres = '01-03'+date[5:10]
        date_avant = '28-02'+date[5:10]
        
    elif date[:5]=='28-02' and date[6:10] not in ['2028', '2024', '2020', '2016', '2012', '2008', '2004', '2000']:
        date_apres = '01-03'+date[5:10]
        date_avant = '27-02'+date[5:10]
        
    elif date[:5]=='01-03' and date[6:10] not in ['2028', '2024', '2020', '2016', '2012', '2008', '2004', '2000']:
        date_apres = '02'+date[2:10]
        date_avant = '28-02'+date[5:10]

    elif date[:5]=='01-03' and date[6:10] in ['2028', '2024', '2020', '2016', '2012', '2008', '2004', '2000']:
        date_apres = '02'+date[2:10]
        date_avant = '29-02'+date[5:10]
        
    elif date[:2]=='01':
            date_apres = '02'+date[2:]
            if date[3:5] in ['05', '07', '08', '10', '12']:
                if len(str(int(date[3:5])-1))==1:
                    date_avant = '30-0'+str(int(date[3:5])-1)+date[5:10]
                elif len(str(int(date[3:5])-1))==2:
                    date_avant = '30-'+str(int(date[3:5])-1)+date[5:10]
            if date[3:5] in ['02', '04', '06', '09', '11']:
                if len(str(int(date[3:5])-1))==1:
                    date_avant = '31-0'+str(int(date[3:5])-1)+date[5:10]
                if len(str(int(date[3:5])-1))==2:
                    date_avant = '30-'+str(int(date[3:5])-1)+date[5:10]
                    
    else:
        if len(str(int(date[:2])+1))==2:
            date_apres = str(int(date[:2])+1)+date[2:]
        else:
            date_apres = '0'+str(int(date[:2])+1)+date[2:]    
        if len(str(int(date[:2])-1))==2:
            date_avant = str(int(date[:2])-1)+date[2:]
        else:
            date_avant = '0'+str(int(date[:2])-1)+date[2:]    
    
    return date_avant, date_apres
#############  PROGRAMME PRINCIPAL #############

if (__name__ == "__main__"):

  ## Dates / heures / décalage
  aujourdhui = datetime.datetime.today()
  dateaujourdhui = aujourdhui.strftime("%d-%m-%Y")
  emplacement_rs="//mtoservice/Labos/LIDAR/COR/"
  annees=[str(y) for y in range(2024, 2025)]
  
  date_debut, date_fin = '01-01-'+annees[0], '31-12-'+annees[-1]
  jours_full = []
  jour0 = date_debut
  jours_full.append(jour0)
  while not jour0 == date_fin:
    _, jour0 = jour_davant_dapres(jour0)
    jours_full.append(jour0)
  #ind_fin = jours_full.index('21-05-2024')
  ind_fin = jours_full.index(dateaujourdhui)
  jours_full = jours_full[:ind_fin]

  mf_data = [[], []]
  for date in jours_full:
      if not '29-02' in date: # pour plus de simplicité, on retire les 29 février des années bisexiles 
          data_mf = T_meteofrance(date)
          mf_data[0].append(date)
          if data_mf == 0:
              print(date)
              mf_data[1].append([50*[np.nan], 50*[np.nan], 50*[np.nan]])
          else:
              mf_data[1].append(data_mf)
  z_commun = list(np.arange(0,35,0.3))   ## on créé une échelle commune de 0 à 35 avec une résolution de 300 pour tout ramener sur une même échelle
  mf_data_zcom = [mf_data[0],[]]
  j_per_annee, mf_data_zcom_per_annee = [[] for y in annees], [[] for y in annees]
  for l in range(len(mf_data[0])):
    j_per_annee[annees.index(mf_data[0][l][6:10])].append(mf_data[0])
    z_temp = [[z] for z in z_commun]  ## on créé une liste de liste selon z_commun, on y classera nos valeurs d'altitudes peu à peu avant de moyenner
    for j in range(len(mf_data[1][l][0])):   ## mf_data[1][X][0] désigne toujours l'altitude 
        z_commun.append(mf_data[1][l][0][j])
        z_commun = sorted(z_commun)
        ind = z_commun.index(mf_data[1][l][0][j])  ## on trouve l'indice correspondant à chaque valeur d'altitude, puis on met la valeur de température correspondante dans z_temp
        z_commun.remove(mf_data[1][l][0][j])
        z_temp[ind-1].append(mf_data[1][l][2][j])  ## indice 2 pour la température
    mf_data_zcom[1].append(len(z_commun)*[np.nan]) ## on créé une liste vierge composée de NaN, puis on remplace par les valeurs stockées dans z_temp, quand il y en a
    for alt in range(len(z_temp)):
        if not(z_temp[alt][1:] == []):
          mf_data_zcom[1][l][alt] = np.mean(z_temp[alt][1:])
    mf_data_zcom_per_annee[annees.index(mf_data[0][l][6:10])].append(mf_data_zcom[1][l])
  print(len(mf_data_zcom_per_annee))
  # calcul de l'anomalie
  mf_data_climato = np.nanmean(mf_data_zcom_per_annee[:-1], axis=0)
  mf_data_climato_jusque_20mai = mf_data_climato#[:140]
  #mf_data_climato_2024 = np.array(mf_data_zcom_per_annee[-1])[:140] - mf_data_climato_jusque_20mai
  mf_data_climato_2024 = np.array(mf_data_zcom_per_annee[-1]) - mf_data_climato_jusque_20mai
  print(mf_data_climato_2024)
  # On ecrit le fichier csv
  print(mf_data_zcom_per_annee)
  
  df = pd.DataFrame(mf_data_zcom_per_annee, columns=['FName', 'LName', 'Age'])
  
  
  with open("DATA_series.csv", 'w') as f:
    write=csv.writer(f)
  #mf_data_zcom_per_annee.to_csv("DATA_series.csv", sep=";") 
  
  
 #############  FIN DU PROGRAMME #############

