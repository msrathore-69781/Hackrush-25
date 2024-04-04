from flask import Flask, render_template, request, redirect, url_for, session, flash , jsonify, redirect
import mysql.connector
import re
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MyNewPass',    #Enter ur password for root
    'database': 'CLUB_MS'
}
try:
    conn = mysql.connector.connect(**mysql_config)
    print("Connected to MySQL database successfully!")
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL database: {e}")
conn = mysql.connector.connect(**mysql_config)

@app.route('/', methods=['GET', 'POST'])
def login():
    # message = None
    if "message" in session:
        message = session["message"]
    else:
        message = None
    session["message"] = None

    ''' Log-in for Students '''
    if request.method == 'POST' and 'email_student' in request.form and 'password_student' in request.form:
        email = request.form['email_student']
        roll_no = request.form['password_student']
        print("Received email:", email)          # Debugging print statement
        print("Received roll number:", roll_no)  # Debugging print statement
        cursor = conn.cursor(dictionary=True)
        try:
            # cursor.execute('SELECT * FROM STUDENTS WHERE EMAIL = %s AND ROLL_NO = %s', (email, roll_no))
            cursor.execute('SELECT * FROM STUDENTS WHERE EMAIL = %s', (email,))
            user = cursor.fetchone()
            print("User:", user)                 # Debugging print statement
            if user:
                # Password check
                if roll_no != email.split("@")[0]:
                    print("Incorrect Student Password")
                    # flash("Incorrect Student Password", 'error')         # Flash error message
                    message = "Incorrect Student Password"
                else:
                    session['loggedin'] = "Student"
                    session['userid'] = user['ROLL_NO']
                    session['name'] = user['FIRST_NAME']
                    session['email'] = user['EMAIL']
                    session['user_info'] = user

                    cursor.execute('SELECT COUNCIL_NAME FROM COUNCIL_MEMBERS WHERE ROLLS_NO = %s AND POSITION = "Secretary"', (roll_no,))
                    council_secy = cursor.fetchone()
                    session["council_secretary"] = None
                    if council_secy:
                        session["council_secretary"] = council_secy['COUNCIL_NAME']
                    else:
                        cursor.execute('SELECT CLUBS_NAME FROM CLUB_MEMBERS WHERE ROLLS_NO = %s AND POSITION = "Secretary"', (roll_no,))
                        club_secy = cursor.fetchone()
                        session["club_secretary"] = None
                        if club_secy:
                            session["club_secretary"] = club_secy['CLUBS_NAME']

                    # return render_template('studentInfo.html', studentInfo=user)
                    return redirect(url_for('student_info'))
            else:
                print('User not found (incorrect email)')  # Debugging print statement
                # flash("User not found (incorrect email)", 'error')
                message = 'User not found (incorrect email)'

        except Exception as e:
            flash("An error occurred. Please try again later.", 'error')  # Flash error message
            print('Error:', e)                                            # Debugging print statement
            message = "An error occurred. Please try again later."
        finally:
            cursor.close()  # Always close the cursor

    ''' Log-in for Employees '''
    if request.method == 'POST' and 'email_employee' in request.form and 'password_employee' in request.form:
        email = request.form['email_employee']
        employee_id = request.form['password_employee']
        # print(type(request.form['password_employee']))
        print("Received email:", email)              # Debugging print statement
        print("Received employee id:", employee_id)  # Debugging print statement
        cursor = conn.cursor(dictionary=True)
        try:
            # cursor.execute('SELECT * FROM STUDENTS WHERE EMAIL = %s AND EMPLOYEE_ID = %s', (email, employee_id))
            cursor.execute('SELECT * FROM EMPLOYEE WHERE EMAIL = %s', (email,))
            user = cursor.fetchone()
            print("User:", user)                     # Debugging print statement
            if user:
                # password-check
                if int(employee_id) != user['EMPLOYEE_ID']:
                    print("Incorrect Employee Password")
                    message = "Incorrect Employee Password"
                else:
                    session['loggedin'] = "Employee"
                    session['userid'] = user['EMPLOYEE_ID']
                    session['name'] = user['FIRST_NAME']
                    session['email'] = user['EMAIL']
                    session['user_info'] = user
                    message = 'Logged in successfully !'

                    cursor.execute('SELECT COUNT(*) FROM VENUE WHERE EMPLOYEE_ID = %s', (employee_id,))
                    result = cursor.fetchone()
                    exists_in_venue = result['COUNT(*)'] > 0
                    session["Venue-in-charge"] = None
                    if exists_in_venue:
                        session["Venue-in-charge"] = True

                    cursor.execute('SELECT COUNCIL_NAME FROM COUNCIL WHERE EMPLOYEE_ID = %s', (employee_id,))
                    result = cursor.fetchone()
                    session["council_advisor"] = None
                    if result:
                        session["council_advisor"] = result['COUNCIL_NAME']

                    cursor.execute('SELECT CLUB_NAME FROM OVERSEER WHERE EMPLOYEE_ID = %s', (employee_id,))
                    result = cursor.fetchone()
                    session["club_overseer"] = None
                    if result:
                        session["club_overseer"] = result['CLUB_NAME']

                    # Page you want to navigate to if logged in successfully
                    # return render_template('employeeInfo.html', employeeInfo = user)
                    return redirect(url_for('employee_info'))
            else:
                print('User not found (incorrect email)')  # Debugging print statement
                message = 'User not found (incorrect email)'
                
        except Exception as e:
            print('Error:', e)  # Debugging print statement
            message = 'An error occurred during login.'
        finally:
            cursor.close()  # Always close the cursor

    ''' Log-in for Admin '''
    if request.method == 'POST' and 'email_admin' in request.form and 'password_admin' in request.form:
        email = request.form['email_admin']
        pw = request.form['password_admin']
        print("Received email:", email)              # Debugging print statement
        print("Received password:", pw)              # Debugging print statement
        
        try:
            if email == "admin@iitgn.ac.in":
                # password-check
                if pw != "manudb":
                    print("Incorrect Password")
                    message = "Incorrect Password"
                else:
                    session['loggedin'] = "Admin"
                    session['userid'] = 0
                    session['name'] = "admin"
                    session['email'] = "admin@iitgn.ac.in"
                    message = 'Logged in successfully !'

                    # Page you want to navigate to if logged in successfully
                    # return render_template('admin.html')
                    return redirect(url_for('admin_panel'))
            else:
                print('User not found (incorrect email)')  # Debugging print statement
                message = 'User not found (incorrect email)'
                
        except Exception as e:
            print('Error:', e)  # Debugging print statement
            message = 'An error occurred during login.'

    # we want to show the login page by default
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/studentInfo')
def student_info():
    # Check if the user is logged in, if not redirect to login page
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee":
        session["message"] = "Log-in as student to access Student-Info page."
        return redirect(url_for('login')) 

    return render_template('studentInfo.html', studentInfo = session['user_info'])

