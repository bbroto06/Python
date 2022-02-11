import sqlite3
import yagmail
import pandas as pd
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

# Nurse
def select_all_nurse(conn):
    """
    Query all rows in the Nurse table
    :param conn: the Connection object
    :return: dataframe containing all the data of nurse table
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM nurse")

    rows = cur.fetchall()
    cols = ['NurseId',         'LastName',      'FirstName',   'Designation',   'Qualification', \
            'LicenseNumber',   'BirthDate',     'HireDate',    'Address',       'City',          \
            'State',           'Country',       'PostalCode',  'Phone',         'Email',         \
            'Department',      'Availability',  'Shift']
    df = pd.DataFrame(columns=cols)
    
    for row in rows:
        a_series = pd.Series(list(row), index=df.columns)
        df = df.append(a_series, ignore_index=True)
    
    return (df)

# HOSPITAL
def select_all_hospital(conn):
    """
    Query all rows in the Hospital table
    :param conn: the Connection object
    :return: dataframe containing all the data of hospital table
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM hospital")

    rows = cur.fetchall()
    cols = ['HospitalId',    'Name',          'Address',       'City',         'State',      \
            'Country',       'PostalCode',    'Phone',         'Email',        'Quantity',   \
            'Department',    'Availability',  'Shift']
    df = pd.DataFrame(columns=cols)
    
    for row in rows:
        a_series = pd.Series(list(row), index=df.columns)
        df = df.append(a_series, ignore_index=True)
    
    return (df)

# Create requirement table
def create_req_table(df_hospital):
    """
    Create requirement table based on the requirements provided inside the hospital table
    :param df_hospital: the hospital dataframe
    :return: dataframe containing each and every requirement of the hospitals
    """
    cols = ['ReqId',      'HospitalId',     'Department',    'Availability',  'Shift', \
            'Nurse',      'ReqStatus']
    df = pd.DataFrame(columns=cols)
    
    req_counter = 1
    for index, row in df_hospital.iterrows():
        quantity = int(row['Quantity'])
        while(quantity > 0):
            reqId = 'R' + str(req_counter)
            nurse = 'NotAssigned'
            reqStatus = 'NotSatisfied'
            a_list = [reqId, row['HospitalId'], row['Department'], row['Availability'], row['Shift'], nurse, reqStatus]
            a_series = pd.Series(a_list, index=df.columns)
            df = df.append(a_series, ignore_index=True)
            req_counter += 1
            quantity -= 1
    
    return(df)

# Try to find if nurses are available that are matching the Department, Availability and Shift
def match_filters(department, availability, shift, df_nurse):
    """
    Try to find if nurses are available that are matching the Department, Availability and Shift
    :param department: department of a particular row
    :param availability: availability of a particular row
    :param shift: shift of a particular row
    :param df_nurse: the nurse dataframe
    :return: the list of nurses matching the search criteria. It might be blank if no matching nurses are found
    """
    list_of_nurses_available = []
    df = df_nurse[(df_nurse['Department'] == department) & (\
                    df_nurse['Availability'] == availability) & (\
                    df_nurse['Shift'] == shift)]
    if(not df.empty):
        list_of_nurses_available = list(set(df['NurseId']))
        df_nurse = df_nurse.loc[~df_nurse['NurseId'].isin(list_of_nurses_available)]
        
    return (list_of_nurses_available, df_nurse)

