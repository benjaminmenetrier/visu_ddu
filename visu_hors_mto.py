# -*- coding: utf-8 -*-
"""
Created on Aout 2024
@authors : Rachel Honnert (TA74)

Ce script crée une interface graphique (GUI) permettant de visualiser les données quo ne viennent pas de Cobalt  : 
elles sont sur Groberg  : 
 - Ceilomètre : 
 - Pluviomètre : 
 - Camera Infoclimat : 
.-.Données du marégraphe 
.-.Données satellites 
ou ce sont des données RS 
 - RS : => une journée : T, U, FF,DD, vitesse verticale 
        => graphiques cumulés de Florent Tence 
# --------------------------------------------------------------------------
# Graphiques de base du RS : 
# 3 graphiques dans un fichier
# - température et humidité relative (saturation par rapport à l'eau liquide et la glace)
# - vent (force et direction) 
# - vitesse de montée du ballon 
# --------------------------------------------------------------------------
# Fonction lecture_rs 
# Auteur : R. Honnert à partir d'une fonction de Florent Tence
# Date : mars 2024
# Cette fonction récupère les données de RS correspondant à la date en entrée
# entrée : date au format "annee-mois-jour"
# sortie : altitude, la pression et la température, humidité vent (force et direction) à la montée et à la descente 
# --------------------------------------------------------------------------


Utilisation :
    python visu_hors_mto.py ou double clic sur un bouton du bureau : VISU_HORS_MTO

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
logging.basicConfig(level=logging.DEBUG, filename="py_hors_cobalt_log.log",filemode="w")
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

#def modification_date(window):
#  # Modification de la string dates_choisies, vérification de la cohérence avec les données en mémoire
#  dates_choisies = jour + "/" + mois + "/" + annee + "  >>>  " + jour_fin + "/" + mois_fin + "/" + annee_fin 
#  if donnees_en_memoire != vide:
#    if dates_choisies == donnees_en_memoire:
#      window['-donnees_en_memoire-'].update(donnees_en_memoire, "darkgreen", "white" )
#    else:
#      window['-donnees_en_memoire-'].update(donnees_en_memoire + " - récupération requise !", "darkred", "white" )

def recuperation_fichiers_ceilo():
  date_locale = datetime.datetime(int(annee),int(mois),int(jour))
  if date_locale >= datetime.datetime.today():
    sg.popup_ok("La date est dans le futur !", title="Erreur", keep_on_top=True)
    return False
  else :
    layout, row, cols, length = [], [], 2, int(nb_jours)
    for i in reversed(range(length)):
      date=date_locale-datetime.timedelta(days=i)
      ddmmyyhhmm=date.strftime("%Y%m%d")
      fichier = "TempCALVA_CL31_"+ddmmyyhhmm+"_1.png"
      image = os.path.join(emplacement_ceilo, fichier)
      row.append(sg.Image(image, subsample=2))
      if (i%cols) == cols-2 or i == 0 :
        layout.append(row)
        row = []
    sg.Window('Ceilomètre', layout, resizable=True).read(close=True)
    return True 

def recuperation_fichiers_pluvio():
  # Date locale de début, date locale de fin
  date_locale = datetime.datetime(int(annee),int(mois),int(jour))
  if date_locale >= datetime.datetime.today():
    sg.popup_ok("La date est dans le futur !", title="Erreur", keep_on_top=True)
    return False
  else :
    # J'utilise le premier fichier de cette date 
    my_var=r"\\mtoservice\Labos\CALVA\Pluviometre\pluvio_mass_"+date_locale.strftime("%Y-%m-%d")+r"_00h15.png"
    subprocess.Popen(fr'explorer /select, "{my_var}"')
    return True 

def recuperation_fichiers_mrr():
  # Date locale de début, date locale de fin
  date_locale = datetime.datetime(int(annee),int(mois),int(jour))
  if date_locale >= datetime.datetime.today():
    sg.popup_ok("La date est dans le futur !", title="Erreur", keep_on_top=True)
    return False
  else :
    # J'utilise le premier fichier de cette date 
    path=r"\\mtoservice\Labos\CALVA\MRR"
    my_var=os.path.join(path, date_locale.strftime("%Y-%m-%d")+r"_00h15.png")
    subprocess.Popen(fr'explorer /select, "{my_var}"')
    return True 

def recuperation_fichiers_camera():
  # Date locale de début, date locale de fin
  date_locale = datetime.datetime(int(annee),int(mois),int(jour))
  if date_locale >= datetime.datetime.today():
    sg.popup_ok("La date est dans le futur !", title="Erreur", keep_on_top=True)
    return False
  else :
    # J'utilise le premier fichier de cette date 
    my_var=r"\\groberg\Groberg\meteo\Camera\20"+date_locale.strftime("%y%m%d")
    subprocess.Popen(fr'explorer /select, "{my_var}"')
    return True 

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

def extract_data_rs_T(date):
  alt_tot,P_tot,T_tot,U_tot,FF_tot,DD_tot,As_tot = [], [], [], [], [], [], [] 
  alt_tot,P_tot,T_tot,U_tot,FF_tot,DD_tot,As_tot=lecture_rs(date)
  alt,alt_d,T,U,U_d,T_d,U2,U2_d = [], [], [], [], [], [], [], [] # altitude, température, humidité
  if not not(alt_tot) :
    imax=alt_tot.index(max(alt_tot))
    alt=alt_tot[0:imax]
    alt_d=alt_tot[(imax+1):len(alt_tot)]
    P=P_tot[0:imax]
    T=T_tot[0:imax]
    U=U_tot[0:imax]
    P_d=P_tot[(imax+1):len(alt_tot)]
    T_d=T_tot[(imax+1):len(alt_tot)]
    U_d=U_tot[(imax+1):len(alt_tot)]
    # Humidité / saturation par rapport à la glace
    To = 273.15 # température de condensation
    Lv = 2257 # chaleur latente de vaporisation (kJ/kg)
    Ls = 2800 # chaleur latente de sublimation (kJ/kg)
    R  = 8.314 # constante des gaz parfaits
    Me =0.018 # masse molaire de l'eau (kg/mol)
    Ma =0.029 # masse molaire de l'air sec (kg/mol)
    e  =[0.61*np.exp(21.87*(x-To)/(x-To+265.5)) for x in T] 
    e_d=[0.61*np.exp(21.87*(x-To)/(x-To+265.5)) for x in T_d]
    U2 = [U[i]*np.exp((Lv-Ls)/R*(1/To-1/T[i])*(e[i]*Me*Me+(P[i]-e[i])*Ma*Ma)/((P[i]-e[i])*Ma+e[i]*Me)) for i in range(len(P))]
    U2_d = [U_d[i]*np.exp((Lv-Ls)/R*(1/To-1/T_d[i])*(e_d[i]*Me*Me+(P_d[i]-e_d[i])*Ma*Ma)/((P_d[i]-e_d[i])*Ma+e_d[i]*Me)) for i in range(len(P_d))]
  return T, U, U2, T_d, U_d, U2_d, alt,alt_d 

def extract_data_rs_FF(date):
  alt_tot,P_tot,T_tot,U_tot,FF_tot,DD_tot,As_tot = [], [], [], [], [], [], [] 
  alt_tot,P_tot,T_tot,U_tot,FF_tot,DD_tot,As_tot=lecture_rs(date)
  FF,DD,FF_d,DD_d, alt,alt_d = [], [], [], [], [], [] # l'altitude, vent ff et direction 
  if not not(alt_tot) :
    imax=alt_tot.index(max(alt_tot))
    alt=alt_tot[0:imax]
    alt_d=alt_tot[(imax+1):len(alt_tot)]
    FF=FF_tot[0:imax]
    DD=DD_tot[0:imax]
    FF_d=FF_tot[(imax+1):len(alt_tot)]
    DD_d=DD_tot[(imax+1):len(alt_tot)]
  return FF,DD,FF_d,DD_d, alt,alt_d 
  
def extract_data_rs_Vi(date):
  alt_tot,P_tot,T_tot,U_tot,FF_tot,DD_tot,As_tot = [], [], [], [], [], [], [] # l'altitude, la pression, la température, l'humidité, vent ff et direction, vitesse ascendente 
  alt_tot,P_tot,T_tot,U_tot,FF_tot,DD_tot,As_tot=lecture_rs(date)
  As,As_d, alt,alt_d = [], [], [], []
  if not not(alt_tot) :
    imax=alt_tot.index(max(alt_tot))
    alt=alt_tot[0:imax]
    alt_d=alt_tot[(imax+1):len(alt_tot)]
    As=As_tot[0:imax]
    As_d=As_tot[(imax+1):len(alt_tot)]
  return As, As_d, alt,alt_d 
  
def figure_tempe_rs(date,unite):
  # Trace du profil rs de température et d'humidité
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)
  # Nom du fichier
  fichier_figure = "graphe_RS_" + str(annee) + str(mois) + str(jour) +'.png'
  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)
  # graphics
  alt,alt_d,T,U,U_d,T_d,U2,U2_d = [], [], [], [], [], [], [], [] # altitude, température, humidité 
  T, U, U2, T_d, U_d, U2_d, alt, alt_d=extract_data_rs_T(date)
    # Conversion à la demande
  if unite == '°C':
    print("coucou")
  elif unite == '°F':
    T=[x*1.8+32 for x in T]
    T_d=[x*1.8+32 for x in T_d]
  elif unite == 'K' :
    T=[x+273.15 for x in T]
    T_d=[x+273.15 for x in T_d]
  else:
    logging.error("Unité de température inconnue !")
    exit(1)
  fontsize=10
  fig, ax1 = plt.subplots(1, 1, figsize=(16, 9))
  fig.suptitle("RS du "+date+" \n", fontsize=10)
  if not not(T) :
    l1=ax1.plot(T, alt, color='red', label='T montée')
    l2=ax1.plot(T_d, alt_d, "--",color='red', label='T descente')
    twinax1 = ax1.twiny()
    l3=twinax1.plot(U, alt, color='blue', label='Hu montée')
    l4=twinax1.plot(U_d, alt_d, "--", label='Hu descente')
    # humidité relative / saturation par rapport à la glace
    l5=twinax1.plot(U2, alt, color='orange', label='Hu ice montée')
    l6=twinax1.plot(U2_d, alt_d, "--",color='orange', label='Hu ice descente')
    # axis title
    ax1.title.set_text("Température et Humidité")
    ax1.set_ylabel('Altitude [km]', fontsize=fontsize+4)
    if unite == '°C' :
      ax1.set_xlabel("Température [°C]", fontsize=fontsize)
    elif unite == '°F' :
      ax1.set_xlabel("Température [°F]", fontsize=fontsize)
    elif unite == 'K' :
      ax1.set_xlabel("Température [K]", fontsize=fontsize)
    twinax1.set_xlabel("Humidité [%]", fontsize=fontsize)
    ax1.xaxis.label.set_color('red')
    twinax1.xaxis.label.set_color('blue')
    twinax1.tick_params(axis='x',colors="blue")
    ax1.tick_params(axis='x',colors="red")
    # legend
    ln=l1+l2+l3+l4+l5+l6
    labs=[l.get_label() for l in ln]
    ax1.legend(ln,labs,loc=0)
  return fig, chemin_figure

def figure_vent_rs(date,unite):
  # Trace du profil rs de direction et force du vent 
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)
  # Nom du fichier
  fichier_figure = "graphe_RS_Vent_" + str(annee) + str(mois) + str(jour) +'.png'
  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)
  # Graphics
  FF,DD,FF_d,DD_d, alt,alt_d = [], [], [], [], [], [] # l'altitude, vent ff et direction 
  FF,DD,FF_d,DD_d, alt,alt_d = extract_data_rs_FF(date)
  # Conversion à la demande
  if unite == 'km/h' :
    FF = [x*3.6 for x in FF]
    FF_d = [x*3.6 for x in FF_d]
  elif unite =='kt' :
    FF = [x*3.6/1.8 for x in FF]
    FF_d = [x*3.6/1.8 for x in FF_d]
  elif unite =='m/s' :
    print("coucou")
  else:
    logging.info("Unité de vent inconnue !")
    exit(1)
  fontsize=10
  fig, ax2 = plt.subplots(1, 1, figsize=(16, 9))
  fig.suptitle("RS du "+date+" \n", fontsize=10)
  if not not(FF) :
    l1=ax2.plot(FF, alt, color='green', label='DD montée')
    l2=ax2.plot(FF_d, alt_d, "--",color='green', label='DD descente')
    twinax2 = ax2.twiny()
    l3=twinax2.plot(DD, alt, color='orange', label='FF montée')
    l4=twinax2.plot(DD_d, alt_d, "--",color='orange', label='FF descente')
    # axis title
    ax2.title.set_text("Vent")
    ax2.set_ylabel('Altitude [km]', fontsize=fontsize+4)
    if unite == 'km/h' :
      ax2.set_xlabel("Force du vent [km/h]", fontsize=fontsize)
    elif unite =='kt' :
      ax2.set_xlabel("Force du vent [kt]", fontsize=fontsize)
    elif unite =='m/s' :
      ax2.set_xlabel("Force du vent [m/s]", fontsize=fontsize)
    twinax2.set_xlabel("Direction du vent [°]", fontsize=fontsize)
    ax2.xaxis.label.set_color('green')
    twinax2.xaxis.label.set_color('orange')
    twinax2.tick_params(axis='x',colors="orange")
    ax2.tick_params(axis='x',colors="green")
    # legend
    ln=l1+l2+l3+l4
    labs=[l.get_label() for l in ln]
    ax2.legend(ln,labs,loc=0)
  return fig, chemin_figure

def figure_vitesse_rs(date,unite):
  # Trace du profil rs de vitesse ascentionnelle du ballon 
  logging.info("Le fichier png est enregistré sous : " + emplacement_figure)
  existence_repertoire(emplacement_figure)
  # Nom du fichier
  fichier_figure = "graphe_RS_Vitesse ascentionnelle_" + str(annee) + str(mois) + str(jour) +'.png'
  # Chemin complet
  chemin_figure = os.path.join(emplacement_figure, fichier_figure)
  logging.info("Nom du fichier png: " + chemin_figure)
  # Graphics
  As, As_d, alt,alt_d = [], [], [], [] # l'altitude, vent FF et direction 
  As, As_d, alt,alt_d = extract_data_rs_Vi(date)
  # Conversion à la demande
  if unite == 'km/h' :
    As = [x*3.6 for x in As]
    As_d = [x*3.6 for x in As_d]
  elif unite =='m/s' :
    print("coucou")
  elif unite =='kt' :
    As = [x*3.6/1.8 for x in As]
    As_d = [x*3.6/1.8 for x in As_d]
  else:
    logging.info("Unité de vent inconnue !")
    exit(1)
  fontsize=10
  fig, ax3 = plt.subplots(1, 1, figsize=(16, 9))
  fig.suptitle("RS du "+date+" \n", fontsize=10)
  if not not(As) :
    l1=ax3.plot(alt,As, color='black', label='Montée')
    l2=ax3.plot(alt_d,As_d, color='gray', label='Descente')
    # axis title
    ax3.title.set_text("Vitesse de la sonde")
    ax3.set_xlabel('Altitude [km]', fontsize=fontsize+4)
    if unite == 'km/h' :
      ax3.set_ylabel("Vitesse de la sonde [km/h]", fontsize=fontsize)
    elif unite =='kt' :
      ax3.set_ylabel("Vitesse de la sonde [kt]", fontsize=fontsize)
    elif unite =='m/s' :
      ax3.set_ylabel("Vitesse de la sonde [m/s]", fontsize=fontsize)
    Vamoy=np.mean(As)
    #l3=plt.axhline(5,color="red",label="5m/s")
    plt.axhline(Vamoy,color="yellow")
    if unite == 'km/h' :
      plt.text(-3.2,Vamoy,str(round(Vamoy,2))+"km/h",rotation=0)
    elif unite =='m/s' :
      plt.text(-3.2,Vamoy,str(round(Vamoy,2))+"m/s",rotation=0)
    elif unite =='kt' :
      plt.text(-3.2,Vamoy,str(round(Vamoy,2))+"kt",rotation=0)
    #plt.text(-2.8,Vamoy,str(round(Vamoy*1.8,2)),rotation=0)
    # legend
    ln=l1+l2
    labs=[l.get_label() for l in ln]
    ax3.legend(ln,labs,loc=0)
  return fig, chemin_figure

#############  PROGRAMME PRINCIPAL #############

if (__name__ == "__main__"):
  # Paramètres fixes
  jours = ["{:02d}".format(x) for x in range(1,32)]
  mois = ["{:02d}".format(x) for x in range(1,13)]
  annees = ["{:04d}".format(x) for x in range(1900,2100)]
  nbs_jours = ["{:02d}".format(x) for x in range(1,5)]
  decalage = {'UTC':0, 'DDU':10}
  logo = plt.imread("logo_MF.png")
  vide = "  mémoire vide - récupération requise !"

  ## Définition du fichier des paramètres
  sg.user_settings_filename(path='.',filename='visu_hors_mto.json')

  ## Dates / heures / décalage
  aujourdhui = datetime.datetime.today()
  date = aujourdhui.strftime("%d-%m-%Y")
  jour = sg.user_settings_get_entry('-jour-', date[0:2])
  mois = sg.user_settings_get_entry('-mois-', date[3:5])
  annee = sg.user_settings_get_entry('-annee-', date[6:10])
  nb_jours = sg.user_settings_get_entry('-nb_jours-', 3)

  ## Emplacements
  emplacement_figure = sg.user_settings_get_entry('-emplacement_figure-', os.path.join(os.path.dirname(__file__), 'figures'))
  emplacement_ceilo = sg.user_settings_get_entry('-emplacement_ceilo-', os.path.join("//groberg/Groberg/calva/CL31/donnees/Figs/"))
  emplacement_rs = sg.user_settings_get_entry('-emplacement_rs-', os.path.join("//mtoservice/Labos/LIDAR/COR/",annee))
  #emplacement_pluvio = sg.user_settings_get_entry('-emplacement_ceilo-', r"\\mtoservice\Labos\CALVA\Pluviometre\")
  
  ## Dates choisies pour les données minutes 
  dates_choisies = jour + "/" + mois + "/" + annee 

  ## unités 
  unite_vent = sg.user_settings_get_entry('-unite_vent-', 'kt')
  unite_vitesse = sg.user_settings_get_entry('-unite_vitesse-', 'm/s')
  unite_pression = sg.user_settings_get_entry('-unite_pression-', 'hPa')
  unite_temperature = sg.user_settings_get_entry('-unite_temperature-', '°C')
  chemin_figure = None

  
  # Interface graphique
  sg.theme('Dark Blue 3')

  # Frame 2 : 
  sg_date_temps = [ [ sg.Text('Date : ', size=12),
                            sg.Combo(jours, size=(3, 1), default_value=jour, enable_events=True ,key='-jour-', bind_return_key='-jour-'),
                            sg.Combo(mois, size=(3, 1), default_value=mois, enable_events=True ,key='-mois-', bind_return_key='-mois-'),
                            sg.Combo(annees, size=(5, 1), default_value=annee, enable_events=True ,key='-annee-', bind_return_key='-annee-') ] 
                        ]
  layout_date_temps = sg.Column( [ [ sg.Column(sg_date_temps, element_justification='c') ] ],
                                element_justification='c' )
  
  # Frame 2 : figure minute
  frame_layout_date_temps_decalage = [ [ sg.Column( [ [ layout_date_temps, ] ], element_justification='c' ) ] ]

  # Frame 3 : récupération des données ceilomètre 
  sg_donnees_ceilo = [ [ sg.Button('Ceilomètre ', enable_events=True ,key='-recuperation_donnees_ceilo-') ] 
                     ]
  sg_nb_jours_ceilo = [ [ sg.Combo(nbs_jours, size=(3, 1), default_value=nb_jours, enable_events=True ,key='-nb_jours-', bind_return_key='-nb_jours-') ] ]
  layout_nb_jours_ceilo = sg.Column( [ [ sg.Column(sg_nb_jours_ceilo, element_justification='c') ] ], element_justification='c' )
  
  #frame_donnees_ceilo = [ [sg.Column(sg_donnees_ceilo, element_justification='c') ] ]
  # Frame 4 : récupération des données pluviometre 
  sg_donnees_pluvio = [ [ sg.Button('Pluviomètre ', enable_events=True ,key='-recuperation_donnees_pluvio-')]
                      ]
  #frame_donnees_pluvio = [ [sg.Column(sg_donnees_pluvio, element_justification='c') ] ]
  # Frame 4 : récupération des données mrr 
  sg_donnees_mrr = [ [ sg.Button('MRR ', enable_events=True ,key='-recuperation_donnees_mrr-')]
                      ]
  #frame_donnees_mrr = [ [sg.Column(sg_donnees_mrr, element_justification='c') ] ]
  # Frame 5 : récupération des données de la camera Infoclimat 
  sg_donnees_camera = [ [ sg.Button('Caméra', enable_events=True ,key='-recuperation_donnees_camera-')]
                      ]
  #frame_donnees_camera = [ [sg.Column(sg_donnees_camera, element_justification='c') ] ]
  # Frame 6 : récupération des données maregraphe 
  sg_donnees_mare = [ [ sg.Button('Marégraphe ', enable_events=True ,key='-recuperation_donnees_maregraphe-')]
                    ]
  #frame_donnees_mare = [ [sg.Column(sg_donnees_mare, element_justification='c') ] ]
  frame_donnees_hors_mto = [ [sg.Column(sg_donnees_ceilo, element_justification='c'), 
                              sg.Column( [ [ layout_nb_jours_ceilo, ] ], element_justification='c' ),
                              sg.Column(sg_donnees_pluvio, element_justification='c'), 
                              sg.Column(sg_donnees_mrr, element_justification='c'), 
                              sg.Column(sg_donnees_camera, element_justification='c'), 
                              sg.Column(sg_donnees_mare, element_justification='c') ],
                           ]
  # Frame 7 : plot donnee RS quotidient 
  sg_emplacement_figure = [ [ sg.Text('Figures', size=9),
                              sg.In(size=(80,1), enable_events=True ,key='-emplacement_figure-', default_text=emplacement_figure),
                              sg.FolderBrowse("Répertoires") ],
                            [ sg.Button('Exporter la figure en PNG', enable_events=True ,key='-export_figure_rs-', expand_x=True)] 
                          ]
  sg_figure_RS = [ [ sg.Button('Vent', size=(20,1), enable_events=True ,key='-figure_vent-'),
                     sg.Radio('m/s', size=(7,1), group_id=2, default=(unite_vent=='m/s'), enable_events=True, key='-unite_vent_ms-'),
                     sg.Radio('km/h', size=(7,1), group_id=2, default=(unite_vent=='km/h'), enable_events=True, key='-unite_vent_kmh-'),
                     sg.Radio('kt', size=(7,1), group_id=2, default=(unite_vent=='kt'), enable_events=True, key='-unite_vent_kt-'),  ],
                   [ sg.Button('Vitesse Verticale', size=(20,1), enable_events=True ,key='-figure_vitesse-'),
                     sg.Radio('m/s', size=(7,1), group_id=3, default=(unite_vitesse=='m/s'), enable_events=True, key='-unite_vitesse_ms-'),
                     sg.Radio('km/h', size=(7,1), group_id=3, default=(unite_vitesse=='km/h'), enable_events=True, key='-unite_vitesse_kmh-'),
                     sg.Radio('kt', size=(7,1), group_id=3, default=(unite_vitesse=='kt'), enable_events=True, key='-unite_vitesse_kt-'),  ],
                   [ sg.Button('Temperature', size=(20,1), enable_events=True ,key='-figure_temperature-'),
                     sg.Radio('°C', size=(7,1), group_id=4, default=(unite_temperature=='°C'), enable_events=True, key='-unite_temperature_c-'),
                     sg.Radio('°F', size=(7,1), group_id=4, default=(unite_temperature=='°F'), enable_events=True, key='-unite_temperature_f-'),
                     sg.Radio('K', size=(7,1), group_id=4, default=(unite_temperature=='K'), enable_events=True, key='-unite_temperature_k-') ],
                   [ sg.Button('Série Température', size=(20,1), enable_events=True ,key='-figure_serie_tempe-') ],
                   [ sg.Button('Série Anomalie Temperature', size=(20,1), enable_events=True ,key='-figure_serie_anom_tempe-') ],
                   [ sg.Button('Série Vitesse verticale', size=(20,1), enable_events=True ,key='-figure_serie_vitesse-')],
                   ]
  frame_figure_RS = [ [ sg.Column(sg_figure_RS, element_justification='l', expand_x=True) ],
                      [ sg.Column(sg_emplacement_figure, element_justification='l', expand_x=True) ] ]
  
  ## Layout gauche
  layout_gauche = [ [ sg.Frame('Date', frame_layout_date_temps_decalage, expand_x=True) ],
                    [ sg.Frame('Mais où se trouve ...?', frame_donnees_hors_mto, expand_x=True) ],
                    [ sg.Frame('RS', frame_figure_RS, expand_x=True), sg.Image("logo_MF.png") ],
                    [ sg.Image("ddu.png", size=(800, 320)) ] ]

  ## Layout droite
  layout_droite = [ [sg.Frame('Figures', [[sg.Canvas(key='-CANVAS-', background_color='white', size = (16*get_dpi(), 10.25*get_dpi()))]]) ] ]

  ## Layout total
  layout = [ [ sg.Column(layout_gauche, element_justification='c', vertical_alignment='top'), sg.Column(layout_droite, element_justification='c', vertical_alignment='top') ] ]

  ## Création de la fenêtre
  window = sg.Window('Visualisation des données éparpillées', layout, resizable=True)

  # Gestion des événements
  while True:
    ## Récupération de l'événement et des valeurs
    event, values = window.read()
    if event != None:
      logging.info("Event: " + event)

    ## Quitter normalement
    if event in (sg.WIN_CLOSED, 'Exit'):
      break

    ## Date 
    if event == '-jour-':
      logging.info("Value: " + values[event])
      jour = values[event].zfill(2)
      window[event].update(jour)
      #modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-mois-':
      logging.info("Value: " + values[event])
      mois = values[event].zfill(2)
      window[event].update(mois)
      #modification_date(window)
      sg.user_settings_set_entry(event, values[event])
    if event == '-annee-':
      logging.info("Value: " + values[event])
      annee = values[event].zfill(4)
      window[event].update(annee)
      #modification_date(window)
      sg.user_settings_set_entry(event, values[event])

    ## Date / heure de fin des fichiers horaires
    if event == '-nb_jours-':
      logging.info("Value: " + values[event])
      nb_jours = values[event].zfill(1)
      window[event].update(nb_jours)
      #modification_date(window)
      sg.user_settings_set_entry(event, values[event])

    ## Récupération des données des fichiers 
    if event == '-recuperation_donnees_ceilo-':
      success = recuperation_fichiers_ceilo()
    if event == '-recuperation_donnees_pluvio-':
      success = recuperation_fichiers_pluvio()  
    if event == '-recuperation_donnees_mrr-':
      success = recuperation_fichiers_mrr()  
    if event == '-recuperation_donnees_maregraphe-':
      sg.popup_ok("Pas encore de figure pour le marégraphe du Lion", title="Erreur", keep_on_top=True)
    if event == '-recuperation_donnees_camera-':
      success = recuperation_fichiers_camera()  
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
    if event == '-figure_vent-':
      logging.info("figure_vent")
      if 'tkcanvas' in globals():
        tkcanvas.get_tk_widget().destroy()
      print(jour+'-'+mois+'-'+annee)
      fig, chemin_figure = figure_vent_rs(jour+'-'+mois+'-'+annee,unite_vent)
      tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)
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
      if 'tkcanvas' in globals():
        tkcanvas.get_tk_widget().destroy()
      fig, chemin_figure = figure_tempe_rs(jour+'-'+mois+'-'+annee,unite_temperature)
      tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)
    if event == '-unite_vitesse_ms-':
      unite_vitesse = 'm/s'
      logging.info("unite_vitesse:" + unite_vitesse)
    if event == '-unite_vitesse_kmh-':
      unite_vitesse = 'km/h'
      logging.info("unite_vitesse:" + unite_vitesse)
      sg.user_settings_set_entry('-unite_vitesse-', unite_vitesse)
    if event == '-unite_vitesse_kt-':
      unite_vitesse = 'kt'
      logging.info("unite_vitesse:" + unite_vitesse)
      sg.user_settings_set_entry('-unite_vitesse-', unite_vitesse)
    if event == '-figure_vitesse-':
      logging.info("figure_vitesse_verticale")
      if 'tkcanvas' in globals():
        tkcanvas.get_tk_widget().destroy()
      fig, chemin_figure = figure_vitesse_rs(jour+'-'+mois+'-'+annee,unite_vitesse)
      tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)
    if event == '-figure_serie_tempe-':
      logging.info("figure_serie_tempe")
      sg.popup_ok("Pas encore de figure RS", title="Erreur", keep_on_top=True)
        #if 'tkcanvas' in globals():
        #  tkcanvas.get_tk_widget().destroy()
        #  fig, ax, chemin_figure = figure_serie_tempe_rs(data)
        #  tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)
    if event == '-figure_serie_anom_tempe-':
      logging.info("figure_serie_anom_tempe")
      sg.popup_ok("Pas encore de figure RS", title="Erreur", keep_on_top=True)
        #if 'tkcanvas' in globals():
        #  tkcanvas.get_tk_widget().destroy()
        #  fig, ax, chemin_figure = figure_serie_anom_tempe_rs(data)
        #  tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)
    if event == '-figure_serie_vitesse-':
      logging.info("figure_serie_vitesse_verticale")
      sg.popup_ok("Pas encore de figure RS", title="Erreur", keep_on_top=True)
        #if 'tkcanvas' in globals():
        #  tkcanvas.get_tk_widget().destroy()
        #  fig, ax, chemin_figure = figure_serie_vitesse_rs(data)
        #  tkcanvas = affichage_figure(window['-CANVAS-'].TKCanvas, fig)
    # Export figure fichier minute
    if event == '-export_figure_rs-':
      if chemin_figure == None:
        sg.popup_ok("Impossible d'exporter une figure qui n'existe pas !", title="Erreur", keep_on_top=True)
      else:
        plt.savefig(chemin_figure, bbox_inches="tight")
        plt.close(fig)
        sg.popup_ok("Fichier " + chemin_figure + " exporté", title="Confirmation", keep_on_top=True)        
    

  # Fermeture de la fenêtre
  window.close()
