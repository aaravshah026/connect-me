import pandas as pd
import json
import warnings
import datetime
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_date(str_date):
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
    df.drop(df.columns[[0, 6, 10]], axis='columns', inplace=True)

    # create filtered dataframe with target rows
    filtered_df = pd.DataFrame(columns=df.columns)
    filtered_df_row = 0

    # dataframe row iteration
    for row in df.index:
        assigned_date = get_date(df.loc[row, "Date Assigned"])
        # add row to filtered_df if "Date Assigned" is between beginning and end dates
        print(beginning_date, assigned_date, end_date)
        if assigned_date != None and between_dates(beginning_date, assigned_date, end_date):
            # don't add row to filtered_df if the interview is scheduled for a future date (ie. process isn't complete)
            if date_difference(datetime.datetime.now(), get_date(df.loc[row, "Interview Date"])) < 0:
                filtered_df.loc[filtered_df_row] = df.loc[row]
                filtered_df_row += 1

    # return filtered dataframe
    return filtered_df

def gather_data(dfs, beginning_date, end_date):
    beginning_date = get_date(beginning_date)
    end_date = datetime.datetime.now() if end_date == None else end_date

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
            total_initial_email += abs(date_difference(get_date(df.loc[row, "Date Assigned"]), get_date(df.loc[row, "Date of Result 1 Email"])))
            if df.loc[row, "Initial Screening"] == True:
                num_initial_accepted += 1
                if df.loc[row, "Interview Scheduled"] == True:
                    num_scheduled_interview += 1
                    if not pd.isna(df.loc[row, "Date of Result 2 Email"]):
                        num_show_interview += 1
                        time_welcome_email += abs(date_difference(get_date(df.loc[row, "Interview Date"]), get_date(df.loc[row, "Date of Result 2 Email"])))
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
    message = "Tutor application data from " + beginning_date.strftime('%m/%d/%Y') + " to " + end_date.strftime('%m/%d/%Y')
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
    outfile = open("/Users/aaravashah/Connect Me/tutor_information.json", "w")
    json.dump(out, outfile)
    outfile.close()

tutor_data_example = pd.read_csv("file path to .csv file here")
tutor_data = [["Example", tutor_data_example]]
# add ["name", pd.DataFrame] pairs for each person!

gather_data(tutor_data, beginning_date="1/1/2024", end_date=None)
