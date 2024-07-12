# -*- coding: utf-8 -*-
"""
Created on January 2024
@author : R. Honnert TA-74

Ce programme permet d'extraire des données d'un fichier horaire et de le mettre en forme pour le fournir aux personnes de la base qui les demandent.

Utilisation du programme : en ligne de commande dans un terminal
    exemple :  >python extract_data.py

Le programme :
    - pour les dates + heures DDU founies 
    - passe des dates DDU en dates UTC
    - détermine si le fichier "minute" existe
    - extrait les dates, puis des champs demandés
    - Fabrique un fichier de données ".ods" et dans un unique fichier trace les champs demandés. 

En entrée :
    un fichier de données minutes au format de sortie BDClim contenant les paramètres ddmmyyyyhhmm, T, DI, U, PSTA, FM1, FF, DD
    exemple : premières lignes dun fichier source conforme :
        ddmmyyyyhhmm;PSTA;T;U;TDET;DI;RG;DD;FF;FM1;DM1;DD;FF;FM1;DM1;
        260820210900;994,1;-14,4;35;-26,5;0;0;190;8,5;16,5;210;;;;;
        260820210901;994,3;-14,5;35;-26,6;0;0;190;9;14,9;200;;;;;

En sortie : 
    - Un fichier de données ".ods" et dans un unique fichier trace les champs demandés. 

extract_data : fabrique un fichier temporaire qui ne comprend que les dates et heures souhaitées 
plot_vent_minute_ponctuel : tracé du vent, de la rafale et de la direction 
plot_pression_minute_ponctuel :
plot_temperature_minute_ponctuel : tracé de la température réelle et ressentie 
plot_humidite_minute_ponctuel :


Paramètres unité/heure des graphes :
    fuseau horaires possibles (heure) : 'UTC' ou 'DDU'
    unités possibles pour le vent (unite) : 'm/s', 'km/h' ou 'kt'
    unités possibles pour la pression (unite): 'hPa' ou 'mmHg'
    unités possibles pour la température (unite) : '°C', '°F' ou 'K'
    unité possible pour l'humidité (non implémentable par l'utilisateur) : '%' non implémentable par l'utilisateur
"""

### chargement des librairies :
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment',None)
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import datetime
import locale
import calendar
import os
import sys
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import FreeSimpleGUI as sg
from tkinter import *

############# DEFINITION DES FONCTIONS#############
### Environnement de travail :
def existence_fichier(FICHIER):   
    # si le fichier n'exsite pas, on quite le script
    test = os.path.isfile(FICHIER)
    if not test :
        print(f"---> Le fichier suivant n'a pas été trouvé : {FICHIER}")
        exit(0)

def existence_repertoire_graphe(REPERTOIRE) :    
    # si le répertoire n'existe pas, il est créé
    test = os.path.isdir(REPERTOIRE)
    if not test :
        print(f"---> le réperoire suivant n'existe pas, création du répertoire : {REPERTOIRE}")
        os.mkdir(REPERTOIRE)

def get_dpi():
    screen = Tk()
    current_dpi = screen.winfo_fpixels('1i')
    screen.destroy()
    return current_dpi

### Extraction et formattage des données :      
def creer_donnees_minutes_ponctuel(FICHIER,D1,D2) :
    # construit une dataframe au pas de temps minutes à partir des données minutes.
    # les données sources doivent à minima débuter à J 00:00UTC et se terminer à J 23:59UTC
    # les données sources sont au pas de temps minute
    # déclarations :
    
    # test et lecture des données horaires :
    data_minutes = pd.read_csv(FICHIER, sep=';', decimal=",", engine='python')

    # correction du zero manquant devant certaines date :
    # TODO(Rachel) : toujours le cas ? je n'ai pas l'impression dans le fichier, mais peut-être dans les précédent ?
    TMP=[]
    for x in range (0,len(data_minutes['ddmmyyyyhhmm'])):
        if len(str(data_minutes['ddmmyyyyhhmm'][x])) == 11 :
            TMP.append('0'+str(data_minutes['ddmmyyyyhhmm'][x]))
        else :
            TMP.append(str(data_minutes['ddmmyyyyhhmm'][x]))
    data_minutes['ddmmyyyyhhmm']=TMP

    # sélection des dates et heures :
    iD1 = (data_minutes.ddmmyyyyhhmm == D1).idxmax()
    iD2 = (data_minutes.ddmmyyyyhhmm == D2).idxmax()
    if data_minutes['ddmmyyyyhhmm'][iD1] != D1:
      # pas de date pertinente dans ce fichier, ce n'est pas normal !
      print("pas de date pertinente dans ce fichier, ce n'est pas normal !")
      exit()
    if data_minutes['ddmmyyyyhhmm'][iD2] != D2:
      # pas de date pertinente dans ce fichier, ce n'est pas normal !
      print("pas de date pertinente dans ce fichier, ce n'est pas normal !")
      exit()
    data_minutes = data_minutes.iloc[iD1:iD2+1,:]

    # formatage des dates et heures :
    data_minutes['ddmmyyyyhhmm']=pd.to_datetime(data_minutes['ddmmyyyyhhmm'][:],format='%d%m%Y%H%M',errors='coerce')
    data_minutes['date']=data_minutes['ddmmyyyyhhmm']

    # formatage des données numériques :
    for param in data_minutes.columns[2:14]:
        data_minutes[param] = pd.to_numeric(data_minutes[param])
    
    # création d'un index :
    data_minutes.set_index(['date'], inplace=True)
    data_minutes.sort_index(ascending=True, inplace=True)
 
    # enregistrement de la dataframe
    index=np.where(data_minutes['ddmmyyyyhhmm'].notnull())[0]
    data_minutes_final=pd.DataFrame({
        'DATE':data_minutes['ddmmyyyyhhmm'].iloc[index], # date
           'T':data_minutes['T'].iloc[index],            # température
          'DI':data_minutes['DI'].iloc[index],           # durée d'insolation
          #'RG':data_minutes['RG'].iloc[index],           # rayonnement global
         'FXI':data_minutes['FM1'].iloc[index],          # vitesse maximale sur 10min          
          'FF':data_minutes['FF'].iloc[index],           # vitesse moyenne sur 10min
          'DD':data_minutes['DD'].iloc[index],           # direction moyenne sur 10min
           'U':data_minutes['U'].iloc[index],            # humidité relative
           'P':data_minutes['PSTA'].iloc[index]          # pression au niveau de la station 
           }, columns=['DATE','T','DI','RG','FXI','FF','DD','U','P'])
    # fin de la fonction :
    return(data_minutes_final)

