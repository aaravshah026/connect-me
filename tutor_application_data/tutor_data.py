import pandas as pd
import json
import warnings
import datetime
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_date(pairing_date):
    # formatted as a string either "mm-dd-yyyy" or "mm/dd/yyyy", with the year being either 2 or 4 digits
    # returns three integers representing the month, day, and year of the string literal
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
        if len(pairing_year) == 2:
            pairing_year = int('20' + pairing_year)
        return int(pairing_month), int(pairing_day), int(pairing_year)
    except:
        return -1, -1, -1
def between_dates(bY, bM, bD, eY, eM, eD, mY, mM, mD):
    # return true if the date 'm' is in range ('b', 'e'], false otherwise
    beginning_date = datetime.date(bY, bM, bD)
    middle_date = datetime.date(mY, mM, mD)
    end_date = datetime.date(eY, eM, eD)
    return ((end_date - middle_date).days >= 0) and ((middle_date - beginning_date).days > 0)
def date_difference(date1, date2):
    # returns the difference in days between two date strings
    # example: date1 = "5/30/2024", date2 = "6/1/2024", return 2
    if pd.isna(date1) or pd.isna(date2):
        return -1
    bM, bD, bY = get_date(date1)
    eM, eD, eY = get_date(date2)
    beginning_date = datetime.date(bY, bM, bD)
    end_date = datetime.date(eY, eM, eD)
    return (end_date - beginning_date).days
def resolve_null_end(end_date):
    if end_date == None:
        end_month = datetime.datetime.now().month
        end_day = datetime.datetime.now().day
        end_year = datetime.datetime.now().year
        end_date = str(end_month) + "-" + str(end_day) + "-" + str(end_year)
    return end_date

def filter_data(df, beginning_date, end_date):
    # drop unnecessary columns from the dataframe
    df.drop(df.columns[[0, 6, 10]], axis='columns', inplace=True)

    # get the beginning and end date values for row comparisons
    end_month, end_day, end_year = get_date(resolve_null_end(end_date))
    beginning_month, beginning_day, beginning_year = get_date(beginning_date)

    # create filtered dataframe with target rows
    filtered_df = pd.DataFrame(columns=df.columns)
    filtered_df_row = 0

    # dataframe row iteration
    for row in df.index:
        assigned_date = df.loc[row, "Date Assigned"]
        assigned_month, assigned_day, assigned_year = get_date(assigned_date)
        # add row to filtered_df if "Date Assigned" is between beginning and end dates
        if assigned_year > 0 and between_dates(beginning_year, beginning_month, beginning_day, end_year, end_month, end_day, assigned_year, assigned_month, assigned_day):
            # don't add row to filtered_df if the interview is scheduled for a future date (ie. process isn't complete)
            if date_difference(date1=resolve_null_end(end_date=None), date2=df.loc[row, "Interview Date"]) < 0:
                filtered_df.loc[filtered_df_row] = df.loc[row]
                filtered_df_row += 1

    # return filtered dataframe
    return filtered_df

def gather_data(dfs, beginning_date, end_date):
    # metrics to evaluate
    number_tutors_assigned = {}
    time_initial_email = {}
    percent_initial_accepted = {}
    percent_schedule_interview = {}
    percent_show_interview = {}
    time_interview_results_email = {}
    percent_pass_interview = {}
    percent_join_discord = {}
    percent_accepted = {}
    number_tutors_joined = {}

    for name_df_pair in dfs:
        # dfs consists of a list of [name, dataframe] pairs for each interviewer
        interviewer = name_df_pair[0]
        df = name_df_pair[1]
        df = filter_data(df, beginning_date=beginning_date, end_date=end_date)
        print(df)

        # individual data variables to put into dictionaries later
        num_tutors = 0
        total_initial_email = 0
        num_initial_accepted = 0
        num_scheduled_interview = 0
        num_show_interview = 0
        time_welcome_email = 0
        num_pass_interview = 0
        num_join_discord = 0

        # data collection!
        for row in df.index:
            num_tutors += 1
            total_initial_email += abs(date_difference(df.loc[row, "Date Assigned"], df.loc[row, "Date of Result 1 Email"]))
            if df.loc[row, "Initial Screening"] == True:
                num_initial_accepted += 1
                if df.loc[row, "Interview Scheduled"] == True:
                    num_scheduled_interview += 1
                    if not pd.isna(df.loc[row, "Date of Result 2 Email"]):
                        num_show_interview += 1
                        time_welcome_email += abs(date_difference(df.loc[row, "Interview Date"], df.loc[row, "Date of Result 2 Email"]))
                        if df.loc[row, "Interview Results"] == True:
                            num_pass_interview += 1
                            if df.loc[row, "Added to Discord (Aarav)"] == True:
                                num_join_discord += 1

        # putting it all together
        number_tutors_assigned[interviewer] = num_tutors
        time_initial_email[interviewer] = round(total_initial_email / num_tutors, 2)
        percent_initial_accepted[interviewer] = str(round(num_initial_accepted / num_tutors * 100, 2)) + "%"
        percent_schedule_interview[interviewer] = str(round(num_scheduled_interview / num_initial_accepted * 100, 2)) + "%"
        percent_show_interview[interviewer] = str(round(num_show_interview / num_scheduled_interview * 100, 2)) + "%"
        time_interview_results_email[interviewer] = round(time_welcome_email / num_show_interview, 2)
        percent_pass_interview[interviewer] = str(round(num_pass_interview / num_show_interview * 100, 2)) + "%"
        percent_join_discord[interviewer] = str(round(num_join_discord / num_pass_interview * 100, 2)) + "%"
        percent_accepted[interviewer] = str(round(num_join_discord / num_tutors * 100, 2)) + "%"
        number_tutors_joined[interviewer] = num_join_discord
    
    # outputting the information into a json file
    message = "Tutor application data from " + beginning_date + " to " + resolve_null_end(end_date)
    out = {message: {},
           'Total number of tutors assigned:': number_tutors_assigned,
           'Average number of days to send the initial email:': time_initial_email,
           'Percentage of tutors passing the initial screening:': percent_initial_accepted,
           'Percentage of tutors that schedule interviews:': percent_schedule_interview,
           'Percentage of tutors that show up for interviews:': percent_show_interview,
           'Average number of days to send interview results email:': time_interview_results_email,
           'Percentage of tutors that pass their interview:': percent_pass_interview,
           'Percentage of accepted tutors that join the Discord:': percent_join_discord,
           'Percentage of tutors that pass the whole process:': percent_accepted,
           'Total number of tutors accepted:': number_tutors_joined}
    outfile = open("tutor_information.json", "w")
    json.dump(out, outfile)
    outfile.close()

tutor_data_person1 = pd.read_csv("pathfile_to_person1.csv")
tutor_data_person2 = pd.read_csv("pathfile_to_person2.csv")
tutor_data_person3 = pd.read_csv("pathfile_to_person3.csv")
tutor_data_person4 = pd.read_csv("pathfile_to_person4.csv")

tutor_data = [["Person 1", tutor_data_person1], ["Person 2", tutor_data_person2], ["Person 3", tutor_data_person3], ["Person 4", tutor_data_person4]]
# change to correct names and path locations!

gather_data(tutor_data, beginning_date="4-1-2024", end_date="6-23-2024")