@app.route('/employeeInfo')
def employee_info():
    # Check if the user is logged in, if not redirect to login page
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Student":
        session["message"] = "Log-in as employee to access Employee-Info page."
        return redirect(url_for('login')) 

    return render_template('employeeInfo.html', employeeInfo = session['user_info'])

#this is used to display council details 
@app.route('/councils')
def council():
    try:
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute(' Select council.COUNCIL_NAME ,council.DESCRIPTION, count(COUNCIL_MEMBERS.ROLLS_NO) as "TOTAL_MEMBERS" from council , COUNCIL_MEMBERS where council.COUNCIL_NAME = COUNCIL_MEMBERS.COUNCIL_NAME group by COUNCIL_MEMBERS.COUNCIL_NAME ')
        councils = cursor.fetchall()
        print(councils)
        # session['councilName']= councils[0]['COUNCIL_NAME']
        # print(session['councilName'])

        cursor.execute('''
            SELECT clubs.CLUB_NAME, clubs.DESCRIPTION, COUNT(CLUB_MEMBERS.ROLLS_NO) AS "TOTAL_MEMBERS"
            FROM clubs
            JOIN CLUB_MEMBERS ON clubs.CLUB_NAME = CLUB_MEMBERS.CLUBS_NAME
            WHERE clubs.COUNCIL_NAME IS NULL
            GROUP BY clubs.CLUB_NAME, clubs.DESCRIPTION
        ''')
        hobby_groups = cursor.fetchall()
        print(hobby_groups)

        # Render the template with club information
        return render_template('councils.html', councils=councils, clubs=hobby_groups)
    except mysql.connector.Error as e:
        return f"Error retrieving club information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()


