import pandas as pd
from datetime import date
import json

def get_pairing_data(pairing_date):
    try:
        if pairing_date[1] == '-':
            pairing_month = int(pairing_date[0])
            pairing_date = pairing_date[2:]
        else: 
            pairing_month = int(pairing_date[:2])
            pairing_date = pairing_date[3:]
        if pairing_date[1] == '-':
            pairing_day = int(pairing_date[0])
        else: 
            pairing_day = int(pairing_date[:2])
        return pairing_month, pairing_day
    except:
        return -1, -1

def monthly_data(df, num_months):
    curr_month = int(date.today().strftime("%m"))
    curr_day = int(date.today().strftime("%d"))
    beginning_month = ((curr_month - (1 + num_months)) % 12) + 1
    pairer_info = {}
    incomplete_pairings = {}

    for row in df.index:
        pairer = df.loc[row, 'Pairer']
        pairing_date = df.loc[row, 'Assigned']
        pairing_month, pairing_day = get_pairing_data(pairing_date)
        
        if type(pairer) == str and (pairing_month > beginning_month or (pairing_month == beginning_month and pairing_day > curr_day)):
            pairer = pairer.strip().lower() if pairer[:4] != 'josh' else pairer.lower()
            incomplete_pairings[pairer] = 0 if pairer not in incomplete_pairings.keys() else incomplete_pairings[pairer]
            pairer_info[pairer] = {'Total Pairing Days': 0, 'Total Students Paired': 0} if pairer not in pairer_info.keys() else pairer_info[pairer]
            
            if df.loc[row, 'Pairer Finalized (CheckBox)'] != True:
                incomplete_pairings[pairer] += 1
                df.drop(index=row, axis='index', inplace=True)
            else:
                pairer_info[pairer]['Total Pairing Days'] += int(df.loc[row, 'Days Taken'])
                pairer_info[pairer]['Total Students Paired'] += 1
        else:
            df.drop(index=row, axis='index', inplace=True)

    committee_pairing_days = 0
    committee_students_paired = 0
    avg_pairing_time = {}

    for pairer in pairer_info.keys():
        committee_pairing_days += pairer_info[pairer]['Total Pairing Days']
        committee_students_paired += pairer_info[pairer]['Total Students Paired']
        avg_pairing_time[pairer] = pairer_info[pairer]['Total Pairing Days'] / pairer_info[pairer]['Total Students Paired']
    avg_pairing_time["COMMITTEE"] = committee_pairing_days / committee_students_paired

    out = {'Average Pairing Time': avg_pairing_time, 'Incomplete Pairings': incomplete_pairings}
    outfile = open("admissions_committee.json", "w")
    json.dump(out, outfile)
    outfile.close()

admissions_data = pd.read_csv(r"/Users/aaravashah/Admissions Committee Logs - NEW Pairers LOGS (From Jan 2023).csv")
admissions_data.drop(admissions_data.columns[[7, 8, 9]], axis='columns', inplace=True)
monthly_data(admissions_data, 1)