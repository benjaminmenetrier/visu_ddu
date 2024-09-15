#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 15:22:19 2022

@author: tence
"""

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