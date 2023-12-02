import pandas as pd
import json

admissions_data = pd.read_csv(r"/Users/aaravashah/Admissions Committee Logs - NEW Pairers LOGS (From Jan 2023).csv")

def get_pairing_date(pairing_date):
    try:
        if pairing_date[1] == '-' or pairing_date[1] == '/':
            pairing_month = int(pairing_date[0])
            pairing_date = pairing_date[2:]
        else: 
            pairing_month = int(pairing_date[:2])
            pairing_date = pairing_date[3:]
        if pairing_date[1] == '-' or pairing_date[1] == '/':
            pairing_day = int(pairing_date[0])
            pairing_year = pairing_date[2:]
        else: 
            pairing_day = int(pairing_date[:2])
            pairing_year = pairing_date[3:]
        return int(pairing_month), int(pairing_day), int(pairing_year)
    except:
        return -1, -1, -1

def filter_data(df, beginning_date):
    df.drop(df.columns[[8, 9, 10]], axis='columns', inplace=True)
    beginning_month, beginning_day, beginning_year = get_pairing_date(beginning_date)
    filtered_df = pd.DataFrame(columns=df.columns)
    filtered_df_row = 0

    for row in df.index:
        pairing_date = df.loc[row, 'Assigned']
        pairing_month, pairing_day, pairing_year = get_pairing_date(pairing_date)
        if(pairing_year > beginning_year):
            pairer = df.loc[row, 'Pairer']
            df.loc[row, 'Pairer'] = pairer.strip().lower() if pairer[:4] != 'josh' else pairer.lower()
            filtered_df.loc[filtered_df_row] = df.loc[row] # warning here, fix later
            filtered_df_row += 1
        elif(pairing_year == beginning_year):
            if(pairing_month > beginning_month):
                pairer = df.loc[row, 'Pairer']
                df.loc[row, 'Pairer'] = pairer.strip().lower() if pairer[:4] != 'josh' else pairer.lower()
                filtered_df.loc[filtered_df_row] = df.loc[row]
                filtered_df_row += 1
            elif(pairing_month == beginning_month):
                if(pairing_day > beginning_day):
                    pairer = df.loc[row, 'Pairer']
                    df.loc[row, 'Pairer'] = pairer.strip().lower() if pairer[:4] != 'josh' else pairer.lower()
                    filtered_df.loc[filtered_df_row] = df.loc[row]
                    filtered_df_row += 1
    
    return(filtered_df)

def get_individual_data(df):
    pairer_info = {}
    incomplete_pairings = {}
    rejected_pairings = {}

    for row in df.index:
        pairer = df.loc[row, 'Pairer']
        incomplete_pairings[pairer] = 0 if pairer not in incomplete_pairings.keys() else incomplete_pairings[pairer]
        rejected_pairings[pairer] = {'Accepted': 0, 'Rejected': 0} if pairer not in rejected_pairings.keys() else rejected_pairings[pairer]
        pairer_info[pairer] = {'Total Pairing Days': 0, 'Total Students Paired': 0} if pairer not in pairer_info.keys() else pairer_info[pairer]
        if df.loc[row, 'Pairer Finalized (CheckBox)'] != True:
            incomplete_pairings[pairer] += 1
            df.drop(index=row, axis='index', inplace=True)
        elif(df.loc[row, 'Accepted (check Box)'] == True):
            pairer_info[pairer]['Total Pairing Days'] += int(df.loc[row, 'Days Taken'])
            pairer_info[pairer]['Total Students Paired'] += 1
            rejected_pairings[pairer]['Accepted'] += 1
        else:
            rejected_pairings[pairer]['Rejected'] += 1

    return pairer_info, incomplete_pairings, rejected_pairings

def add_committee_data(pairer_info, rejected_pairings):
    committee_pairing_days = 0
    committee_students_paired = 0
    committee_rejected = 0
    committee_accepted = 0
    avg_pairing_time = {}
    percentage_rejected = {}

    for pairer in pairer_info.keys():
        committee_pairing_days += pairer_info[pairer]['Total Pairing Days']
        committee_students_paired += pairer_info[pairer]['Total Students Paired']
        avg_pairing_time[pairer] = "Zero students completed on logs" if pairer_info[pairer]['Total Students Paired'] == 0 else pairer_info[pairer]['Total Pairing Days'] / pairer_info[pairer]['Total Students Paired']
        committee_rejected += rejected_pairings[pairer]['Rejected']
        committee_accepted += rejected_pairings[pairer]['Accepted']
        percentage_rejected[pairer] = "Zero students completed on logs" if (rejected_pairings[pairer]['Rejected'] + rejected_pairings[pairer]['Accepted'] == 0) else rejected_pairings[pairer]['Rejected']/(rejected_pairings[pairer]['Rejected'] + rejected_pairings[pairer]['Accepted'])
    avg_pairing_time["COMMITTEE"] = committee_pairing_days / committee_students_paired
    percentage_rejected["COMMITTEE"] = committee_rejected / (committee_rejected + committee_accepted)

    return avg_pairing_time, percentage_rejected

def get_data(df, beginning_date):
    df = filter_data(df, beginning_date=beginning_date)
    pairer_info, incomplete_pairings, rejected_pairings = get_individual_data(df)
    avg_pairing_time, percentage_rejected = add_committee_data(pairer_info, rejected_pairings)

    out = {'Average Accepted Pairing Time': avg_pairing_time, 'Incomplete Pairings': incomplete_pairings, 'Percentage Rejected': percentage_rejected}
    outfile = open("admissions_committee.json", "w")
    json.dump(out, outfile)
    outfile.close()

get_data(admissions_data, "11-2-2023")