@app.route('/events', methods = ['GET'])
def events():
    try:
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute('select PLACE_AND_TIME.EVENTS_NAME, PLACE_AND_TIME.EDITIONS, PLACE_AND_TIME.DATE, EVENT.DESCRIPTION from PLACE_AND_TIME , EVENT where PLACE_AND_TIME.EVENTS_NAME = EVENT.EVENT_NAME and PLACE_AND_TIME.EDITIONS = EVENT.EDITION order by PLACE_AND_TIME.DATE DESC;')
        events = cursor.fetchall()
        # Render the template with club information
        return render_template('events.html',e=events)
    except mysql.connector.Error as e:
        return f"Error retrieving club information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()

@app.route('/event/<ev>/<ed>', methods = ['POST','GET'])
def event(ev,ed):
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor(dictionary=True)
    # Query to retrieve club information
    # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
    cursor.execute(f"select * from EVENT left join PLACE_AND_TIME on EVENTS_NAME = EVENT_NAME and EDITIONS = EDITION where EVENT_NAME= '{ev}' and EDITION= {ed};")
    event = cursor.fetchall()
        # Render the template with club information
    cursor.close()
    return render_template('event.html',event=event[0])
        # Close database connection
        
@app.route('/participate/<ev>/<ed>', methods = ['GET'])
def participate(ev,ed):
    return render_template('participation.html',ev=ev,ed=ed)

@app.route('/participation/<ev>/<ed>', methods = ['POST'])
def participation(ev,ed):
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor(dictionary=True)
    name = request.form['teamname']
    a=0
    if 'captain' in request.form.keys():
        a=1
    roll = request.form['roll']
    query = f"insert into PARTICIPATION values ('{ev}',{ed},{roll},'{name}',{a});"
    try:
        cursor.execute(query)
        message = "Participation added"
    except mysql.connector.errors.IntegrityError as e:
        message = e
    cursor.close()
    conn.close()
    return render_template('participation.html',ev=ev,ed=ed,message=message)

@app.route('/council_members/<council_name>')
def council_members(council_name):
        show_form = session.get("council_secretary") == council_name
        return render_template('council_members.html', council_name=council_name, show_form=show_form)

@app.route('/clubs/<club_name>')
def clubs(club_name):
        show_form = session.get("club_secretary") == club_name
        return render_template('clubs.html', club_name=club_name, show_form=show_form)

@app.route('/fetch_council_member/<council_name>', methods=['POST'])
def fetch_council_members(council_name):
    option = request.form['option']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    
    # Query to fetch data based on the selected option and council name
    if option == 'All member':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    elif option == 'General Members only':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'GENERAL MEMBER' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    elif option =='Coordinators':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'COORDINATOR' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    elif option == 'Secretary':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'SECRETARY' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    conn.close()
    return render_template('council_members.html', data=data, council_name=council_name)


@app.route('/update_council_members/<council_name>', methods=['POST'])
def update_council_members(council_name):
    option = request.form['option2']
    r = request.form['r']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    
    # Query to perform operations based on the selected option and council name
    if option == 'Add member':
        query = f"INSERT INTO COUNCIL_MEMBERS (COUNCIL_NAME, ROLLS_NO, POSITION) VALUES ('{council_name}', {r}, 'General Member');"
    elif option == 'Remove Member':
        query = f"DELETE FROM COUNCIL_MEMBERS WHERE ROLLS_NO = {r} AND POSITION = 'General Member' AND COUNCIL_NAME = '{council_name}';"
    elif option =='Add coordinator':
        query = f"INSERT INTO COUNCIL_MEMBERS (COUNCIL_NAME, ROLLS_NO, POSITION) VALUES ('{council_name}', {r}, 'Coordinator');"
    elif option == 'Remove coordinator':
        query = f"DELETE FROM COUNCIL_MEMBERS WHERE ROLLS_NO = {r} AND POSITION = 'Coordinator' AND COUNCIL_NAME = '{council_name}';"
    
    cursor.execute(query)
    conn.commit()
    conn.close()
    return render_template('council_members.html', council_name=council_name)

@app.route('/fetch_club_member/<club_name>', methods=['POST'])
def fetch_club_members(club_name):
    option = request.form['option']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    
    # Query to fetch data based on the selected option and club name
    if option == 'All member':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    elif option == 'General Members only':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.POSITION = 'GENERAL MEMBER' AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    elif option =='Coordinators':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.POSITION = 'COORDINATOR' AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    elif option == 'Secretary':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.POSITION = 'SECRETARY' AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    conn.close()
    return render_template('clubs.html', data=data, club_name=club_name)