# Try to fill the requirements of the hosptal using nurse table
def fill_req_table(df_req, df_nurse):
    """
    Try to fill the requirement table based on the availability of the nurses provided inside the nurse table
    :param df_req: the requirements dataframe
    :param df_nurse: the nurse dataframe
    :return: the requirements dataframe after filling out the requirements. It can still contain blanks in the Nurse column
    """
    for index, row in df_req.iterrows():
        reqId = row['ReqId']
        hospitalId = row['HospitalId']
        department = row['Department']
        availability = row['Availability']
        shift = row['Shift']
        nurse = row['Nurse']
        reqStatus = row['ReqStatus']
        
        matching_nurse_id = []
        if(reqStatus == 'NotSatisfied'):
            matching_nurse_id, df_nurse = match_filters(department, availability, shift, df_nurse)
            if(len(matching_nurse_id)):
                if(len(matching_nurse_id) == 1):
                    row['Nurse'] = matching_nurse_id[0]
                    row['ReqStatus'] = 'Satisfied' # If only 1 nurse satisfies the conditions
                elif(len(matching_nurse_id) > 1):
                    row['Nurse'] = matching_nurse_id
                    row['ReqStatus'] = 'NeedToFinalise' # If more than 1 nurse satisfy the conditions
                else:
                    print('Else part')
    return (df_req)

# Send email to the nurses where ReqStatus is satisfied 
def send_email_to_nurse(df_nurse, df_hospital, df_req_fill):
    """
    Send automated email to the nurses where ReqStatus is Satisfied [For the rest, email needs to be sent manually]
    :param df_nurse: the nurse dataframe
    :param df_hospital: the hospital dataframe
    :param df_req_fill: the requirements dataframe after filling out the requirements
    :return: 
    """
    df_essential = df_req_fill.loc[df_req_fill['ReqStatus'] == 'Satisfied']
    yag = yagmail.SMTP('nurse.scheduler.agency@gmail.com', 'nurse.scheduler.agency123')
    subject = '[Nurse Scheduling Agency] Schedule for next week'
    for index, row in df_essential.iterrows():
        hospitalId = row['HospitalId']
        department = row['Department']
        availability = row['Availability']
        shift = row['Shift']
        nurseId = row['Nurse']
        
        nurseName = str(df_nurse.loc[df_nurse['NurseId'] == nurseId, 'FirstName'].values[0])
        nurseEmail = str(df_nurse.loc[df_nurse['NurseId'] == nurseId, 'Email'].values[0])
        nurseAvailability = str(df_nurse.loc[df_nurse['NurseId'] == nurseId, 'Availability'].values[0])
        nurseShift = str(df_nurse.loc[df_nurse['NurseId'] == nurseId, 'Shift'].values[0])
        hospitalName = str(df_hospital.loc[df_hospital['HospitalId'] == hospitalId, 'Name'].values[0])
        hospitalAddress = str(df_hospital.loc[df_hospital['HospitalId'] == hospitalId, 'Address'].values[0])
        hospitalPostalCode = str(df_hospital.loc[df_hospital['HospitalId'] == hospitalId, 'PostalCode'].values[0])
        hospitalPhone = str(df_hospital.loc[df_hospital['HospitalId'] == hospitalId, 'Phone'].values[0])
        
        msg = "\nHi {}, \n\n Please note that you are scheduled to work at {} in {} for the next week. \n Address = {} \n PostalCode = {} \n Phone = {}  \n Day  = {} \n Shift = {} \n\nRegards,\nNurseScheduler".format(nurseName, hospitalName, department, hospitalAddress, hospitalPostalCode, hospitalPhone, nurseAvailability, nurseShift)
        yag.send(nurseEmail, subject, msg)
    
    return

def get_last_row(conn, tablename):
    """
    Get the last entry of the ID column
    :param conn:
    :param colname:
    :return: bottom most entry of the column
    """
    last_id = ''
    try:
        cur = conn.cursor()
        cur.execute('''SELECT * FROM '%s' ORDER BY ROWID DESC LIMIT 1;''' % (tablename) )
        df_last_row = pd.DataFrame(cur.fetchall())
        df_last_row.columns = [ x[0] for x in cur.description ]
    except:
        print('Unable to fetch the last value')
    return (df_last_row)

