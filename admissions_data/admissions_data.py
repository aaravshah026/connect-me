import pandas as pd
import warnings
import datetime
import json
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_date(str_date):
    if str_date == None:
        return datetime.datetime.now()
    try:
        return datetime.datetime.strptime(str_date, "%m/%d/%Y")
    except:
        try:
            return datetime.datetime.strptime(str_date, "%m/%d/%y")
        except:
            return None

def between_dates(beginning_date, middle_date, end_date):
    # return true if middle_date is in range [beginning_date, end_date]
    return (date_difference(beginning_date, middle_date) >= 0) and (date_difference(middle_date, end_date) >= 0)

def date_difference(beginning_date, end_date):
    # returns the difference in days between two datetime objects
    try:
        return (end_date - beginning_date).days
    except:
        return -1

def filter_data(df, beginning_date, end_date):
    # drop unnecessary columns from the dataframe
    df.drop(df.columns[[9, 10]], axis='columns', inplace=True)

    # create filtered dataframe with target rows
    filtered_df = pd.DataFrame(columns=df.columns)
    filtered_df_row = 0

    # dataframe row iteration
    for row in df.index:
        assigned_date = get_date(df.loc[row, 'Assigned'])

        # add row to filtered_df if "Assigned" date is between beginning and end dates
        if between_dates(beginning_date, assigned_date, end_date):
            pairer = df.loc[row, 'Pairer']
            df.loc[row, 'Pairer'] = pairer.strip().lower()
            filtered_df.loc[filtered_df_row] = df.loc[row]
            filtered_df_row += 1

    # return filtered dataframe
    return filtered_df

def get_individual_data(df):
    # metrics to evaluate
    pairer_info = {}
    incomplete_pairings = {}
    rejected_pairings = {}

    for row in df.index:
        # determine who the pairier for the row is
        pairer = df.loc[row, 'Pairer']

        # add the pairer to the dictionaries if not already present
        incomplete_pairings[pairer] = 0 if pairer not in incomplete_pairings.keys() else incomplete_pairings[pairer]
        rejected_pairings[pairer] = {'Accepted': 0, 'Rejected': 0} if pairer not in rejected_pairings.keys() else rejected_pairings[pairer]
        pairer_info[pairer] = {'Total Pairing Days': 0, 'Total Students Paired': 0} if pairer not in pairer_info.keys() else pairer_info[pairer]
        
        # if the pairer finalized checkbox is not clicked, add the row as an incomplete pairing
        if df.loc[row, 'Pairer Finalized (CheckBox)'] != True:
            incomplete_pairings[pairer] += 1
            df.drop(index=row, axis='index', inplace=True)

        # if the checkbox is clicked and the pairing was 'paired', add the row to the paired students data
        elif df.loc[row, 'Pairing Status'] == 'Paired':
            pairer_info[pairer]['Total Pairing Days'] += int(df.loc[row, 'Days Taken'])
            pairer_info[pairer]['Total Students Paired'] += 1
            rejected_pairings[pairer]['Accepted'] += 1
        
        # if the checkbox is clicked and the pairing was 'rejected', add the row to the rejected students data
        elif df.loc[row, 'Pairing Status'] == 'Rejected':
            rejected_pairings[pairer]['Rejected'] += 1

    # return the dictionaries containing the data for each pairer
    return pairer_info, incomplete_pairings, rejected_pairings

def get_committee_data(pairer_info, rejected_pairings):
    # metrics to evaluate
    committee_pairing_days = 0
    committee_students_paired = 0
    committee_rejected = 0
    committee_accepted = 0
    avg_pairing_time = {}
    percentage_rejected = {}

    # iterate through all pairers
    for pairer in pairer_info.keys():

        # add pairer data to total committee data
        committee_pairing_days += pairer_info[pairer]['Total Pairing Days']
        committee_students_paired += pairer_info[pairer]['Total Students Paired']
        committee_rejected += rejected_pairings[pairer]['Rejected']
        committee_accepted += rejected_pairings[pairer]['Accepted']

        # calculate average/percentages for individual pairer data
        avg_pairing_time[pairer] = "Zero students completed on logs" if pairer_info[pairer]['Total Students Paired'] == 0 else round(pairer_info[pairer]['Total Pairing Days'] / pairer_info[pairer]['Total Students Paired'], 2)
        percentage_rejected[pairer] = "Zero students completed on logs" if (rejected_pairings[pairer]['Rejected'] + rejected_pairings[pairer]['Accepted'] == 0) else round(rejected_pairings[pairer]['Rejected']/(rejected_pairings[pairer]['Rejected'] + rejected_pairings[pairer]['Accepted']), 2)
    
    # calculate average/percentages for committee data
    avg_pairing_time["COMMITTEE"] = round(committee_pairing_days / committee_students_paired, 2)
    percentage_rejected["COMMITTEE"] = round(committee_rejected / (committee_rejected + committee_accepted), 2)

    # return the dictionaries containing the individual and committee data
    return avg_pairing_time, percentage_rejected

def get_data(df, beginning_date, end_date):
    # convert date strings into datetime objects
    beginning_date = get_date(beginning_date)
    end_date = get_date(end_date)

    # filter dataframe to remove unnecessary rows/columns
    df = filter_data(df, beginning_date=beginning_date, end_date=end_date)

    # collect individual pairer data
    pairer_info, incomplete_pairings, rejected_pairings = get_individual_data(df)

    # use individual pairer data to calculate committee data
    avg_pairing_time, percentage_rejected = get_committee_data(pairer_info, rejected_pairings)

    # output individual pairer and committee data as a JSON file
    message = "Pairing data from " + beginning_date.strftime('%m/%d/%Y') + " to " + end_date.strftime('%m/%d/%Y')
    out = {message: {}, 'Average Accepted Pairing Time': avg_pairing_time, 'Incomplete Pairings': incomplete_pairings, 'Percentage Rejected': percentage_rejected}
    outfile = open("/Users/aaravashah/Connect Me/admissions_committee.json", "w")
    json.dump(out, outfile)
    outfile.close()

admissions_data = pd.read_csv(r"path to .csv file here")
# update admissions_data to the correct file path
get_data(admissions_data, beginning_date="1/1/2024", end_date=None)