@app.route('/update_club_members/<club_name>', methods=['POST'])
def update_club_members(club_name):
    option = request.form['option2']
    r = request.form['r']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    
    # Query to perform operations based on the selected option and club name
    if option == 'Add member':
        query = f"INSERT INTO CLUB_MEMBERS (CLUBS_NAME, ROLLS_NO, POSITION) VALUES ('{club_name}', {r}, 'General Member');"
    elif option == 'Remove Member':
        query = f"DELETE FROM CLUB_MEMBERS WHERE ROLLS_NO = {r} AND POSITION = 'General Member' AND CLUBS_NAME = '{club_name}';"
    elif option =='Add coordinator':
        query = f"INSERT INTO CLUB_MEMBERS (CLUBS_NAME, ROLLS_NO, POSITION) VALUES ('{club_name}', {r}, 'Coordinator');"
    elif option == 'Remove coordinator':
        query = f"DELETE FROM CLUB_MEMBERS WHERE ROLLS_NO = {r} AND POSITION = 'Coordinator' AND CLUBS_NAME = '{club_name}';"
    
    cursor.execute(query)
    conn.commit()
    conn.close()
    return render_template('clubs.html', club_name=club_name)

# Function to fetch all table names from MySQL
def get_table_names():
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

@app.route('/admin')
def admin_panel():
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Employee" or session["loggedin"] == "Student":
        session["message"] = "Only admins can access Admin page."
        return redirect(url_for('login')) 

    tables = get_table_names()
    print(tables)
    return render_template('admin.html', tables=tables)

@app.route('/view_table/<table_name>', methods=['GET', 'POST'])
def view_table(table_name):
    # Establish a connection to MySQL
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    # Fetch column names for the specified table
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    columns = [column[0] for column in cursor.fetchall()]
    
    cursor.execute(f"select * from {table_name}")
    data = cursor.fetchall()

    if request.method == 'POST':
        action = request.form['action']
        if action == 'insert':
        # Extract data from the form
            new_entry_values = [request.form[column] for column in columns]
            
            # Construct the SQL query to insert new entry
            placeholders = ', '.join(['%s'] * len(columns))
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Execute the insert query
            cursor = conn.cursor()
            cursor.execute(insert_query, new_entry_values)
            conn.commit()  # Commit the transaction
            
            cursor = conn.cursor()
            # Fetch data again after insertion
            cursor.execute(f"select * from {table_name}")
            data = cursor.fetchall()
            conn.commit()
    
        elif action =='delete':
            to_delete_values = [request.form[column] for column in columns]
            query=f"DELETE FROM {table_name} WHERE "
            print(query)

            for i in range(len(columns)):
                    if i==len(columns)-1:
                        if columns[i].isnumeric():
                            query+= f"{columns[i]} = {to_delete_values[i]}"
                        else:
                            query+= f"{columns[i]} = '{to_delete_values[i]}'"
                    else :
                        if columns[i].isnumeric():
                            query+= f"{columns[i]} = {to_delete_values[i]} and "
                        else:
                            query+= f"{columns[i]} = '{to_delete_values[i]}' and "
            query+=";"
            print(query)
            cursor.execute(query)  
            conn.commit()  
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            conn.commit()
        # Close the cursor and connection
        cursor.close()
        conn.close()

    # Render the HTML template with table name, column names, and data
    return render_template('view_table.html', table_name=table_name, columns=columns, data=data)