def create_new_id(conn, tablename, colname):
    last_row = get_last_row(conn, tablename)
    last_id = last_row[colname][0]
    first_char = last_id[0]
    num = int(last_id[1:])
    new_num = num + 1
    new_id = first_char + str(new_num)
    return (new_id)

def insert_nurse(conn):
    """
    Insert a new nurse into the nurse table
    :param conn:
    :return: lastrowid
    """
    tablename = 'nurse'
    colname = 'NurseId'
    
    new_nurse_id = create_new_id(conn, tablename, colname)

    try:
        sql = ''' INSERT INTO nurse( \
                    'NurseId',         'LastName',      'FirstName',   'Designation',   'Qualification', \
                    'LicenseNumber',   'BirthDate',     'HireDate',    'Address',       'City',          \
                    'State',           'Country',       'PostalCode',  'Phone',         'Email',         \
                    'Department',      'Availability',  'Shift')
                  VALUES(?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?) '''
        
        new_nurse = (new_nurse_id, 'Chakraborty',    'Chandrima',     'Registered Nurse (RN)',   'Bachelor of Science in Nursing', \
                     '777222',     '1988-12-09 0:00', '2021-01-01 0:00', '4360 Ave Dupuis',        'Montreal', \
                     'QC',         'Canada',          'H3T 1E8',         '4388336834',             'chandrima@gmail.com', \
                     'Oncology',   'Weekday',         'Day')
        
        cur = conn.cursor()
        cur.execute(sql, new_nurse)
        conn.commit()
        return (cur.lastrowid)
    
    except:
        print('Invalid entry')
    return

def insert_hospital(conn):
    print('')
    return

