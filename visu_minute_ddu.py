# -*- coding: utf-8 -*-
"""
Created on Juillet 2024
@author : Rachel Honnert TA74 et Benjamin Ménétrier

Ce script crée une interface graphique (GUI) permettant de visualiser les données des fichiers "minute" du Cobalt ,
d'exporter au format png les plots et d'exporter les données au format "png".

Utilisation :
    python visu_minute_ddu.py ou double clic sur un bouton du bureau : VISU_MINUTE_DDU

Il fonctionne en python3.12 et a besoin des librairies :
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

Graphics : Vent (m/s,kt,km/h), Humidité,Température,Pression
Export : PSTA;T;U;DD;FF;FM1;VVSYNTH;

Modifications : 
     Août 2024 : Les images sont crées à partir de scripts originellement mis en place par Laura Chataignier (TA71) puis des modifications successives. En particulier ici pour une meilleure visualisation sous PySimpleGUI les titres ont été modifiés.
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
from tkinter import *

# Chargement de FreeSimpleGui, ou de PySimpleGui à défaut
try:
  import FreeSimpleGUI as sg
except ModuleNotFoundError:
  import PySimpleGUI as sg
import logging

# Complément pour les librairies
pd.set_option('mode.chained_assignment',None)
register_matplotlib_converters()
#
#logging.basicConfig( filename="py_log.log",filemode="w")
logging.basicConfig(level=logging.DEBUG, filename="py_minute_log.log",filemode="w")
############# DEFINITION DES FONCTIONS #############

### Environnement de travail :
def existence_fichier(fichier, quitter):
  # Si le fichier n'existe pas, une fenêtre popup apparait
  # Si quitter == True, le programme s'arrête
  if os.path.isfile(fichier):
    return True
  else:
    logging.error("Le fichier " + fichier + " n'a pas été trouvé")
    sg.popup_ok("Le fichier " + fichier + " n'a pas été trouvé", title="Erreur", keep_on_top=True)
    if quitter:
      exit(1)
    else:
      return False

def existence_repertoire(repertoire) :
  # Si le répertoire n'existe pas, il est créé
  test = os.path.isdir(repertoire)
  if not test :
    logging.error("Le réperoire " + repertoire + " n'existe pas, création du répertoire")
    os.mkdir(repertoire)

def recuperation_donnees_mois(chemin_minute, date_debut_fichier, date_fin_fichier):
  # Récupération des données pour un seul mois, entre les dates date_debut_fichier et date_fin_fichier
  # Renvoie la dataframe et un booléen indiquant si tout s'est bien passé

  # Test de l'existence du fichier
  if not existence_fichier(chemin_minute, False):
    return None, False

  # Lecture du fichier
  data_minute = pd.read_csv(chemin_minute, sep=';', decimal=",", engine='python')

  # Correction du zero manquant devant certaines dates
  TMP = []
  for x in range (0,len(data_minute['ddmmyyyyhhmm'])):
    if len(str(data_minute['ddmmyyyyhhmm'][x])) == 11:
      TMP.append('0'+str(data_minute['ddmmyyyyhhmm'][x]))
    else:
      TMP.append(str(data_minute['ddmmyyyyhhmm'][x]))
  data_minute['ddmmyyyyhhmm'] = TMP

  # Index de début, index de fin
  index_debut = (data_minute.ddmmyyyyhhmm == date_debut_fichier).idxmax()
  index_fin = (data_minute.ddmmyyyyhhmm == date_fin_fichier).idxmax()
  if data_minute['ddmmyyyyhhmm'][index_debut] != date_debut_fichier:
    # Pas de date pertinente dans ce fichier (index_debut)
    logging.critical("Pas de date pertinente dans ce fichier (index_debut)")
    sg.popup_ok("Pas de date pertinente dans ce fichier (index_debut)", title="Erreur", keep_on_top=True)
    return None, False
  if data_minute['ddmmyyyyhhmm'][index_fin] != date_fin_fichier:
    # Pas de date pertinente dans ce fichier (index_fin)
    logging.critical("Pas de date pertinente dans ce fichier (index_fin)")
    sg.popup_ok("Pas de date pertinente dans ce fichier (index_debut)", title="Erreur", keep_on_top=True)
    return None, False



  # Restrictions des données entre index_debut et index_fin
  data_minute = data_minute.iloc[index_debut:index_fin+1,:]

  # Formatage des dates et heures
  data_minute['ddmmyyyyhhmm'] = pd.to_datetime(data_minute['ddmmyyyyhhmm'][:],format='%d%m%Y%H%M',errors='coerce')
  data_minute['date'] = data_minute['ddmmyyyyhhmm']

  # Formatage des données numériques
  for param in data_minute.columns[2:14]:
    data_minute[param] = pd.to_numeric(data_minute[param])


  # Création d'un index, tri des données
  data_minute.set_index(['date'], inplace=True)
  data_minute.sort_index(ascending=True, inplace=True)

 
  # Enregistrement de la dataframe
  index = np.where(data_minute['ddmmyyyyhhmm'].notnull())[0]
  data_minute_final = pd.DataFrame({
    'DATE':data_minute['ddmmyyyyhhmm'].iloc[index], # date
    'T':data_minute['T'].iloc[index],               # température
    'DI':data_minute['DI'].iloc[index],             # durée d'insolation
    'RG':data_minute['RG'].iloc[index],             # rayonnement global
    'FXI':data_minute['FM1'].iloc[index],           # vitesse maximale sur 10min
    'FF':data_minute['FF'].iloc[index],             # vitesse moyenne sur 10min
    'DD':data_minute['DD'].iloc[index],             # direction moyenne sur 10min
    'U':data_minute['U'].iloc[index],               # humidité relative
    'P':data_minute['PSTA'].iloc[index],            # pression au niveau de la station
    'VIS':data_minute['VVSYNTH'].iloc[index]        # pression au niveau de la station
    }, columns=['DATE','T','DI','RG','FXI','FF','DD','U','P','VIS'])

  # Renvoie la dataframe
  return data_minute_final, True

def recuperation_donnees():
  # Date locale de début, date locale de fin
  date_locale_debut = datetime.datetime(int(annee_debut),int(mois_debut),int(jour_debut),int(heure_debut),int(minute_debut))
  date_locale_fin = datetime.datetime(int(annee_fin),int(mois_fin),int(jour_fin),int(heure_fin),int(minute_fin))
  if date_locale_debut >= date_locale_fin:
    sg.popup_ok("La date de début est postérieure ou égale à la date de fin !", title="Erreur", keep_on_top=True)
    return None, False
  if date_locale_fin >= datetime.datetime.today():
    sg.popup_ok("La date de fin est dans le futur !", title="Erreur", keep_on_top=True)
    return None, False
  if date_locale_debut >= datetime.datetime.today():
    sg.popup_ok("La date de début est dans le futur !", title="Erreur", keep_on_top=True)
    return None, False

  # Dates au format UTC
  date_debut = date_locale_debut - datetime.timedelta(hours=decalage[fuseau])
  date_fin = date_locale_fin - datetime.timedelta(hours=decalage[fuseau])

  # Formatage des dates
  ddmmyyhhmm_debut = date_debut.strftime("%d%m%Y%H%M")
  ddmmyyhhmm_fin = date_fin.strftime("%d%m%Y%H%M")
  yymm_debut = date_debut.strftime("%Y%m")
  yymm_fin = date_fin.strftime("%Y%m")

  # Date du jour
  aujourdhui = datetime.datetime.today()

  # Boucle sur les mois demandés
  for yymm in range(int(yymm_debut), int(yymm_fin)+1):
    # Choix du fichier
    if str(yymm)==aujourdhui.strftime("%Y%m"):
      fichier_minute = "DON_Minute_UTC_moisencours.csv"
    else :
      fichier_minute = "DON_Minute_UTC_" + str(yymm) + ".txt"

    # Chemin complet
    chemin_minute = os.path.join(emplacement_minute, fichier_minute)

    # Date de début et date de fin du mois de ce fichier
    date_debut_fichier = "01" + str(yymm)[4:6] + str(yymm)[0:4] + "0000"
    res = calendar.monthrange(int(str(yymm)[0:4]), int(str(yymm)[4:6]))
    date_fin_fichier = str(res[1]) + str(yymm)[4:6] + str(yymm)[0:4] + "2359"

    # Cas spécial pour le premier ou le dernier fichier
    if str(yymm) == yymm_debut:
      # Premier fichier
      date_debut_fichier = ddmmyyhhmm_debut
    if str(yymm) == yymm_fin:
      # Dernier fichier
      date_fin_fichier = ddmmyyhhmm_fin

    logging.info("Lecture et nettoyage des données de : " + chemin_minute)
    logging.info("Date de début : " + date_debut_fichier)
    logging.info("Date de fin :   " + date_fin_fichier)

    # Barre de progression
    if not sg.one_line_progress_meter('Récupération des données "Minute"',
                                      int(yymm)-int(yymm_debut)+1,
                                      int(yymm_fin)-int(yymm_debut)+1,
                                      key='-barre-',
                                      orientation='h',
                                      no_titlebar=True,
                                      grab_anywhere=True,
                                      no_button=True):
      logging.info('Hit the break')
      break

    if str(yymm) == yymm_debut:
      # Premier fichier
      data, success = recuperation_donnees_mois(chemin_minute, date_debut_fichier, date_fin_fichier)
      if not success:
        sg.one_line_progress_meter_cancel(key='-barre-')
        return None, False
      logging.info("Nombre de ligne pour ce fichier : " + str(data.shape[0]))
    else:
      # Fichiers suivants
      dataTmp, success = recuperation_donnees_mois(chemin_minute, date_debut_fichier, date_fin_fichier)
      if not success:
        sg.one_line_progress_meter_cancel(key='-barre-')
        return None, False
      logging.info("Nombre de ligne pour ce fichier : " + str(dataTmp.shape[0]))

      # Concaténation avec la dataframe
      data = pd.concat([data, dataTmp], ignore_index=True)

  # Taille totale de la dataframe
  logging.info("Taille totale de la dataframe: " + str(data.shape[0]))

  # Renvoie la dataframe
  return data, True

def write_data(data, P=False, T=False, Tres=False, FMOY=False, DMOY=False, FINS=False, DINS=False, HU=False, DI=False, RG=False, VIS=False) :
  # Ecriture d'un fichier csv
  logging.info("Le fichier csv est enregistré sous : " + emplacement_csv)
  existence_repertoire(emplacement_csv)

  # Nom du fichier
  fichier_csv = "DATA_METEO_" + str(annee_debut) + str(mois_debut) + str(jour_debut) + str(heure_debut) + str(minute_debut) + '-' + str(annee_fin) + str(mois_fin) + str(jour_fin) + str(heure_fin) + str(minute_fin) + '.csv'

  # Chemin complet
  chemin_csv = os.path.join(emplacement_csv, fichier_csv)
  logging.info("Nom du fichier csv: " + chemin_csv)

  # Sélection des données
  list_data = []
  if T:
    list_data.append('T')
  if HU:
    list_data.append('U')
  if P:
    list_data.append('P')
  if FMOY:
    list_data.append('FF')
  if DMOY:
    list_data.append('DD')
  if FINS:
    list_data.append('FXI')
  if RG:
    list_data.append('RG')
  if DINS:
    list_data.append('DI')
  if VIS:
    list_data.append('VIS')
  newdata = data[list_data]

  # Ecrire newdata dans un fichier csv
  newdata.to_csv(chemin_csv, sep=";")

  # Message de confirmation
  sg.popup_ok("Fichier " + chemin_csv + " exporté", title="Confirmation", keep_on_top=True)

def figure_vent(data,unite):
  # Trace le vent moyen
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)

  # Nom du fichier
  fichier_figure = "graphe_VentMinute_" + str(annee_debut) + str(mois_debut) + str(jour_debut) + str(heure_debut) + str(minute_debut) + '-' + str(annee_fin) + str(mois_fin) + str(jour_fin) + str(heure_fin) + str(minute_fin) + '.png'

  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)

  # Date
  data_date = data['DATE'] + datetime.timedelta(hours=decalage[fuseau])

  # Paramètres du graphe
  ratio = 0.2

  # Conversion à la demande
  if unite == 'km/h' :
    data_FF = data['FF']*3.6
    data_FXI = data['FXI']*3.6
    ymin = 0
    ymax = 250
    seuil = 90
  elif unite =='kt' :
    data_FF = data['FF']*3.6/1.8
    data_FXI = data['FXI']*3.6/1.8
    ymin = 0
    ymax = 140
    seuil = 50
  elif unite == 'm/s':
    data_FF = data['FF']
    data_FXI = data['FXI']
    ymin = 0
    ymax = 70
    seuil = 25
  else:
    logging.info("Unité de vent inconnue !")
    exit(1)


  # Calculs des bornes de l'axe des ordonnées
  if max(data_FXI)+abs(ratio*max(data_FXI)) > ymax:
    bmax = ymax
  else:
    bmax = max(data_FXI)+ratio*abs(max(data_FXI))
  if min(data_FXI)-ratio*min(data_FXI) < ymin:
    bmin = ymin
  else:
    bmin = min(data_FXI)-ratio*abs(min(data_FXI))

  # Tracé du graphe
  fig, ax = plt.subplots(1, 1, figsize=(16, 9))
  ax.plot(np.array(data_date),np.array(data_FXI), linewidth=1, color='brown', label='rafales')
  ax.plot(np.array(data_date),np.array(data_FF), linewidth=1, color='darkblue', label='vent moyen')
  ax.axhline(seuil, color='red', linewidth=1, linestyle='--',label='seuil tempête')
  ax.axhline(0, color='grey', linestyle='--')
#  ax.grid(b=True, which='major', axis='both', color='lightgrey', zorder=1)
  ax2=ax.twinx()
  ax2.set_ylabel('direction du vent [°]', color='black')
  ax2.plot(np.array(data_date), np.array(data['DD']), color='forestgreen', label='direction', linestyle='dashed', linewidth=0.7)
  ax2.tick_params(axis='y', labelcolor='forestgreen')
  ax.set_xlabel(f"date et heure  {str(fuseau)}")
  ax.set_ylabel(f"Vent moyen et rafales [{str(unite)}]")
  ax.autoscale(axis='x', tight='true')
  fig.autofmt_xdate()
  #ax.set_title(f"Vent moyen et rafales - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
  ax.text(x=0.5, y=1.1 , s=f"Vent moyen et rafales", fontsize=16, weight='bold', ha='center', va='bottom', transform=ax.transAxes)
  ax.text(x=0.5, y=1.05, s=f"Données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}", fontsize=8, alpha=0.75, ha='center', va='bottom', transform=ax.transAxes)
  _, ylim = ax.get_ylim()
  ax.set_ylim(bottom=bmin, top=bmax)
  l=4
  axins = inset_axes(ax, width=0.984 * l, height=0.157 * l, borderpad=0, loc="upper right")
  axins.imshow(logo, alpha=0.5)
  axins.axis('off')

  return fig, ax, chemin_figure

def figure_pression(data, unite):
  # Trace la pression atmosphérique
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)

  # Nom du fichier
  fichier_figure = "graphe_PressionMinute_" + str(annee_debut) + str(mois_debut) + str(jour_debut) + str(heure_debut) + str(minute_debut) + '-' + str(annee_fin) + str(mois_fin) + str(jour_fin) + str(heure_fin) + str(minute_fin) + '.png'

  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)

  # Date
  data_date = data['DATE'] + datetime.timedelta(hours=decalage[fuseau])

  # Paramètres du graphe
  ratio = 0.002


  # Conversion à la demande
  if unite == 'mmHg':
    data_P = data['P']*0.75
    ymax = 765
    ymin = 675
  elif unite == 'hPa':
    data_P = data['P']
    ymin = 930
    ymax = 1020
  else:
    logging.error("Unité de pression inconnue !")
    exit(1)


  # Calculs des bornes de l'axe des ordonnées
  if max(data_P)+abs(ratio*max(data_P)) > ymax:
    bmax = ymax
  else:
    bmax = max(data_P)+ratio*abs(max(data_P))
  if min(data_P)-ratio*min(data_P) < ymin:
    bmin = ymin
  else:
    bmin = min(data_P)-ratio*abs(min(data_P))


  # Tracé du graphe
  fig, ax = plt.subplots(1, 1, figsize=(16, 9))
  ax.plot(np.array(data_date),np.array(data_P), linewidth=1, color='darkblue', label='P')
  ax.axhline(0, color='grey', linestyle='--')
#  ax.grid(b=True, which='both', axis='both', color='lightgrey', zorder=1)
  ax.set_xlabel(f"date et heure {str(fuseau)}")
  ax.set_ylabel(f"Pression atmosphérique [{str(unite)}]")
  ax.autoscale(axis='x', tight='true')
  fig.autofmt_xdate()
  #ax.set_title(f"Pression atmosphérique - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
  ax.text(x=0.5, y=1.1 , s=f"Pression atmosphérique", fontsize=16, weight='bold', ha='center', va='bottom', transform=ax.transAxes)
  ax.text(x=0.5, y=1.05, s=f"Données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}", fontsize=8, alpha=0.75, ha='center', va='bottom', transform=ax.transAxes)
  _, ylim = ax.get_ylim()
  ax.set_ylim(bottom=bmin, top=bmax)
  l=4
  axins = inset_axes(ax, width=0.984*l, height=0.157*l, borderpad=0, loc="upper right")
  axins.imshow(logo, alpha=0.5)
  axins.axis('off')

  return fig, ax, chemin_figure

def figure_temperature(data,unite):
  # Trace la température sous abri et la température ressentie
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)

  # Nom du fichier
  fichier_figure = "graphe_TemperatureMinute_" + str(annee_debut) + str(mois_debut) + str(jour_debut) + str(heure_debut) + str(minute_debut) + '-' + str(annee_fin) + str(mois_fin) + str(jour_fin) + str(heure_fin) + str(minute_fin) + '.png'

  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)

  # Date
  data_date = data['DATE'] + datetime.timedelta(hours=decalage[fuseau])

  # Calcul de la température ressentie
  data_Tres = 13.12+0.6215*(data['T'])+(0.3965*data['T']-11.37)*(data['FF']*3.6)**0.16


  # Conversion à la demande
  if unite == '°C':
    data_T=data['T']
    ymin=-45
    ymax=10
    ratio=0.2
  elif unite == '°F':
    data_T=data['T']*1.8+32
    data_Tres=data_Tres*1.8+32
    ymax=10*1.8+32
    ymin=-45*1.8+32
    ratio=0.2
  elif unite == 'K' :
    data_T=data['T']+273.15
    data_Tres=data_Tres+273.15
    ymax=10+273.15
    ymin=-45+273.5
    ratio=0.002
  else:
    logging.error("Unité de température inconnue !")
    exit(1)

  # Calculs des bornes de l'axe des ordonnées
  if max(data_T)+abs(ratio*max(data_T)) > ymax:
    bmax = ymax
  else:
    bmax = max(data_T)+ratio*abs(max(data_T))
  if min(data_Tres)-ratio*min(data_Tres) < ymin :
    bmin = ymin
  else :
    bmin = min(data_Tres)-ratio*abs(min(data_Tres))


  # Tracé du graphe
  fig, ax = plt.subplots(1, 1, figsize=(16, 9))
  ax.plot(np.array(data_date),np.array(data_T), linewidth=1, color='blue', label='T sous abri')
  ax.plot(np.array(data_date),np.array(data_Tres), linewidth=1, color='black', label='T ressentie')
  ax.axhline(0, color='grey', linestyle='--')
#  ax.grid(b=True, which='both', axis='both', color='lightgrey', zorder=1)
  ax.set_xlabel(f"date et heure {str(fuseau)}")
  ax.set_ylabel(f"Températures [{str(unite)}]")
  ax.autoscale(axis='x', tight='true')
  fig.autofmt_xdate()
  #ax.set_title(f"Températures - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
  ax.text(x=0.5, y=1.1 , s=f"Températures", fontsize=16, weight='bold', ha='center', va='bottom', transform=ax.transAxes)
  ax.text(x=0.5, y=1.05, s=f"Données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}", fontsize=8, alpha=0.75, ha='center', va='bottom', transform=ax.transAxes)
  _, ylim = ax.get_ylim()
  ax.set_ylim(bottom=bmin, top=bmax)
  handles, labels = ax.get_legend_handles_labels()
  ax.legend([handles[x] for x in [0, 1]], [labels[x] for x in [0, 1]], loc="upper left", ncol=len(handles))
  l=4
  axins = inset_axes(ax, width=0.984 * l, height=0.157 * l, borderpad=0, loc="upper right")
  axins.imshow(logo, alpha=0.5)
  axins.axis('off')

  return fig, ax, chemin_figure

def figure_humidite(data):
  # Trace l'humidité relative
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)

  # Nom du fichier
  fichier_figure = "graphe_HumiditeMinute_" + str(annee_debut) + str(mois_debut) + str(jour_debut) + str(heure_debut) + str(minute_debut) + '-' + str(annee_fin) + str(mois_fin) + str(jour_fin) + str(heure_fin) + str(minute_fin) + '.png'

  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)

  # Date
  data_date = data['DATE'] + datetime.timedelta(hours=decalage[fuseau])

  # Paramètres du graphe
  ymax = 100
  ymin = 0
  unite = '%'
  ratio = 0.1
  data_U = data['U']


  # Calculs des bornes de l'axe des ordonnées
  if max(data['U'])+abs(ratio*max(data['U'])) > ymax:
    bmax = ymax
  else :
    bmax = max(data['U'])+ratio*abs(max(data['U']))
  if min(data['U'])-ratio*min(data['U']) < ymin:
    bmin = ymin
  else:
    bmin = min(data['U'])-ratio*abs(min(data['U']))

  # Tracé du graphe
  fig, ax = plt.subplots(1, 1, figsize=(16, 9))
  ax.plot(np.array(data_date),np.array(data_U), linewidth=1, color='darkblue', label='P')
  ax.axhline(0, color='grey', linestyle='--')
#  ax.grid(b=True, which='both', axis='both', color='lightgrey', zorder=1)
  ax.set_xlabel(f"date et heure {str(fuseau)}")
  ax.set_ylabel(f"Humidité relative [{str(unite)}]")
  ax.autoscale(axis='x', tight='true')
  fig.autofmt_xdate()
  #ax.set_title(f"Humidité relative - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
  ax.text(x=0.5, y=1.1 , s=f"Humidité Relative", fontsize=16, weight='bold', ha='center', va='bottom', transform=ax.transAxes)
  ax.text(x=0.5, y=1.05, s=f"Données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}", fontsize=8, alpha=0.75, ha='center', va='bottom', transform=ax.transAxes)
  #_, ylim = ax.get_ylim()  _, ylim = ax.get_ylim()
  ax.set_ylim(bottom=bmin, top=bmax)
  l=4
  axins = inset_axes(ax, width=0.984 * l, height=0.157 * l, borderpad=0, loc="upper right")
  axins.imshow(logo, alpha=0.5)
  axins.axis('off')

  return fig, ax, chemin_figure

def figure_rayonnement(data):
  # Trace le rayonnement global
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)

  # Nom du fichier
  fichier_figure = "graphe_RayonnementMinute_" + str(annee_debut) + str(mois_debut) + str(jour_debut) + str(heure_debut) + str(minute_debut) + '-' + str(annee_fin) + str(mois_fin) + str(jour_fin) + str(heure_fin) + str(minute_fin) + '.png'

  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)

  # Date
  data_date = data['DATE'] + datetime.timedelta(hours=decalage[fuseau])

  # Paramètres du graphe
  ymax = 900
  ymin = 0
  unite = 'W/m2'
  ratio = 0.1
  data_RG = data['RG']/60


  # Calculs des bornes de l'axe des ordonnées
  if max(data_RG)+abs(ratio*max(data_RG)) > ymax:
    bmax = ymax
  else :
    bmax = max(data_RG)+ratio*abs(max(data_RG))
  if min(data_RG)-ratio*min(data_RG) < ymin:
    bmin = ymin
  else:
    bmin = min(data_RG)-ratio*abs(min(data_RG))

  # Tracé du graphe
  fig, ax = plt.subplots(1, 1, figsize=(16, 9))
  ax.plot(np.array(data_date),np.array(data_RG), linewidth=1, color='darkblue', label='P')
  ax.axhline(0, color='grey', linestyle='--')
#  ax.grid(b=True, which='both', axis='both', color='lightgrey', zorder=1)
  ax.set_xlabel(f"date et heure {str(fuseau)}")
  ax.set_ylabel(f"Rayonnement Global [{str(unite)}]")
  ax.autoscale(axis='x', tight='true')
  fig.autofmt_xdate()
  #ax.set_title(f"Rayonnement Global - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
  ax.text(x=0.5, y=1.1 , s=f"Rayonnement global", fontsize=16, weight='bold', ha='center', va='bottom', transform=ax.transAxes)
  ax.text(x=0.5, y=1.05, s=f"Données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}", fontsize=8, alpha=0.75, ha='center', va='bottom', transform=ax.transAxes)
  _, ylim = ax.get_ylim()
  ax.set_ylim(bottom=bmin, top=bmax)
  l=4
  axins = inset_axes(ax, width=0.984 * l, height=0.157 * l, borderpad=0, loc="upper right")
  axins.imshow(logo, alpha=0.5)
  axins.axis('off')

  return fig, ax, chemin_figure


def get_dpi():
  # Récupération du DPI de l'écran
  screen = Tk()
  current_dpi = screen.winfo_fpixels('1i')
  screen.destroy()
  return current_dpi

def affichage_figure(canvas, figure):
  # Affichage de la figure
  tkcanvas = FigureCanvasTkAgg(figure, canvas)
  tkcanvas.draw()
  tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
  return tkcanvas

def modification_date(window):
  # Modification de la string dates_choisies, vérification de la cohérence avec les données en mémoire
  dates_choisies = jour_debut + "/" + mois_debut + "/" + annee_debut + " - " + heure_debut + ":" + minute_debut + "  >>>  " + jour_fin + "/" + mois_fin + "/" + annee_fin + " - " + heure_fin + ":" + minute_fin
  if donnees_en_memoire != vide:
    if dates_choisies == donnees_en_memoire:
      window['-donnees_en_memoire-'].update(donnees_en_memoire, "darkgreen", "white" )
    else:
      window['-donnees_en_memoire-'].update(donnees_en_memoire + " - récupération requise !", "darkred", "white" )

#############  PROGRAMME PRINCIPAL #############

if (__name__ == "__main__"):
  # Paramètres fixes
  jours = ["{:02d}".format(x) for x in range(1,32)]
  mois = ["{:02d}".format(x) for x in range(1,13)]
  annees = ["{:04d}".format(x) for x in range(1900,2100)]
  heures = ["{:02d}".format(x) for x in range(0,24)]
  minutes = ["{:02d}".format(x) for x in range(0,60)]
  decalage = {'UTC':0, 'DDU':10}
  logo = plt.imread("logo_MF.png")
  vide = "  mémoire vide - récupération requise !"

  # Lecture des paramètres initiaux (visu_minute_ddu.json)

  ## Définition du fichier des paramètres : un json
  sg.user_settings_filename(path='.',filename='visu_minute_ddu.json')

  ## Dates / heures / décalage
  aujourdhui = datetime.datetime.today()
  date_debut = aujourdhui.strftime("%d-%m-%Y")
  jour_debut = sg.user_settings_get_entry('-jour_debut-', date_debut[0:2])
  mois_debut = sg.user_settings_get_entry('-mois_debut-', date_debut[3:5])
  annee_debut = sg.user_settings_get_entry('-annee_debut-', date_debut[6:10])
  temps_debut = aujourdhui.strftime("%H:%M")
  heure_debut = sg.user_settings_get_entry('-heure_debut-', temps_debut[0:2])
  minute_debut = sg.user_settings_get_entry('-minute_debut-', temps_debut[3:5])
  date_fin = aujourdhui.strftime("%d-%m-%Y")
  jour_fin = sg.user_settings_get_entry('-jour_fin-', date_fin[0:2])
  mois_fin = sg.user_settings_get_entry('-mois_fin-', date_fin[3:5])
  annee_fin = sg.user_settings_get_entry('-annee_fin-', date_fin[6:10])
  temps_fin = aujourdhui.strftime("%H:%M")
  heure_fin = sg.user_settings_get_entry('-heure_fin-', temps_fin[0:2])
  minute_fin = sg.user_settings_get_entry('-minute_fin-', temps_fin[3:5])
  fuseau = sg.user_settings_get_entry('-fuseau-', 'DDU')

  ## Emplacements
  emplacement_minute = sg.user_settings_get_entry('-emplacement_minute-', os.path.join("N:/partageMto_DON_SA/Minute/", annee_debut))
  emplacement_figure = sg.user_settings_get_entry('-emplacement_figure-', os.path.join(os.path.dirname(__file__), 'figures'))
  emplacement_csv = sg.user_settings_get_entry('-emplacement_csv-', os.path.join(os.path.dirname(__file__), 'csv'))

  ## Dates choisies pour les données minutes 
  dates_choisies = jour_debut + "/" + mois_debut + "/" + annee_debut + " - " + heure_debut + ":" + minute_debut + "  >>>  " + jour_fin + "/" + mois_fin + "/" + annee_fin + " - " + heure_fin + ":" + minute_fin

  ## Données en mémoire
  donnees_en_memoire = vide

  ## Unités des figures
  unite_vent = sg.user_settings_get_entry('-unite_vent-', 'kt')
  unite_pression = sg.user_settings_get_entry('-unite_pression-', 'hPa')
  unite_temperature = sg.user_settings_get_entry('-unite_temperature-', '°C')
  chemin_figure = None

  ## Export CSV
  csv_p = sg.user_settings_get_entry('-csv_p-', True)
  csv_t = sg.user_settings_get_entry('-csv_t-', True)
  csv_u = sg.user_settings_get_entry('-csv_u-', True)
  csv_ff = sg.user_settings_get_entry('-csv_ff-', True)
  csv_fi = sg.user_settings_get_entry('-csv_fi-', True)
  csv_dd = sg.user_settings_get_entry('-csv_dd-', True)
  csv_vis = sg.user_settings_get_entry('-csv_vis-', False)

  # Interface graphique
  sg.theme('Dark Blue 3')
  ## Frame 1 : emplacements
  sg_emplacement_minute = [ [ sg.Text('Fichiers "Minute"', size=13),
                              sg.In(size=(80,1), enable_events=True ,key='-emplacement_minute-', default_text=emplacement_minute),
                              sg.FolderBrowse("Répertoires") ] ]

  sg_emplacement_csv = [ [sg.Text('Fichiers csv', size=13),
                          sg.In(size=(80,1), enable_events=True ,key='-emplacement_csv-', default_text=emplacement_csv),
                          sg.FolderBrowse("Répertoires") ] ]

  sg_emplacement_figure = [ [ sg.Text('Figures', size=13),
                              sg.In(size=(80,1), enable_events=True ,key='-emplacement_figure-', default_text=emplacement_figure),
                              sg.FolderBrowse("Répertoires") ] ]

  frame_layout_emplacement = [ [ sg.Column(sg_emplacement_minute, element_justification='c') ],
                               [ sg.Column(sg_emplacement_csv, element_justification='c') ],
                               [ sg.Column(sg_emplacement_figure, element_justification='c') ] ]

  ## Frame 2.1 : dates / heures
  sg_date_temps_debut = [ [ sg.Text('Date de début: ', size=12),
                            sg.Combo(jours, size=(3, 1), default_value=jour_debut, enable_events=True ,key='-jour_debut-', bind_return_key='-jour_debut-'),
                            sg.Combo(mois, size=(3, 1), default_value=mois_debut, enable_events=True ,key='-mois_debut-', bind_return_key='-mois_debut-'),
                            sg.Combo(annees, size=(5, 1), default_value=annee_debut, enable_events=True ,key='-annee_debut-', bind_return_key='-annee_debut-'),
                            sg.Button('Cal', key='-selection_date_debut-'),
                            sg.Text('Heure de début : ', size=13),
                            sg.Combo(heures, size=(3, 1), default_value=heure_debut, enable_events=True ,key='-heure_debut-', bind_return_key='-heure_debut-'),
                            sg.Combo(minutes, size=(3, 1), default_value=minute_debut, enable_events=True ,key='-minute_debut-', bind_return_key='-minute_debut-') ] ]

  sg_date_temps_fin = [ [ sg.Text('Date de fin: ', size=12),
                          sg.Combo(jours, size=(3, 1), default_value=jour_fin, enable_events=True ,key='-jour_fin-', bind_return_key='-jour_fin-'),
                          sg.Combo(mois, size=(3, 1), default_value=mois_fin, enable_events=True ,key='-mois_fin-', bind_return_key='-mois_fin-'),
                          sg.Combo(annees, size=(5, 1), default_value=annee_fin, enable_events=True ,key='-annee_fin-', bind_return_key='-annee_fin-'),
                          sg.Button('Cal', key='-selection_date_fin-'),
                          sg.Text('Heure de fin : ', size=13),
                          sg.Combo(heures, size=(3, 1), default_value=heure_fin, enable_events=True ,key='-heure_fin-', bind_return_key='-heure_fin-'),
                          sg.Combo(minutes, size=(3, 1), default_value=minute_fin, enable_events=True ,key='-minute_fin-', bind_return_key='-minute_fin-') ] ]


  layout_date_temps = sg.Column( [ [ sg.Column(sg_date_temps_debut, element_justification='c') ],
                                   [ sg.Column(sg_date_temps_fin, element_justification='c') ] ],
                                 element_justification='c' )

  ## Frame 2.2 : décalage horaire
  sg_decalage = sg.Column( [ [ sg.Radio('UTC (+00)', size=(15,1), group_id=1, default=(fuseau=='UTC'), enable_events=True, key='-decalage_utc-') ],
                             [ sg.Radio('DDU (+10)', size=(15,1), group_id=1, default=(fuseau=='DDU'), enable_events=True, key='-decalage_ddu-') ]  ],
                           element_justification='c')
                           
  ## Frame 2 : date / heure / décalage horaire
  frame_layout_date_temps_decalage = [ [ sg.Column( [ [ layout_date_temps, sg_decalage] ], element_justification='c' ) ] ]

  ## Frame 3 : récupération des données
  sg_donnees = [ [ sg.Button('Récupérer', enable_events=True ,key='-recuperation_donnees-'),
                   sg.Text('Données actuellement chargées:', justification='right'),
                   sg.Text(donnees_en_memoire, background_color="darkred", text_color='white', key='-donnees_en_memoire-', justification='left') ] ]

  frame_donnees = [ [sg.Column(sg_donnees, element_justification='c') ] ]

  ## Frame 4 : figure "Minute"
  sg_figure = [ [ sg.Button('Vent', size=(12,1), enable_events=True ,key='-figure_vent-'),
                  sg.Radio('m/s', size=(7,1), group_id=2, default=(unite_vent=='m/s'), enable_events=True, key='-unite_vent_ms-'),
                  sg.Radio('km/h', size=(7,1), group_id=2, default=(unite_vent=='km/h'), enable_events=True, key='-unite_vent_kmh-'),
                  sg.Radio('kt', size=(7,1), group_id=2, default=(unite_vent=='kt'), enable_events=True, key='-unite_vent_kt-'),
                  sg.Radio('beaufort', size=(7,1), group_id=2, default=(unite_vent=='bf'), enable_events=True, key='-unite_vent_bf-'),  ],
                [ sg.Button('Pression', size=(12,1), enable_events=True ,key='-figure_pression-'),
                  sg.Radio('mmHg', size=(7,1), group_id=3, default=(unite_pression=='mmHg'), enable_events=True, key='-unite_pression_mmhg-'),
                  sg.Radio('hPa', size=(7,1), group_id=3, default=(unite_pression=='hPa'), enable_events=True, key='-unite_pression_hpa-')  ],
                [ sg.Button('Temperature', size=(12,1), enable_events=True ,key='-figure_temperature-'),
                  sg.Radio('°C', size=(7,1), group_id=4, default=(unite_temperature=='°C'), enable_events=True, key='-unite_temperature_c-'),
                  sg.Radio('°F', size=(7,1), group_id=4, default=(unite_temperature=='°F'), enable_events=True, key='-unite_temperature_f-'),
                  sg.Radio('K', size=(7,1), group_id=4, default=(unite_temperature=='K'), enable_events=True, key='-unite_temperature_k-'),  ],
                [ sg.Button('Humidité', size=(12,1), enable_events=True ,key='-figure_humidite-') ],
                [ sg.Button('Rayonnement', size=(12,1), enable_events=True ,key='-figure_rayonnement-') ],
                [ sg.Button('Autres', size=(12,1), enable_events=True ,key='-figure_autres-') ],
                [ sg.Button('Exporter la figure en PNG', enable_events=True ,key='-export_figure-', expand_x=True) ] ]

  sg_export_csv = [ [ sg.Checkbox('P', default=csv_p, enable_events=True, key='-csv_p-'),
                      sg.Checkbox('T', default=csv_t, enable_events=True, key='-csv_t-'),
                      sg.Checkbox('U', default=csv_u, enable_events=True, key='-csv_u-'),
                      sg.Checkbox('FF', default=csv_ff, enable_events=True, key='-csv_ff-'),
                      sg.Checkbox('FI', default=csv_fi, enable_events=True, key='-csv_fi-'),
                      sg.Checkbox('DD', default=csv_dd, enable_events=True, key='-csv_dd-'),
                      sg.Checkbox('VIS', default=csv_vis, enable_events=True, key='-csv_vis-') ],
                    [ sg.Button('Exporter au format CSV', enable_events=True ,key='-export_csv-', expand_x=True) ] ]

  frame_figure = [ [ sg.Column(sg_figure, element_justification='l', expand_x=True) ] ]
  frame_csv = [ [ sg.Column(sg_export_csv, element_justification='l', expand_x=True) ] ]

  # Layout gauche
  layout_gauche = [ [ sg.Frame('Emplacements des données "Minutes"', frame_layout_emplacement, expand_x=True) ],
                    [ sg.Frame('Dates / heures / Fuseau des données "Minute" ', frame_layout_date_temps_decalage, expand_x=True) ],
                    [ sg.Frame('Récupération des données "Minutes"', frame_donnees, expand_x=True) ],
                    [ sg.Frame('Figure / export PNG des données "Minutes"', frame_figure, expand_x=True), sg.Image("logo_MF.png") ],
                    [ sg.Frame('Export CSV des données "Minutes"', frame_csv, expand_x=True) ],
                    [ sg.Image("ddu.png", size=(800, 320)) ] ]

  # Layout droite
  layout_droite = [ [sg.Frame('Figure "Minute"', [[sg.Canvas(key='-CANVAS-', background_color='white', size = (16*get_dpi(), 10.25*get_dpi()))]]) ] ]

  ## Layout total
  layout = [ [ sg.Column(layout_gauche, element_justification='c', vertical_alignment='top'), sg.Column(layout_droite, element_justification='c', vertical_alignment='top') ] ]

  ## Création de la fenêtre
  window = sg.Window('Visualisation simple des fichiers "Minutes" - DDU', layout, resizable=True)

  # Gestion des événements
  while True:
    ## Récupération de l'événement et des valeurs
    event, values = window.read()
    if event != None:
      logging.info("Event: " + event)

    ## Quitter normalement
    if event in (sg.WIN_CLOSED, 'Exit'):
      break

    ## Emplacements
    if event == '-emplacement_minute-':
      logging.info("Value: " + values[event])
      emplacement_minute = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-emplacement_figure-':
      logging.info("Value: " + values[event])
      emplacement_figure = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-emplacement_csv-':
      logging.info("Value: " + values[event])
      emplacement_csv = values[event]
      sg.user_settings_set_entry(event, values[event])

    ## Date / heure de début fichier minute
    if event == '-jour_debut-':
      logging.info("Value: " + values[event])
      jour_debut = values[event].zfill(2)
      window[event].update(jour_debut)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-mois_debut-':
      logging.info("Value: " + values[event])
      mois_debut = values[event].zfill(2)
      window[event].update(mois_debut)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-annee_debut-':
      logging.info("Value: " + values[event])
      annee_debut = values[event].zfill(4)
      window[event].update(annee_debut)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-heure_debut-':
      logging.info("Value: " + values[event])
      heure_debut = values[event].zfill(2)
      window[event].update(heure_debut)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-minute_debut-':
      logging.info("Value: " + values[event])
      minute_debut = values[event].zfill(2)
      window[event].update(minute_debut)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-selection_date_debut-':
      date_debut_tuple = sg.popup_get_date(start_mon=int(mois_debut), start_day=int(jour_debut), start_year=int(annee_debut), begin_at_sunday_plus=1, title="Date de début")
      logging.info("Tuple:" + str(date_debut_tuple))
      if date_debut_tuple is not None:
        jour_debut = str(date_debut_tuple[1]).zfill(2)
        mois_debut = str(date_debut_tuple[0]).zfill(2)
        annee_debut = str(date_debut_tuple[2]).zfill(2)
        window['-jour_debut-'].update(jour_debut)
        window['-mois_debut-'].update(mois_debut)
        window['-annee_debut-'].update(annee_debut)
        datetime_str = mois_debut+'/'+jour_debut+'/'+annee_debut+' 00:00:00'
        datetime_object = datetime.datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
        if datetime_object >= datetime.datetime.today():
          sg.popup_ok("La date de debut est dans le futur !", title="Erreur", keep_on_top=True)
        else:
          sg.user_settings_set_entry('-jour_debut-', values['-jour_debut-'])
          sg.user_settings_set_entry('-mois_debut-', values['-mois_debut-'])
          sg.user_settings_set_entry('-annee_debut-', values['-annee_debut-'])

    ## Date / heure de fin fichier minute
    if event == '-jour_fin-':
      logging.info("Value: " + values[event])
      jour_fin = values[event].zfill(2)
      window[event].update(jour_fin)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-mois_fin-':
      logging.info("Value: " + values[event])
      mois_fin = values[event].zfill(2)
      window[event].update(mois_fin)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-annee_fin-':
      logging.info("Value: " + values[event])
      annee_fin = values[event].zfill(4)
      window[event].update(annee_fin)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-heure_fin-':
      logging.info("Value: " + values[event])
      heure_fin = values[event].zfill(2)
      window[event].update(heure_fin)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-minute_fin-':
      logging.info("Value: " + values[event])
      minute_fin = values[event].zfill(2)
      window[event].update(minute_fin)
      modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-selection_date_fin-':
      date_fin_tuple = sg.popup_get_date(start_mon=int(mois_fin), start_day=int(jour_fin), start_year=int(annee_fin), begin_at_sunday_plus=1, title="Date de début")
      logging.info("Tuple:" + str(date_fin_tuple))
      if date_fin_tuple is not None:
        jour_fin = str(date_fin_tuple[1]).zfill(2)
        mois_fin = str(date_fin_tuple[0]).zfill(2)
        annee_fin = str(date_fin_tuple[2]).zfill(2)
        window['-jour_fin-'].update(jour_fin)
        window['-mois_fin-'].update(mois_fin)
        window['-annee_fin-'].update(annee_fin)
        datetime_str = mois_fin+'/'+jour_fin+'/'+annee_fin+' 00:00:00'
        datetime_object = datetime.datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
        if datetime_object >= datetime.datetime.today():
          sg.popup_ok("La date de fin est dans le futur !", title="Erreur", keep_on_top=True)
        else:
          sg.user_settings_set_entry('-jour_fin-', values['-jour_fin-'])
          sg.user_settings_set_entry('-mois_fin-', values['-mois_fin-'])
          sg.user_settings_set_entry('-annee_fin-', values['-annee_fin-'])

    ## Décalage horaire fichier minute
    if event == '-decalage_utc-':
      logging.info("Fuseau: UTC")
      fuseau = 'UTC'
      sg.user_settings_set_entry('-fuseau-', fuseau)
    if event == '-decalage_ddu-':
      logging.info("Fuseau: DDU")
      fuseau = 'DDU'
      sg.user_settings_set_entry('-fuseau-', fuseau)

    ## Récupération des données fichier minute
    if event == '-recuperation_donnees-':
      data, success = recuperation_donnees()
      if success:
        donnees_en_memoire = jour_debut + "/" + mois_debut + "/" + annee_debut + " - " + heure_debut + ":" + minute_debut + "  >>>  " + jour_fin + "/" + mois_fin + "/" + annee_fin + " - " + heure_fin + ":" + minute_fin
        window['-donnees_en_memoire-'].update(donnees_en_memoire, "green", "white" )

    ## Figure vent fichier minute
    if event == '-unite_vent_ms-':
      unite_vent = 'm/s'
      logging.info("unite_vent:" + unite_vent)
      sg.user_settings_set_entry('-unite_vent-', unite_vent)
    if event == '-unite_vent_kmh-':
      unite_vent = 'km/h'
      logging.info("unite_vent:" + unite_vent)
      sg.user_settings_set_entry('-unite_vent-', unite_vent)
    if event == '-unite_vent_kt-':
      unite_vent = 'kt'
      logging.info("unite_vent:" + unite_vent)
      sg.user_settings_set_entry('-unite_vent-', unite_vent)
    if event == '-unite_vent_bf-':
      unite_vent = 'kt'
      logging.info("unite_vent:" + unite_vent)
      sg.user_settings_set_entry('-unite_vent-', unite_vent)
      sg.popup_ok("Pas de encore de figure pour ce bouton ", title="Erreur", keep_on_top=True)
    if event == '-figure_vent-':
      logging.info("figure_vent")
      if donnees_en_memoire == vide:
        sg.popup_ok("Mémoire vide... Récupérez des données et recommencez !", title="Erreur", keep_on_top=True)
      else:
        if 'tkcanvas' in globals():
          tkcanvas.get_tk_widget().destroy()
        if event == '-unite_vent_bf-':
          sg.popup_ok("Pas encore de figure pour les indices beaufort", title="Erreur", keep_on_top=True)
        else:
          fig, ax, chemin_figure = figure_vent(data, unite_vent)
          tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)

    ## Figure pression fichier minute
    if event == '-unite_pression_mmhg-':
      unite_pression = 'mmHg'
      logging.info("unite_pression:" + unite_pression)
      sg.user_settings_set_entry('-unite_pression-', unite_pression)
    if event == '-unite_pression_hpa-':
      unite_pression = 'hPa'
      logging.info("unite_pression:" + unite_pression)
      sg.user_settings_set_entry('-unite_pression-', unite_pression)
    if event == '-figure_pression-':
      logging.info("figure_pression")
      if donnees_en_memoire == vide:
        sg.popup_ok("Mémoire vide... Récupérez des données et recommencez !", title="Erreur", keep_on_top=True)
      else:
        if 'tkcanvas' in globals():
          tkcanvas.get_tk_widget().destroy()
        fig, ax, chemin_figure = figure_pression(data,unite_pression)   # unité possibles : 'hPa' ou 'mmHg'
        tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)

    ## Figure température fichier minute
    if event == '-unite_temperature_c-':
      unite_temperature = '°C'
      logging.info("unite_temperature:" + unite_temperature)
      sg.user_settings_set_entry('-unite_temperature-', unite_temperature)
    if event == '-unite_temperature_f-':
      unite_temperature = '°F'
      logging.info("unite_temperature:" + unite_temperature)
      sg.user_settings_set_entry('-unite_temperature-', unite_temperature)
    if event == '-unite_temperature_k-':
      unite_temperature = 'K'
      logging.info("unite_temperature:" + unite_temperature)
      sg.user_settings_set_entry('-unite_temperature-', unite_temperature)
    if event == '-figure_temperature-':
      logging.info("figure_temperature")
      if donnees_en_memoire == vide:
        sg.popup_ok("Mémoire vide... Récupérez des données et recommencez !", title="Erreur", keep_on_top=True)
      else:
        if 'tkcanvas' in globals():
          tkcanvas.get_tk_widget().destroy()
        fig, ax, chemin_figure = figure_temperature(data,unite_temperature)   # unité possibles : 'hPa' ou 'mmHg'
        tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)

    ## Figure humidité
    if event == '-figure_humidite-':
      logging.info("figure_humidite")
      if donnees_en_memoire == vide:
        sg.popup_ok("Mémoire vide... Récupérez des données et recommencez !", title="Erreur", keep_on_top=True)
      else:
        if 'tkcanvas' in globals():
          tkcanvas.get_tk_widget().destroy()
        fig, ax, chemin_figure = figure_humidite(data)
        tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)

    ## Figure rayonnement fichier minute
    if event == '-figure_rayonnement-':
      logging.info("figure_rayonnement")
      if donnees_en_memoire == vide:
        sg.popup_ok("Mémoire vide... Récupérez des données et recommencez !", title="Erreur", keep_on_top=True)
      else:
        if 'tkcanvas' in globals():
          tkcanvas.get_tk_widget().destroy()
        fig, ax, chemin_figure = figure_rayonnement(data)
        tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)

    ## Figure autres fichier minute
    if event == '-figure_autres-':
      logging.info("figure_autres")
      if donnees_en_memoire == vide:
        sg.popup_ok("Mémoire vide... Récupérez des données et recommencez !", title="Erreur", keep_on_top=True)
      else:
        sg.popup_ok("Pas de encore de figure pour ce bouton ", title="Erreur", keep_on_top=True)

    ## Export figure fichier minute
    if event == '-export_figure-':
      if chemin_figure == None:
        sg.popup_ok("Impossible d'exporter une figure qui n'existe pas !", title="Erreur", keep_on_top=True)
      else:
        plt.savefig(chemin_figure, bbox_inches="tight")
        plt.close(fig)
        sg.popup_ok("Fichier " + chemin_figure + " exporté", title="Confirmation", keep_on_top=True)

    ## Paramètres csv fichier minute
    if event == '-csv_p-':
      logging.info("Value: " + str(values[event]))
      csv_p = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-csv_t-':
      logging.info("Value: " + str(values[event]))
      csv_t = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-csv_ff-':
      logging.info("Value: " + str(values[event]))
      csv_ff = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-csv_dd-':
      logging.info("Value: " + str(values[event]))
      csv_dd = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-csv_fi-':
      logging.info("Value: " + str(values[event]))
      csv_fi = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-csv_u-':
      logging.info("Value: " + str(values[event]))
      csv_u = values[event]
      sg.user_settings_set_entry(event, values[event])
    if event == '-csv_vis-':
      logging.info("Value: " + str(values[event]))
      csv_vis = values[event]
      sg.user_settings_set_entry(event, values[event])

    ## Export csv
    if event == '-export_csv-':
      if donnees_en_memoire == vide:
        sg.popup_ok("Mémoire vide... Récupérez des données et recommencez !", title="Erreur", keep_on_top=True)
      else:
        logging.info("export_csv")
        write_data(data=data, P=csv_p, T=csv_t, FMOY=csv_ff, DMOY=csv_dd, FINS=csv_fi, HU=csv_u, VIS=csv_vis)

  # Fermeture de la fenêtre
  window.close()