### Ecrire un fichier csv :
def write_data(data,P=False,T=False,Tres=False,FMOY=False,DMOY=False,FINS=False,DINS=False,HU=False,DI=False,RG=False,VIS=False) :
    # ecriture d'un fichier csv
    print("-- Ecriture d'un fichier CSV ")
    FILEOUT="DATA_METEO_"+str(annee_debut)+str(mois_debut)+str(jour_debut)+str(heure_debut)+str(minute_debut)+'-'+str(annee_fin)+str(mois_fin)+str(jour_fin)+str(heure_fin)+str(minute_fin)+'.csv'
    print(f"--> Le fichier csv est enregistré sous : {emplacement_csv}")
    print("----> OK ")

    # le programme écrit dans un csv les données qui sont demandées 
    # selection des données 
    list_data=[]
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
    newdata=data[list_data]

    # ecrire newdata dans un fichier csv FILEOUT
    newdata.to_csv(os.path.join(emplacement_csv, FILEOUT), sep=";")

def recuperation_donnees():
    print('-> Début du programme : tracés de données minutes sur période courte')
    ###############################################################################"
    # CODE
    ###############################################################################"
    # Calcul du vecteur temps :
    date_locale_deb=datetime.datetime(int(annee_debut),int(mois_debut),int(jour_debut),int(heure_debut),int(minute_debut))
    date_locale_fin=datetime.datetime(int(annee_fin),int(mois_fin),int(jour_fin),int(heure_fin),int(minute_fin))

    # Date au format UTC : 
    date_deb=date_locale_deb-datetime.timedelta(hours=decalage[fuseau])
    date_fin=date_locale_fin-datetime.timedelta(hours=decalage[fuseau])

    # Formatage des données 
    D1=date_deb.strftime("%d%m%Y%H%M")
    D2=date_fin.strftime("%d%m%Y%H%M")
    d1=date_deb.strftime("%Y%m")
    d2=date_fin.strftime("%Y%m")
    today=datetime.datetime.today()

    print("Date de début: " + D1)
    print("Date de fin:   " + D2)
    # Boucle sur les mois demandés
    for dd in range(int(d1), int(d2)+1):
      # choix du fichier
      if str(dd)==today.strftime("%Y%m"):
          FILENAME_MINUTE = "DON_Minute_UTC_moisencours.csv"
      else :
          FILENAME_MINUTE = "DON_Minute_UTC_"+str(dd)+".txt"

      # on teste si le fichier est bien là dans son répertoire
      FICHIER_MINUTE = os.path.join(emplacement_minute, FILENAME_MINUTE)
      print("-- vérifications de l'existence de : "+FICHIER_MINUTE)
      existence_fichier(FICHIER_MINUTE)
      print("----> OK ")

      # on trouve la date de début et la date de fin du fichier FICHIER_MINUTE
      DEB_FIC="01"+str(dd)[4:6]+str(dd)[0:4]+"0000"
      res=calendar.monthrange(int(str(dd)[0:4]), int(str(dd)[4:6]))
      FIN_FIC=str(res[1])+str(dd)[4:6]+str(dd)[0:4]+"2359"
      if str(dd) == d1:
        # Premier fichier
        DEB_FIC=D1
      elif str(dd) == d2:
        # Dernier fichier
        FIN_FIC=D2

      print("-- lecture et nettoyage des données de : "+FICHIER_MINUTE)
      print("--- date de début : "+DEB_FIC)
      print("--- date de fin :   "+FIN_FIC)
      if str(dd) == d1:
        # Premier fichier
        data = creer_donnees_minutes_ponctuel(FICHIER_MINUTE,DEB_FIC,FIN_FIC)
        print("--- nombre de ligne pour ce fichier :   " + str(data.shape[0]))
      else:
        # Concaténation avec la base data
        dataTmp = creer_donnees_minutes_ponctuel(FICHIER_MINUTE,DEB_FIC,FIN_FIC)
        print("--- nombre de ligne pour ce fichier : " + str(dataTmp.shape[0]))
        data = pd.concat([data, dataTmp], ignore_index=True)
        print("--- nombre de ligne pour ce fichier :   " + str(dataTmp.shape[0]))
      print("--- taille totale de la base de données : " + str(data.shape[0]))
      print("----> OK ")

    return data