def update_nurse(conn):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :return: lastrowid
    """
    n_id = input('Enter the ID of the nurse whose records need to be updated : ')
    try:
        sql = ''' UPDATE nurse
                  SET LastName=?, FirstName=?, Phone=?, Email=?, Availability=?, Shift=? 
                  WHERE NurseId = ?'''
        update_existing_nurse = ('Chakraborty', 'Chandrima', '438336834', 'chandrima@gmail.com', 'Weekend', 'Night', n_id)

        cur = conn.cursor()
        cur.execute(sql, update_existing_nurse)
        conn.commit()

        return (cur.lastrowid)
    
    except:
        print('This ID does not exist')
    return

def update_hospital(conn):
    print('Enter ID of hospital to update')
    return

def delete_nurse(conn):
    """
    Delete a nurse by NurseId
    :param conn:  Connection to the SQLite database
    :NurseId: id of the Nurse
    :return:
    """
    n_id = input('Enter the ID of the nurse whose records need to be deleted : ')
    try:
        sql = 'DELETE FROM nurse WHERE NurseId=?'
        delete_nurse_id = (n_id,)
        cur = conn.cursor()
        cur.execute(sql, delete_nurse_id)
        conn.commit()
        return (cur.lastrowid)
    
    except:
        print('This ID does not exist in the database')
    return

def delete_hospital(conn):
    print('Enter ID of hospital to delete')
    return

def select_a_nurse(conn, n_id):
    cur = conn.cursor()
    try:
        cur.execute(''' SELECT * FROM nurse WHERE NurseId = '%s'; ''' % (n_id) )
        df_n_id = pd.DataFrame(cur.fetchall())
        df_n_id.columns = [ x[0] for x in cur.description ]
    except:
        print('No records were found.')
    return(df_n_id)

def select_a_hospital(conn, h_id):
    cur = conn.cursor()
    try:
        cur.execute(''' SELECT * FROM hospital WHERE HospitalId = '%s'; ''' % (h_id) )
        df_h_id = pd.DataFrame(cur.fetchall())
        df_h_id.columns = [ x[0] for x in cur.description ]
    except:
        print('No records were found.')
    return(df_h_id)

def display_nurse(conn):
    n_id = input('Enter ID of the nurse whose records you want to see : ')
    df_n_id = select_a_nurse(conn, n_id)
    display(df_n_id)
    return

def display_hospital(conn):
    h_id = input('Enter ID of the hospital whose records you want to see : ')
    df_h_id = select_a_hospital(conn, h_id)
    display(df_h_id)
    return

def display_entire_nurse(conn):
    df_nurse = select_all_nurse(conn)
    print(df_nurse.shape)
    display(df_nurse)
    return

def display_entire_hospital(conn):
    df_hospital = select_all_hospital(conn)
    print(df_hospital.shape)
    display(df_hospital)
    return

def choice_of_table(conn):
    while(1):
        print('\n****\nSelect the table on which you want to operate')
        print('0 : Exit')
        print('1 : NURSE table')
        print('2 : HOSPITAL table')
        
        try:
            choice_table = int(input('Enter your choice : '))
            if(0 == choice_table):
                print('Exit')
                break
            elif(1==choice_table or 2==choice_table):
                choice_operation = choice_of_operation(conn, choice_table)
            else:
                print('\n Wrong Choice')
        except:
            print('\n Invalid selection')
            
    return (choice_table)

def get_filled_req_table(conn):
    df_nurse = select_all_nurse(conn)
    df_hospital = select_all_hospital(conn)
    df_req = create_req_table(df_hospital)
    df_req_fill = fill_req_table(df_req, df_nurse)
    return (df_nurse, df_hospital, df_req_fill)

def choice_of_operation(conn, choice_table):
    table = 'NURSE' if choice_table == 1 else 'HOSPITAL'
    while(1):
        print('\nSelect the type of operation on ', table, ' table')
        print('0 : Return to Main Menu')
        print('1 : To INSERT new record into ', table, ' table')
        print('2 : To UPDATE existing record of ', table, ' table')
        print('3 : To DELETE a record of ', table, ' table')
        print('4 : To DISPLAY a particular record of ', table, ' table')
        print('5 : To display entire ', table, ' table')
        print('6 : To create the requirement table')
        print('7 : To send emails to nurses where the requirement is satisfied')
        
        try:
            choice_operation = int(input('Enter your choice : '))
            if(0 == choice_operation):
                print('Exit')
                break
            elif(1 == choice_operation):
                print('INSERT into ', table, ' table')
                ret = insert_nurse(conn) if choice_table == 1 else insert_hospital(conn)
            elif(2 == choice_operation):
                print('UPDATE ', table, ' table')
                ret = update_nurse(conn) if choice_table == 1 else update_hospital(conn)
            elif(3 == choice_operation):
                print('DELETE from ', table, ' table')
                ret = delete_nurse(conn) if choice_table == 1 else delete_hospital(conn)
            elif(4 == choice_operation):
                print('display ', table, ' table where ID matches')
                ret = display_nurse(conn) if choice_table == 1 else display_hospital(conn)
            elif(5 == choice_operation):
                print('\n Display entire', table, ' table')
                ret = display_entire_nurse(conn) if choice_table == 1 else display_entire_hospital(conn)
            elif(6 == choice_operation):
                print('\n Create requirement table')
                df_nurse, df_hospital, df_req_fill = get_filled_req_table(conn)
                display(df_req_fill)
            elif(7 == choice_operation):
                print('\n Send emails as per requirement table')
                df_nurse, df_hospital, df_req_fill = get_filled_req_table(conn)
                send_email_to_nurse(df_nurse, df_hospital, df_req_fill)
            else:
                print('\n Wrong Choice')
        except:
            print('\n Invalid selection')
    return (choice_operation)

def main():
    database = r'C:\sqlite\gui\sqlitestudio-3.3.2\SQLiteStudio\chinook\chinook.db'  
    # create a database connection
    conn = create_connection(database)
    with conn:       
        while(1):
            print('\n Select an option')
            choice_table = choice_of_table(conn)
            if(choice_table == 0):
                break
        
        print('END')

if __name__ == '__main__':
    main()