@app.route('/addEvent', methods=['GET','POST'])
def submit():
    if request.method == 'POST' and 'event_name' in request.form and 'edition' in request.form and 'mode_of_conduct' in request.form and 'description' in request.form and 'participation_form' in request.form and 'rulebook_link' in request.form and 'budget' in request.form and 'team_name' in request.form and 'team_captain' in request.form and 'filler_roll_no' in request.form and 'organizer_roll_no' in request.form and 'responsibility' in request.form and 'club_name' in request.form:
        event_name = request.form['event_name']
        edition = int(request.form['edition'])
        mode_of_conduct = request.form['mode_of_conduct']
        description = request.form['description']
        participation_form = request.form['participation_form']
        rulebook_link = request.form['rulebook_link']
        budget = float(request.form['budget'])

        team_name = request.form['team_name']
        team_captain = 1 if request.form['team_captain'] =='Yes' else 0
        filler_roll_no = int(request.form['filler_roll_no'])


        organizer_roll_no = int(request.form['organizer_roll_no'])
        responsibility= request.form['responsibility']

        club_name = request.form['club_name']

        venue = request.form['venue']
        date = request.form['date']
        print(type(date))
        

        start_time = request.form['start_time']
        end_time = request.form['end_time']
        print(type(start_time))
        print(end_time)


        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO event 
                (event_name, edition, mode_of_conduct, description, participation_form, rulebook_link, budget) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (event_name, edition, mode_of_conduct, description, participation_form, rulebook_link, budget))
            conn.commit()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO participation
                           (EVENTS_NAME,EDITIONS,ROLL_NO,TEAM_NAME,TEAM_CAPTAIN)
                           VALUES (%s, %s, %s,%s,%s)''',
                           (event_name,edition,filler_roll_no,team_name,team_captain))
            conn.commit()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO ORGANIZERS
                           VALUES (%s, %s, %s,%s)
                           ''',(event_name,edition,organizer_roll_no,responsibility))
            conn.commit()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO CONDUCTS
                            VALUES (%s, %s, %s)
                            ''',(club_name,event_name,edition))
            conn.commit()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO PLACE_AND_TIME 
                            VALUES (%s, %s,%s,%s,%s,%s)
                            ''',(venue,event_name,edition,date,start_time,end_time))    
            conn.commit()                       
            
            cursor.close()
            conn.close()
            message = 'Event added successfully!'
        except mysql.connector.Error as e:
            message = f"Error adding event: {e}"
    else:
        message = "Missing form fields"
   
    return render_template('addEvent.html', message=message)


@app.route('/equipment', methods=['GET'])
def equipment():
    return render_template('equipments.html', a=0)

@app.route('/equipmentaction', methods=['POST'])
def action():
    option = request.form.get('option')
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    # Query to fetch data based on the selected option
    if option == 'issue':
        query = f"select distinct club_name as NAME from EQUIPMENT;"
        a=1
    elif option == "view_history":
        query = f"select * from ISSUE where ROLL_NO = {session['userid']}"
        a=4
    else:
        query = f"select ISSUE.EQUIPMENT_ID, EQUIPMENT.NAME from ISSUE left join EQUIPMENT on ISSUE.EQUIPMENT_ID = EQUIPMENT.EQUIPMENT_ID where ROLL_NO = {session['userid']} and isnull(RETURN_TIME)"
        a=5
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return render_template('equipments.html', data=data, a=a)

@app.route('/selectclub', methods=['POST'])
def selectclub():
    option = request.form.get('option2')
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    # Query to fetch data based on the selected option
    print("picked",option)
    query = f"select NAME from EQUIPMENT where club_name = '{option}';"
    cursor.execute(query)
    eq = cursor.fetchall()
    conn.close()
    return render_template('equipments.html', equipments=eq, a=2)

@app.route('/issueequipment', methods=['POST'])
def issueequipment():
    option = request.form.get('option')
    sop = request.form['sop']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    # Query to fetch data based on the selected option
    
    query = f"select AVAILABILITY, QUANTITY, EQUIPMENT_ID from EQUIPMENT where NAME = '{option}';"
    cursor.execute(query)
    eq = cursor.fetchone()
    if (eq[0]==0):
        conn.close()
        flash("Not available at the moment")
        return render_template('equipments.html', a=0)
    
    else:
        id = eq[2]
        count = eq[1]

        query = f"insert into ISSUE values ({id},{session['userid']},'{datetime.now()}',NULL,'{sop}')"
        cursor.execute(query)

        query = f"select count(*) as c from ISSUE where EQUIPMENT_ID = {id} and RETURN_TIME = NULL"
        cursor.execute(query)
        eq = cursor.fetchone()
        if eq[0]==count:
            query = f"update EQUIPMENT set AVAILABILITY = 0 where EQUIPMENT_ID = {id}"
            cursor.execute(query)
        conn.commit()
        conn.close()
        flash("Equipment Issued")
        return render_template('equipments.html', a=0)

@app.route('/returnequipment', methods=['POST'])
def returnequipment():
    option = request.form.get('option')
    if (option is not None):
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        query = f"update ISSUE set RETURN_TIME = '{datetime.now()}' where ROLL_NO = {session['userid']} and EQUIPMENT_ID = {option} and isnull(RETURN_TIME)"
        cursor.execute(query)
        query = f"update EQUIPMENT set AVAILABILITY = 1 where EQUIPMENT_ID = {option}"
        cursor.execute(query)
        message="Equipment Returned"
        conn.commit()
        conn.close()
    else:
        message="Select a valid Equipment to return"
    return render_template('equipments.html', message=message, a=0)

if __name__ == "__main__":
    app.run(debug=True)
    