### Graphes :
def plot_pression_minute_ponctuel(data, unite):
     # trace la pression atmosphérique à la station sur la période données dans le fichier source, au pas de temps minute
    print(f"---> pression minutes en {str(unite)}, heure {str(fuseau)}")
    date_graphe=f"{min(data['DATE']).strftime('%d')}-{min(data['DATE']).strftime('%m')}-{min(data['DATE']).strftime('%Y')}"
    GRAPHE_NAME=f"graphe_PressionMinute_{date_graphe}.png"
    existence_repertoire_graphe(emplacement_figures)
    GRAPHE= os.path.join(emplacement_figures, GRAPHE_NAME)
    # paramètres du graphe :
    ratio=0.002

    # calcul du vecteur temps :
    data_date=data['DATE']+datetime.timedelta(hours=decalage[fuseau])
              
    # conversion à la demande
    if unite == 'mmHg' :
        data_P=data['P']*0.75
        YMAX=765
        YMIN=675
    else :
        unite='hPa'
        data_P=data['P']
        YMIN=930
        YMAX=1020
        
        # calculs des bornes de l'axe des ordonnées :
    if max(data_P)+abs(ratio*max(data_P)) > YMAX :
        BMAX=YMAX
    else :
        BMAX=max(data_P)+ratio*abs(max(data_P))
        
    if min(data_P)-ratio*min(data_P) <YMIN :
        BMIN=YMIN
    else :
        BMIN=min(data_P)-ratio*abs(min(data_P))
        
    # tracé du graphe :
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.plot(np.array(data_date),np.array(data_P), linewidth=1, color='darkblue', label='P')
    ax.axhline(0, color='grey', linestyle='--')
    #ax.grid(b=True, which='both', axis='both', color='lightgrey', zorder=1)
    ax.set_xlabel(f"date et heure {str(fuseau)}")
    ax.set_ylabel(f"Pression atmosphérique [{str(unite)}]")
    ax.autoscale(axis='x', tight='true')
    fig.autofmt_xdate()
    ax.set_title(f"Pression atmosphérique - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
    _, ylim = ax.get_ylim()
    ax.set_ylim(bottom=BMIN, top=BMAX)
    #
    l=4
    axins = inset_axes(ax, width=0.984*l, height=0.157*l, borderpad=0, loc="upper right")
    axins.imshow(logo, alpha=0.5)
    axins.axis('off')
    print('-----> OK')
    return fig, ax, GRAPHE

def plot_vent_minute_ponctuel(data,unite):
    # trace la force et direction du vent moyen et force des rafales à la station sur la période données dans le fichier source, au pas de temps minute
    print(f"---> vent minutes en {str(unite)}, heure {str(fuseau)}")
    date_graphe=f"{min(data['DATE']).strftime('%d')}-{min(data['DATE']).strftime('%m')}-{min(data['DATE']).strftime('%Y')}"
    GRAPHE_NAME=f"graphe_VentMinute_{date_graphe}.png"
    existence_repertoire_graphe(emplacement_figures)
    GRAPHE= os.path.join(emplacement_figures, GRAPHE_NAME)
    # paramètres du graphe :
    ratio=0.2
    
    # calcul du vecteur temps :
    data_date=data['DATE']+datetime.timedelta(hours=decalage[fuseau])
                
    # conversion à la demande
    if unite == 'km/h' :
        data_FF=data['FF']*3.6
        data_FXI=data['FXI']*3.6
        YMIN=0
        YMAX=250
        seuil=90
    else :
        if unite =='kt' :
            data_FF=data['FF']*3.6/1.8
            data_FXI=data['FXI']*3.6/1.8
            YMIN=0
            YMAX=140
            seuil=50
        else :
            unite='m/s'
            data_FF=data['FF']
            data_FXI=data['FXI']
            YMIN=0
            YMAX=70
            seuil=25
                
    # calculs des bornes de l'axe des ordonnées :
    if max(data_FXI)+abs(ratio*max(data_FXI)) > YMAX :
        BMAX=YMAX
    else :
        BMAX=max(data_FXI)+ratio*abs(max(data_FXI))
        
    if min(data_FXI)-ratio*min(data_FXI) <YMIN :
        BMIN=YMIN
    else :
        BMIN=min(data_FXI)-ratio*abs(min(data_FXI))
    # tracé du graphe :
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.plot(np.array(data_date),np.array(data_FXI), linewidth=1, color='brown', label='rafales')
    ax.plot(np.array(data_date),np.array(data_FF), linewidth=1, color='darkblue', label='vent moyen')
    ax.axhline(seuil, color='red', linewidth=1, linestyle='--',label='seuil tempête')
    ax.axhline(0, color='grey', linestyle='--')
    #ax.grid(b=True, which='major', axis='both', color='lightgrey', zorder=1)
    #
    ax2=ax.twinx()
    ax2.set_ylabel('direction du vent [°]', color='black')
    ax2.plot(np.array(data_date), np.array(data['DD']), color='forestgreen', label='direction', linestyle='dashed', linewidth=0.7)
    ax2.tick_params(axis='y', labelcolor='forestgreen')
    #
    ax.set_xlabel(f"date et heure  {str(fuseau)}")
    ax.set_ylabel(f"Vent moyen et rafales [{str(unite)}]")
    ax.autoscale(axis='x', tight='true')
    fig.autofmt_xdate()
    ax.set_title(f"Vent moyen et rafales - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
    _, ylim = ax.get_ylim()
    ax.set_ylim(bottom=BMIN, top=BMAX)
    #
    #handles, labels = ax.get_legend_handles_labels()
    #green_line = mlines.Line2D([], [], color='forestgreen', linestyle='dashed', linewidth=0.7)
    #handles.append(green_line)
    #labels.append("direction")
    #ax.legend([handles[x] for x in [0, 1, 2, 3]], [labels[x] for x in [0, 1, 2, 3]], loc="upper left", ncol=len(handles))
    #
    l=4
    axins = inset_axes(ax, width=0.984 * l, height=0.157 * l, borderpad=0, loc="upper right")
    axins.imshow(logo, alpha=0.5)
    axins.axis('off')
    print('-----> OK')
    return fig, ax, GRAPHE

def plot_temperature_minute_ponctuel(data,unite):
    # trace la température sous abri et la température ressentie sur la période données dans le fichier source, au pas de temps minute
    print(f"---> températures minutes en {str(unite)}, heure {str(fuseau)}")
    #paramètres du graphe :
    date_graphe=f"{min(data['DATE']).strftime('%d')}-{min(data['DATE']).strftime('%m')}-{min(data['DATE']).strftime('%Y')}"
    GRAPHE_NAME=f"graphe_TemperatureMinute_{date_graphe}.png"
    existence_repertoire_graphe(emplacement_figures)
    GRAPHE= os.path.join(emplacement_figures, GRAPHE_NAME)
    
    # calcul du vecteur temps :
    data_date=data['DATE']+datetime.timedelta(hours=decalage[fuseau])
    
    # calcul de la température ressentie :
    data_Tres=13.12+0.6215*(data['T'])+(0.3965*data['T']-11.37)*(data['FF']*3.6)**0.16
              
    # conversion à la demande
    if unite == '°F' :
        data_T=data['T']*1.8+32
        data_Tres=data_Tres*1.8+32
        YMAX=10*1.8+32
        YMIN=-45*1.8+32
        ratio=0.2
    else :
        if unite == 'K' :
            data_T=data['T']+273.15
            data_Tres=data_Tres+273.15
            YMAX=10+273.15
            YMIN=-45+273.5
            ratio=0.002
        else:
            unite='°C'
            data_T=data['T']
            YMIN=-45
            YMAX=10
            ratio=0.2
                
        # calculs des bornes de l'axe des ordonnées :
    if max(data_T)+abs(ratio*max(data_T)) > YMAX :
        BMAX=YMAX
    else :
        BMAX=max(data_T)+ratio*abs(max(data_T))
        
    if min(data_Tres)-ratio*min(data_Tres) <YMIN :
        BMIN=YMIN
    else :
        BMIN=min(data_Tres)-ratio*abs(min(data_Tres))
        
    # tracé du graphe :
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.plot(np.array(data_date),np.array(data_T), linewidth=1, color='blue', label='T sous abri')
    ax.plot(np.array(data_date),np.array(data_Tres), linewidth=1, color='black', label='T ressentie')
    ax.axhline(0, color='grey', linestyle='--')
    #ax.grid(b=True, which='both', axis='both', color='lightgrey', zorder=1)
    ax.set_xlabel(f"date et heure {str(fuseau)}")
    ax.set_ylabel(f"Températures [{str(unite)}]")
    ax.autoscale(axis='x', tight='true')
    fig.autofmt_xdate()
    ax.set_title(f"Températures - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
    _, ylim = ax.get_ylim()
    ax.set_ylim(bottom=BMIN, top=BMAX)
    #
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([handles[x] for x in [0, 1]], [labels[x] for x in [0, 1]], loc="upper left", ncol=len(handles))
    #
    l=4
    axins = inset_axes(ax, width=0.984 * l, height=0.157 * l, borderpad=0, loc="upper right")
    axins.imshow(logo, alpha=0.5)
    axins.axis('off')
    print('-----> OK')
    return fig, ax, GRAPHE

def plot_humidite_minute_ponctuel(data):
    # trace l'humidité relative à la station sur la période données dans le fichier source, au pas de temps minute
    print(f"---> humidité minutes en %, heure {str(fuseau)}")
    date_graphe=f"{min(data['DATE']).strftime('%d')}-{min(data['DATE']).strftime('%m')}-{min(data['DATE']).strftime('%Y')}"
    GRAPHE_NAME=f"graphe_HumiditeMinute_{date_graphe}.png"
    existence_repertoire_graphe(emplacement_figures)
    GRAPHE= os.path.join(emplacement_figures, GRAPHE_NAME)

    # paramètres du graphe :
    YMAX=100
    YMIN=0
    unite='%'
    ratio=0.1
    data_U=data['U']
    
    # calcul du vecteur temps :
    data_date=data['DATE']+datetime.timedelta(hours=decalage[fuseau])
               
    # calculs des bornes de l'axe des ordonnées :
    if max(data['U'])+abs(ratio*max(data['U'])) > YMAX :
        BMAX=YMAX
    else :
        BMAX=max(data['U'])+ratio*abs(max(data['U']))
        
    if min(data['U'])-ratio*min(data['U']) <YMIN :
        BMIN=YMIN
    else :
        BMIN=min(data['U'])-ratio*abs(min(data['U']))
        
    # tracé du graphe :
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.plot(np.array(data_date),np.array(data_U), linewidth=1, color='darkblue', label='P')
    ax.axhline(0, color='grey', linestyle='--')
    #ax.grid(b=True, which='both', axis='both', color='lightgrey', zorder=1)
    ax.set_xlabel(f"date et heure {str(fuseau)}")
    ax.set_ylabel(f"Humidité relative [{str(unite)}]")
    ax.autoscale(axis='x', tight='true')
    fig.autofmt_xdate()
    ax.set_title(f"Humidité relative - données minutes du {min(data_date).strftime('%d')} {min(data_date).strftime('%h')} {min(data_date).strftime('%Y')} à {min(data_date).strftime('%H:%M')} au {max(data_date).strftime('%d')} {max(data_date).strftime('%h')} {max(data_date).strftime('%Y')} à {max(data_date).strftime('%H:%M')}, heure {str(fuseau)}", fontsize=15)
    _, ylim = ax.get_ylim()
    ax.set_ylim(bottom=BMIN, top=BMAX)
    #
    l=4
    axins = inset_axes(ax, width=0.984 * l, height=0.157 * l, borderpad=0, loc="upper right")
    axins.imshow(logo, alpha=0.5)
    axins.axis('off')
    print('-----> OK')
    return fig, ax, GRAPHE

def draw_figure(canvas, figure):
    tkcanvas = FigureCanvasTkAgg(figure, canvas)
    tkcanvas.draw()
    tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
    return tkcanvas

#############  PROGRAMME PRINCIPAL : #############
    #%% MAIN
if (__name__ == "__main__"):
    # Valeurs initiales (devraient être lues dans un fichier de paramètre si celui-ci existe)

    ###############################################################################"
    # Répertoires locaux :
    PATH_TO_LOGO = "./"
    # déclaration des variables d'environnement :
    FILENAME_LOGO = "logo_MF.png"

    # fabrication des graphiques
    # vérifications des autres fichiers d'environnement
    FICHIER_LOGO =  os.path.join(PATH_TO_LOGO, FILENAME_LOGO)
    print("-- vérifications de l'environnement de travail : ")
    existence_fichier(FICHIER_LOGO)
    
    # paramètres des graphes :
    logo=plt.imread(FICHIER_LOGO)

    ## Emplacements
    emplacement_minute = os.path.join(os.path.dirname(__file__), 'minute')
    emplacement_figures = os.path.join(os.path.dirname(__file__), 'figures')
    emplacement_csv = os.path.join(os.path.dirname(__file__), 'csv')

    ## Dates / heures / décalage
    today = datetime.datetime.today()
    date_debut = today.strftime("%d-%m-%Y")
    jour_debut = date_debut[0:2]
    mois_debut = date_debut[3:5]
    annee_debut = date_debut[6:10]
    temps_debut = today.strftime("%H:%M")
    heure_debut = temps_debut[0:2]
    minute_debut = temps_debut[3:5]
    date_fin = today.strftime("%d-%m-%Y")
    jour_fin = date_fin[0:2]
    mois_fin = date_fin[3:5]
    annee_fin = date_fin[6:10]
    temps_fin = today.strftime("%H:%M")
    heure_fin = temps_fin[0:2]
    minute_fin = temps_fin[3:5]
    fuseau = 'DDU hiver'

    ## Hack TODO: à supprimer
    mois_debut = "05"
    mois_fin = "06"

    ## Données en mémoire
    donnees_en_memoire = "  mémoire vide !  "
    couleur_donnees = 'red'

    ## Export CSV
    plot_p = True
    plot_t = True
    plot_u = True
    plot_ff = True
    plot_fi = True
    plot_dd = True
    plot_vis = False

    ## Unités
    unite_vent = 'kt'
    unite_pression = 'hPa'
    unite_temperature = '°C'

    # Paramètres fixes
    jours = ["{:02d}".format(x) for x in range(1,32)]
    mois = ["{:02d}".format(x) for x in range(1,13)]
    annees = ["{:04d}".format(x) for x in range(1900,2100)]
    heures = ["{:02d}".format(x) for x in range(1,25)]
    minutes = ["{:02d}".format(x) for x in range(1,61)]
    decalage = {'UTC':0, 'DDU hiver':10, 'DDU été':11}

    # Frame 1 : emplacements
    sg_emplacement_minute = [ [ sg.Text('Fichiers minute', size=13),
                                sg.In(size=(80,1), enable_events=True ,key='-emplacement_minute-', default_text=emplacement_minute),
                                sg.FolderBrowse() ] ]

    sg_emplacement_csv = [ [sg.Text('Fichiers csv', size=13),
                            sg.In(size=(80,1), enable_events=True ,key='-emplacement_csv-', default_text=emplacement_csv),
                            sg.FolderBrowse() ] ]

    sg_emplacement_figure = [ [ sg.Text('Figures', size=13),
                                sg.In(size=(80,1), enable_events=True ,key='-emplacement_figure-', default_text=emplacement_figures),
                                sg.FolderBrowse() ] ]

    frame_layout_emplacement = [ [ sg.Column(sg_emplacement_minute, element_justification='c') ],
                                 [ sg.Column(sg_emplacement_csv, element_justification='c') ],
                                 [ sg.Column(sg_emplacement_figure, element_justification='c') ] ]

    # Frame 2.1 : dates / heures
    sg_date_temps_debut = [ [ sg.Text('Date de début: ', size=12),
                              sg.Combo(jours, size=(3, 1), default_value=jour_debut, enable_events=True ,key='-jour_debut-', bind_return_key='-jour_debut-'),
                              sg.Combo(mois, size=(3, 1), default_value=mois_debut, enable_events=True ,key='-mois_debut-', bind_return_key='-mois_debut-'),
                              sg.Combo(annees, size=(5, 1), default_value=annee_debut, enable_events=True ,key='-annee_debut-', bind_return_key='-annee_debut-'),
                              sg.Button('Cal', key='-selection_date_debut-'),
                              sg.Text('Heure de début: ', size=13),
                              sg.Combo(heures, size=(3, 1), default_value=heure_debut, enable_events=True ,key='-heure_debut-', bind_return_key='-heure_debut-'),
                              sg.Combo(minutes, size=(3, 1), default_value=minute_debut, enable_events=True ,key='-minute_debut-', bind_return_key='-minute_debut-') ] ]

    sg_date_temps_fin = [ [ sg.Text('Date de fin: ', size=12),
                            sg.Combo(jours, size=(3, 1), default_value=jour_fin, enable_events=True ,key='-jour_fin-', bind_return_key='-jour_fin-'),
                            sg.Combo(mois, size=(3, 1), default_value=mois_fin, enable_events=True ,key='-mois_fin-', bind_return_key='-mois_fin-'),
                            sg.Combo(annees, size=(5, 1), default_value=annee_fin, enable_events=True ,key='-annee_fin-', bind_return_key='-annee_fin-'),
                            sg.Button('Cal', key='-selection_date_fin-'),
                            sg.Text('Heure de fin: ', size=13),
                            sg.Combo(heures, size=(3, 1), default_value=heure_fin, enable_events=True ,key='-heure_fin-', bind_return_key='-heure_fin-'),
                            sg.Combo(minutes, size=(3, 1), default_value=minute_fin, enable_events=True ,key='-minute_fin-', bind_return_key='-minute_fin-') ] ]
 

    layout_date_temps = sg.Column( [ [ sg.Column(sg_date_temps_debut, element_justification='c') ],
                                     [ sg.Column(sg_date_temps_fin, element_justification='c') ] ],
                                   element_justification='c' )

    # Frame 2.2 : décalage horaire
    sg_decalage = sg.Column( [ [ sg.Radio('UTC (+0)', size=(15,1), group_id=1, default=(fuseau=='UTC'), enable_events=True, key='-decalage_utc-') ],
                               [ sg.Radio('DDU hiver (+10)', size=(15,1), group_id=1, default=(fuseau=='DDU hiver'), enable_events=True, key='-decalage_ddu_hiver-') ],
                               [ sg.Radio('DDU été (+11)', size=(15,1), group_id=1, default=(fuseau=='DDU été'), enable_events=True, key='-decalage_ddu_ete-') ]  ],
                             element_justification='c') 
   
    # Frame 2 : date / heure / décalage horaire
    frame_layout_date_temps_decalage = [ [ sg.Column( [ [ layout_date_temps, sg_decalage] ], element_justification='c' ) ] ]

    # Frame 3 : récupération des données
    sg_donnees = [ [ sg.Button('Récupérer', enable_events=True ,key='-recuperation_donnees-'),
                     sg.Text('Données actuellement chargées:', justification='right'),
                     sg.Text(donnees_en_memoire, background_color=couleur_donnees, text_color='white', key='-donnees_en_memoire-', justification='left') ] ]

    frame_donnees = [ [sg.Column(sg_donnees, element_justification='c') ] ]

    # Frame 4 : plot et export CSV
    sg_plot = [ [ sg.Button('Vent', size=(12,1), enable_events=True ,key='-plot_vent_minute_ponctuel-'),
                  sg.Radio('m/s', size=(7,1), group_id=2, default=(unite_vent=='m/s'), enable_events=True, key='-unite_vent_ms-'),
                  sg.Radio('km/h', size=(7,1), group_id=2, default=(unite_vent=='km/h'), enable_events=True, key='-unite_vent_kmh-'),
                  sg.Radio('kt', size=(7,1), group_id=2, default=(unite_vent=='kt'), enable_events=True, key='-unite_vent_kt-'),  ],
                [ sg.Button('Pression', size=(12,1), enable_events=True ,key='-plot_pression_minute_ponctuel-'),
                  sg.Radio('mmHg', size=(7,1), group_id=3, default=(unite_pression=='mmHg'), enable_events=True, key='-unite_pression_mmhg-'),
                  sg.Radio('hPa', size=(7,1), group_id=3, default=(unite_pression=='hPa'), enable_events=True, key='-unite_pression_hpa-')  ],
                [ sg.Button('Temperature', size=(12,1), enable_events=True ,key='-plot_temperature_minute_ponctuel-'),
                  sg.Radio('°C', size=(7,1), group_id=4, default=(unite_temperature=='°C'), enable_events=True, key='-unite_temperature_c-'),
                  sg.Radio('°F', size=(7,1), group_id=4, default=(unite_temperature=='°F'), enable_events=True, key='-unite_temperature_f-'),
                  sg.Radio('K', size=(7,1), group_id=4, default=(unite_temperature=='K'), enable_events=True, key='-unite_temperature_k-'),  ],
                [ sg.Button('Humidité', size=(12,1), enable_events=True ,key='-plot_humidite_minute_ponctuel-') ],
                [ sg.Button('Exporter le plot en PNG', enable_events=True ,key='-export_plot-', expand_x=True) ] ]

    sg_export_csv = [ [ sg.Checkbox('P', default=plot_p, enable_events=True, key='-plot_p-'),
                        sg.Checkbox('T', default=plot_t, enable_events=True, key='-plot_t-'),
                        sg.Checkbox('U', default=plot_u, enable_events=True, key='-plot_u-'),
                        sg.Checkbox('FF', default=plot_ff, enable_events=True, key='-plot_ff-'),
                        sg.Checkbox('FI', default=plot_fi, enable_events=True, key='-plot_fi-'),
                        sg.Checkbox('DD', default=plot_dd, enable_events=True, key='-plot_dd-'),
                        sg.Checkbox('VIS', default=plot_vis, enable_events=True, key='-plot_vis-') ],
                      [ sg.Button('Exporter au format CSV', enable_events=True ,key='-export_csv-', expand_x=True) ] ]

    frame_plot = [ [ sg.Column(sg_plot, element_justification='l', expand_x=True) ],
                   [ sg.Column(sg_export_csv, element_justification='l', expand_x=True) ] ]

    # Layout gauche
    layout_gauche = [ [ sg.Frame('Emplacements', frame_layout_emplacement, expand_x=True) ],
                      [ sg.Frame('Dates / heures / décalage horaire ', frame_layout_date_temps_decalage, expand_x=True) ],
                      [ sg.Frame('Récupération des données', frame_donnees, expand_x=True) ],
                      [ sg.Frame('Plot / export CSV', frame_plot, expand_x=True), sg.Image("logo_MF.png") ],
                      [ sg.Image("ddu.png") ] ]

    # Layout droite
    layout_droite = [ [sg.Frame('Figure', [[sg.Canvas(key='-CANVAS-', background_color='white', size = (16*get_dpi(), 9.37*get_dpi()))]]) ] ]

    # Layout total
    layout = [ [ sg.Column(layout_gauche, element_justification='c', vertical_alignment='top'), sg.Column(layout_droite, element_justification='c', vertical_alignment='top') ] ]

    # Fenêtre
    window = sg.Window('MINUTE - DDU', layout, resizable=True)    

    # Gestion des événements
    while True:
      event, values = window.read()
      if event in (sg.WIN_CLOSED, 'Exit'):
        break
      if event == '-emplacement_minute-':
        emplacement_minute = values['-emplacement_minute-']  
        print("emplacement_minute: " + emplacement_minute)
      if event == '-emplacement_figure-':
        emplacement_figure = values['-emplacement_figure-']  
        print("emplacement_figure: " + emplacement_figure)
      if event == '-emplacement_csv-':
        emplacement_csv = values['-emplacement_csv-']  
        print("emplacement_csv: " + emplacement_csv)

      if event == '-jour_debut-':
        jour_debut = values['-jour_debut-'].zfill(2)
        window['-jour_debut-'].update(jour_debut)
        print("jour_debut: " + jour_debut)
      if event == '-mois_debut-':
        mois_debut = values['-mois_debut-'].zfill(2)
        window['-mois_debut-'].update(mois_debut)
        print("mois_debut: " + mois_debut)
      if event == '-annee_debut-':
        annee_debut = values['-annee_debut-'].zfill(4)
        window['-annee_debut-'].update(annee_debut)
        print("annee_debut: " + annee_debut)
      if event == '-heure_debut-':
        heure_debut = values['-heure_debut-'].zfill(2)
        window['-heure_debut-'].update(heure_debut)
        print("heure_debut: " + heure_debut)
      if event == '-minute_debut-':
        minute_debut = values['-minute_debut-'].zfill(2)
        window['-minute_debut-'].update(minute_debut)
        print("minute_debut: " + minute_debut)
      if event == '-selection_date_debut-':
        date_debut_tuple = sg.popup_get_date(start_mon=int(mois_debut), start_day=int(jour_debut), start_year=int(annee_debut), begin_at_sunday_plus=1, title="Date de début")
        jour_debut = str(date_debut_tuple[1]).zfill(2)
        mois_debut = str(date_debut_tuple[0]).zfill(2)
        annee_debut = str(date_debut_tuple[2]).zfill(2)
        window['-jour_debut-'].update(jour_debut)
        window['-mois_debut-'].update(mois_debut)
        window['-annee_debut-'].update(annee_debut)

      if event == '-jour_fin-':
        jour_fin = values['-jour_fin-'].zfill(2)
        window['-jour_fin-'].update(jour_fin)
        print("jour_fin: " + jour_fin)
      if event == '-mois_fin-':
        mois_fin = values['-mois_fin-'].zfill(2)
        window['-mois_fin-'].update(mois_fin)
        print("mois_fin: " + mois_fin)
      if event == '-annee_fin-':
        annee_fin = values['-annee_fin-'].zfill(4)
        window['-annee_fin-'].update(annee_fin)
        print("annee_fin: " + annee_fin)
      if event == '-heure_fin-':
        heure_fin = values['-heure_fin-'].zfill(2)
        window['-heure_fin-'].update(heure_fin)
        print("heure_fin: " + heure_fin)
      if event == '-minute_fin-':
        minute_fin = values['-minute_fin-'].zfill(2)
        window['-minute_fin-'].update(minute_fin)
        print("minute_fin: " + minute_fin)
      if event == '-selection_date_fin-':
        date_fin_tuple = sg.popup_get_date(start_mon=int(mois_fin), start_day=int(jour_fin), start_year=int(annee_fin), begin_at_sunday_plus=1, title="Date de début")
        jour_fin = str(date_fin_tuple[1]).zfill(2)
        mois_fin = str(date_fin_tuple[0]).zfill(2)
        annee_fin = str(date_fin_tuple[2]).zfill(2)
        window['-jour_fin-'].update(jour_fin)
        window['-mois_fin-'].update(mois_fin)
        window['-annee_fin-'].update(annee_fin)

      if event == '-decalage_utc-':
        fuseau = 'UTC'
        print("decalage: " + str(decalage[fuseau]))
      if event == '-decalage_ddu_hiver-':
        fuseau = 'DDU hiver'
        print("decalage: " + str(decalage[fuseau]))
      if event == '-decalage_ddu_ete-':
        fuseau = 'DDU été'
        print("decalage: " + str(decalage[fuseau]))

      if event == '-recuperation_donnees-':
        print("récupération des données: ")
        data = recuperation_donnees()
        donnees_en_memoire = jour_debut + "/" + mois_debut + "/" + annee_debut + " - " + heure_debut + ":" + minute_debut + "  >>>  " + jour_fin + "/" + mois_fin + "/" + annee_fin + " - " + heure_fin + ":" + minute_fin
        couleur_donnees = 'green'
        window['-donnees_en_memoire-'].update(donnees_en_memoire, couleur_donnees, "white" )

      if event == '-export_csv-':
        print("export_csv")
        write_data(data=data, P=values['-plot_p-'], T=values['-plot_t-'], FMOY=values['-plot_ff-'], DMOY=values['-plot_dd-'], FINS=values['-plot_fi-'], HU=values['-plot_u-'], VIS=values['-plot_vis-'])

      if event == '-unite_vent_ms-':
        unite_vent = 'm/s'
        print("unite_vent:" + unite_vent)
      if event == '-unite_vent_kmh-':
        unite_vent = 'km/h'
        print("unite_vent:" + unite_vent)
      if event == '-unite_vent_kt-':
        unite_vent = 'kt'
        print("unite_vent:" + unite_vent)
      if event == '-plot_vent_minute_ponctuel-':
        print("plot_vent_minute_ponctuel")
        if 'tkcanvas' in globals():
            tkcanvas.get_tk_widget().destroy()
        fig, ax, GRAPHE = plot_vent_minute_ponctuel(data, unite_vent)
        tkcanvas = draw_figure(window['-CANVAS-'].TKCanvas, fig)

      if event == '-unite_pression_mmhg-':
        unite_pression = 'mmHg'
        print("unite_pression:" + unite_pression)
      if event == '-unite_pression_hpa-':
        unite_pression = 'hPa'
        print("unite_pression:" + unite_pression)
      if event == '-plot_pression_minute_ponctuel-':
        print("plot_pression_minute_ponctuel")
        if 'tkcanvas' in globals():
            tkcanvas.get_tk_widget().destroy()
        fig, ax, GRAPHE = plot_pression_minute_ponctuel(data,unite_pression)   # unité possibles : 'hPa' ou 'mmHg'
        tkcanvas = draw_figure(window['-CANVAS-'].TKCanvas, fig)

      if event == '-unite_temperature_c-':
        unite_temperature = '°C'
        print("unite_temperature:" + unite_temperature)
      if event == '-unite_temperature_f-':
        unite_temperature = '°F'
        print("unite_temperature:" + unite_temperature)
      if event == '-unite_temperature_k-':
        unite_temperature = 'K'
        print("unite_temperature:" + unite_temperature)
      if event == '-plot_temperature_minute_ponctuel-':
        print("plot_temperature_minute_ponctuel")
        if 'tkcanvas' in globals():
            tkcanvas.get_tk_widget().destroy()
        fig, ax, GRAPHE = plot_temperature_minute_ponctuel(data,unite_temperature)   # unité possibles : 'hPa' ou 'mmHg'
        tkcanvas = draw_figure(window['-CANVAS-'].TKCanvas, fig)

      if event == '-plot_humidite_minute_ponctuel-':
        print("plot_humidite_minute_ponctuel")
        if 'tkcanvas' in globals():
            tkcanvas.get_tk_widget().destroy()
        fig, ax, GRAPHE = plot_humidite_minute_ponctuel(data)
        tkcanvas = draw_figure(window['-CANVAS-'].TKCanvas, fig)

      if event == '-export_plot-':
        plt.savefig(GRAPHE, bbox_inches="tight")
        plt.close(fig)

    ## FIN DU PROGRAMME
