from flask import Flask, render_template, request, redirect, url_for, session, flash , jsonify, redirect
import mysql.connector
# import re
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from oauthlib.oauth2 import WebApplicationClient

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Your_Password',    #Enter ur password for root
    'database': 'CLUB_MS'
}
try:
    conn = mysql.connector.connect(**mysql_config)
    print("Connected to MySQL database successfully!")
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL database: {e}")
conn = mysql.connector.connect(**mysql_config)


# app.config['SERVER_NAME'] = 'localhost:5000'
oauth = OAuth(app)
 
@app.route('/google/')
def google():
   
    # Google Oauth Config
    # Get client_id and client_secret from environment variables
    # For developement purpose you can directly put it here inside double quotes
    GOOGLE_CLIENT_ID = "134133495392-9i6jrrg4abg2q4qlmhptcl2t9nfclmj9.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
     
    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
 
@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    
    nonce = request.args.get('nonce')  # Retrieve the nonce from the request
    user = oauth.google.parse_id_token(token, nonce=nonce)  

    email = user.get('email')  # Retrieve email from user info
    session['email'] = email  # Store email in session

    print(" Google User ", user)
    return redirect('/register')

@app.route('/', methods=['GET', 'POST'])
def login():
    # message = None
    if "message" in session:
        message = session["message"]
    else:
        message = None
    # session["message"] = None

    session.clear()

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
                query = "SELECT PASSWORD FROM PASSWORDS WHERE EMAIL = %s"
                cursor.execute(query, (email,))
                password = cursor.fetchone()

                # if roll_no != email.split("@")[0]:
                if int(roll_no) != password:
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
                query = "SELECT PASSWORD FROM PASSWORDS WHERE EMAIL = %s"
                cursor.execute(query, (email,))
                password = cursor.fetchone()

                # if int(employee_id) != user['EMPLOYEE_ID']:
                if int(employee_id) != password:
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

    ''' Log-in for Admin '''
    if request.method == 'POST' and 'email_admin' in request.form and 'password_admin' in request.form:
        email = request.form['email_admin']
        pw = request.form['password_admin']
        print("Received email:", email)              # Debugging print statement
        print("Received password:", pw)              # Debugging print statement
        
        cursor = conn.cursor(dictionary=True)
        query = "SELECT ROLE, PASSWORD FROM PASSWORDS WHERE EMAIL = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        try:
            # if email == "admin@iitgn.ac.in":
                # password-check
                # if pw != "manudb":

            if result:
                print(result)
                role, stored_password = result["ROLE"], result["PASSWORD"]
                print(role, stored_password)  # Debugging print statement

                if role != 'Admin':
                    message = "You do not have admin privileges"
                    print("This user is not an admin.")

                else:
                    if pw != stored_password:
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

        finally:
            cursor.close()

    # we want to show the login page by default
    return render_template('login.html', message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    email = session.get('email')  # Retrieve email from session
    print(email)

    if email is None:
        return render_template('login.html', message = "Sign-in your with your IITGN email id to register.")

    ''' Register for Students '''
    if request.method == 'POST' and 'userID_student' in request.form and 'password_student' in request.form and 'name_student' in request.form:
        password = request.form['password_student']
        roll_no = request.form['userID_student'] 
        first_name = request.form['name_student']

        if not roll_no.isnumeric():
            return render_template("registration.html", email=email, message="Roll number should be numeric.")
        if len(roll_no) != 7:
            return render_template("registration.html", email=email, message="Roll number should be 7 digits long.")
        if int(roll_no)<2000000:
            return render_template("registration.html", email=email, message="Invalid Roll number. Should be greater than 2000000.")
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM STUDENTS WHERE ROLL_NO = %s', (roll_no,))
            user = cursor.fetchone()
            if user:
                return render_template("registration.html", email=email, message="User already exists.")
            else:
                # Constant values for the fields
                contact_no = '1234567890'
                middle_name = None
                last_name = None
                street = '123 Street'
                city = 'City'
                state = 'State'
                pincode = '123456'
                dob = '2000-01-01'
                age = 21
                programme = 'BTech'
                discipline = 'CSE'
                year = '2022'

                cursor.execute('INSERT INTO STUDENTS (ROLL_NO, EMAIL, CONTACT_NO, FIRST_NAME, MIDDLE_NAME, LAST_NAME, STREET, CITY, STATE, PINCODE, DATE_OF_BIRTH, AGE, PROGRAMME, DISCIPLINE, YEAR) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (roll_no, email, contact_no, first_name, middle_name, last_name, street, city, state, pincode, dob, age, programme, discipline, year))
                cursor.execute('INSERT INTO PASSWORDS (EMAIL, PASSWORD, ROLE) VALUES (%s, %s, %s)', (email, password, 'Student'))
                conn.commit()
                return redirect(url_for('login'))
            
        except Exception as e:
            print('Error:', e)
            return render_template("registration.html", email=email, message=e)
        finally:
            cursor.close()

    ''' Register for Employees '''
    if request.method == 'POST' and 'userID_employee' in request.form and 'password_employee' in request.form and 'name_employee' in request.form:
        password = request.form['password_employee']
        employee_id = request.form['userID_employee'] 
        first_name = request.form['name_employee']

        if not employee_id.isnumeric():
            return render_template("registration.html", email=email, message="Employee ID should be numeric.")
        if int(employee_id)<1000:
            return render_template("registration.html", email=email, message="Invalid Employee ID. Should be less than 1000.")
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM EMPLOYEES WHERE EMPLOYEE_ID = %s', (employee_id,))
            user = cursor.fetchone()
            if user:
                return render_template("registration.html", email=email, message="User already exists.")
            else:
                # Constant values for the fields
                middle_name = None
                last_name = None
                phone_number = '1234567890'
                department = 'Computer Science'
                designation = 'PROFESSOR'

                cursor.execute('INSERT INTO EMPLOYEES (EMPLOYEE_ID, EMAIL, FIRST_NAME, MIDDLE_NAME, LAST_NAME, PHONE_NUMBER, DEPARTMENT, DESIGNATION) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (employee_id, email, first_name, middle_name, last_name, phone_number, department, designation))
                cursor.execute('INSERT INTO PASSWORDS (EMAIL, PASSWORD, ROLE) VALUES (%s, %s, %s)', (email, password, 'Employee'))
                conn.commit()
                return redirect(url_for('login'))
            
        except Exception as e:
            print('Error:', e)
            return render_template("registration.html", email=email, message=e)
        finally:
            cursor.close()

    return render_template("registration.html", email=email)

@app.route('/logout')
@app.route('/council_members/logout')
@app.route('/clubs/logout')
@app.route('/fetch_club_member/logout')
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
    
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor(dictionary=True)
    employee_id = session['userid']
    
    records_v = None
    if session["Venue-in-charge"]:
        query = """
            SELECT pt.*
            FROM PLACE_AND_TIME pt
            JOIN VENUE v ON pt.name = v.address
            WHERE v.employee_id = %s
        """
        cursor.execute(query, (employee_id,))
        records_v = cursor.fetchall()

        # Convert datetime.timedelta objects to strings
        for record in records_v:
            record['START_TIME'] = str(record['START_TIME'])
            record['END_TIME'] = str(record['END_TIME'])

        print(records_v)

    query = """
            SELECT a.EVENT_NAME, a.EDITION, e.BUDGET, a.APPROVAL_STATUS
            FROM Approval a
            JOIN Event e ON a.EVENT_NAME = e.EVENT_NAME AND a.EDITION = e.EDITION
            WHERE a.EMPLOYEE_ID = %s
        """
    cursor.execute(query, (employee_id,))
    records_b = cursor.fetchall()
    print(records_b)

    # Store the modified records in the session
    session["venues"] = records_v

    return render_template('employeeInfo.html', employeeInfo = session['user_info'], venues=session["venues"], events=records_b)

@app.route('/approval_update', methods=['POST'])
def approval_update():
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))

    # Get the selected event status and approval status from the form
    event_status = request.form.get('event_status')
    status = request.form.get('status')

    # Split the event status into event name and edition
    event_name, edition = event_status.split(',')

    # Update the approval status in the database
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    
    try:
        query = """
            UPDATE Approval
            SET APPROVAL_STATUS = %s
            WHERE EVENT_NAME = %s AND EDITION = %s
        """
        cursor.execute(query, (status, event_name, edition))
        conn.commit()

        query = """
                SELECT a.EVENT_NAME, a.EDITION, e.BUDGET, a.APPROVAL_STATUS
                FROM Approval a
                JOIN Event e ON a.EVENT_NAME = e.EVENT_NAME AND a.EDITION = e.EDITION
                WHERE a.EMPLOYEE_ID = %s
            """
        cursor.execute(query, (session['userid'],))
        records_b = cursor.fetchall()
        print(records_b)
        
        conn.close()

        # Redirect back to the employee info page
        return redirect(url_for('employee_info', employeeInfo = session['user_info'], venues=session["venues"], events=records_b))
    except mysql.connector.Error as e:
        message=f"Error retrieving information: {e}"
        return render_template(url_for('employee_info', employeeInfo = session['user_info'], venues=session["venues"], events=[], message=message))
        

#this is used to display council details 
@app.route('/councils')
def council():

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] != "Student" and session["loggedin"] != "Employee":
        session["message"] = "Log-in as student or employee to view."
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**mysql_config)
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
        message=f"Error retrieving information: {e}"
        return render_template('councils.html', councils=[], clubs=[], message=message)
    finally:
        # Close database connection
        cursor.close()
        conn.close()

@app.route('/fetch_council_member/events', methods = ['GET'])
@app.route('/events', methods = ['GET'])
def events():

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee":
        session["message"] = "Log-in as student to access Events page."
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute(f"select PLACE_AND_TIME.EVENTS_NAME, PLACE_AND_TIME.EDITIONS, PLACE_AND_TIME.DATE, EVENT.DESCRIPTION from PLACE_AND_TIME , EVENT where PLACE_AND_TIME.EVENTS_NAME = EVENT.EVENT_NAME and PLACE_AND_TIME.EDITIONS = EVENT.EDITION and DATE > '{datetime.now().date()}' order by PLACE_AND_TIME.DATE DESC;")
        events = cursor.fetchall()
        # Render the template with club information
        return render_template('events.html',e=events)
    except mysql.connector.Error as e:
        message=f"Error retrieving information: {e}"
        render_template('events.html',e=[],message=message)
    finally:
        # Close database connection
        cursor.close()
        conn.close()

@app.route('/event/<ev>/<ed>', methods = ['POST','GET'])
def event(ev,ed):

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee":
        session["message"] = "Log-in as student to access Events page."
        return redirect(url_for('login'))

    try:

        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute(f"select * from EVENT left join PLACE_AND_TIME on EVENTS_NAME = EVENT_NAME and EDITIONS = EDITION where EVENT_NAME= '{ev}' and EDITION= {ed};")
        event = cursor.fetchall()
            # Render the template with club information
        cursor.close()
        return render_template('event.html',event=event[0])
    
    except mysql.connector.Error as e:
        message=f"Error retrieving information: {e}"
        render_template('events.html',message=message)
        
@app.route('/participate/<ev>/<ed>', methods = ['GET'])
def participate(ev,ed):

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee":
        session["message"] = "Log-in as student to participate."
        return redirect(url_for('login'))

    if (ed[0].isdigit()):
        return render_template('participation.html',ev=ev,ed=ed)
    else:
        return redirect(url_for('event',ev=ev,ed=ed))
    

@app.route('/participation/<ev>/<ed>', methods = ['GET','POST'])
def participation(ev,ed):

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee":
        session["message"] = "Log-in as student to participate."
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor(dictionary=True)
    name = request.form['teamname']
   
    # Get the list of roll values from the form
    captain = request.form['Captain']
    message = None

    try:
        cursor.execute(f"INSERT INTO PARTICIPATION VALUES ('{ev}', {ed}, {captain}, '{name}', {1});")
        conn.commit()
        message = "Participation added"
    except mysql.connector.Error as e:
        message = e
        return render_template('participation.html',ev=ev,ed=ed,message=message)
   
    if request.form.getlist('roll'):
        rolls = request.form.getlist('roll')

        # Iterate over the rolls and insert them into the PARTICIPATION table
        for roll in rolls:
            query = f"INSERT INTO PARTICIPATION VALUES ('{ev}', {ed}, {roll}, '{name}', {0});"
            try:
                cursor.execute(query)
                conn.commit()
                message = "Participation added"
            except mysql.connector.Error as e:
                message = e
                return render_template('participation.html',ev=ev,ed=ed,message=message)

    cursor.close()
    conn.close()
    return render_template('participation.html',ev=ev,ed=ed,message=message)

@app.route('/council_members/<council_name>')
def council_members(council_name):

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] != "Student" and session["loggedin"] != "Employee":
        session["message"] = "Log-in as student or employee to view."
        return redirect(url_for('login'))

    show_form = session.get("council_secretary") == council_name
    print(show_form)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
        SELECT clubs.CLUB_NAME, clubs.DESCRIPTION, COUNT(CLUB_MEMBERS.ROLLS_NO) AS "TOTAL_MEMBERS"
        FROM clubs
        JOIN CLUB_MEMBERS ON clubs.CLUB_NAME = CLUB_MEMBERS.CLUBS_NAME
        WHERE clubs.COUNCIL_NAME = %s
        GROUP BY clubs.CLUB_NAME, clubs.DESCRIPTION;''',(council_name,))
        clubs = cursor.fetchall()
        return render_template('council_members.html', council_name=council_name, show_form=show_form, clubs=clubs)

    except mysql.connector.Error as e:
        message=f"Error retrieving info {e}"
        return render_template('council_members.html', council_name=council_name, show_form=show_form, clubs=clubs)


@app.route('/clubs/<club_name>')
def clubs(club_name):

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] != "Student" and session["loggedin"] != "Employee":
        session["message"] = "Log-in as student or employee to view."
        return redirect(url_for('login'))

    show_form = session.get("club_secretary") == club_name
    print(show_form)

    event_info = None
    if show_form:
        try:
            conn = mysql.connector.connect(**mysql_config)
            cursor = conn.cursor(dictionary=True)
            
            query = '''
            SELECT
                e.EVENT_NAME,
                e.EDITION,
                e.BUDGET,
                a.APPROVAL_STATUS,
                a.EMPLOYEE_ID  AS Overseer,
                o.ROLL_NO AS Event_Lead
            FROM
                event e
            INNER JOIN
                conducts c ON e.EVENT_NAME = c.EVENTS_NAME AND e.EDITION = c.EDITIONS
            LEFT JOIN
                approval a ON e.EVENT_NAME = a.EVENT_NAME AND e.EDITION = a.EDITION
            LEFT JOIN
                organizers o ON e.EVENT_NAME = o.EVENTS_NAME AND e.EDITION = o.EDITIONS
            WHERE
                c.CLUB_NAME = %s
                AND o.RESPONSIBILITY = 'Event Lead'
            '''

            cursor.execute(query, (club_name,))
            event_info = cursor.fetchall()
            print(event_info)

        except mysql.connector.Error as e:
            message= f"Error retrieving club information: {e}"
            return render_template('clubs.html', club_name=club_name, show_form=show_form, event_info=[],message=message)
        finally:
            # Close database connection
            cursor.close()
            conn.close()

    return render_template('clubs.html', club_name=club_name, show_form=show_form, event_info=event_info)

@app.route('/fetch_council_member/<council_name>', methods=['POST'])
def fetch_council_members(council_name):

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] != "Student" and session["loggedin"] != "Employee":
        session["message"] = "Log-in as student or employee to view."
        return redirect(url_for('login'))

    option = request.form['option']
    show_form = session.get("council_secretary") == council_name
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor(dictionary=True)
    
    # Query to fetch data based on the selected option and council name
    if option == 'All member':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    elif option == 'General Members only':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'GENERAL MEMBER' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    elif option =='Coordinators':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'COORDINATOR' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    elif option == 'Secretary':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION FROM STUDENTS, COUNCIL_MEMBERS WHERE COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'SECRETARY' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council_name}';"
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.execute('''
            SELECT clubs.CLUB_NAME, clubs.DESCRIPTION, COUNT(CLUB_MEMBERS.ROLLS_NO) AS "TOTAL_MEMBERS"
            FROM clubs
            JOIN CLUB_MEMBERS ON clubs.CLUB_NAME = CLUB_MEMBERS.CLUBS_NAME
            WHERE clubs.COUNCIL_NAME = %s
            GROUP BY clubs.CLUB_NAME, clubs.DESCRIPTION;''',(council_name,))
        clubs = cursor.fetchall()
        conn.close()
        return render_template('council_members.html', data=data, council_name=council_name, show_form=show_form, clubs=clubs)
    except mysql.connector.Error as e:
        message=f"Error retrieving information: {e}"
        render_template('council_members.html', data=[], council_name=council_name, show_form=show_form, clubs=[])


@app.route('/update_council_members/<council_name>', methods=['POST'])
def update_council_members(council_name):
    
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] != "Student" and session["loggedin"] != "Employee":
        session["message"] = "Log-in as student or employee to view."
        return redirect(url_for('login'))
    
    option = request.form['option2']
    r = request.form['r']
    show_form = session.get("council_secretary") == council_name
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor(dictionary=True)
    
    # Query to perform operations based on the selected option and council name
    if option == 'Add member':
        query = f"INSERT INTO COUNCIL_MEMBERS (COUNCIL_NAME, ROLLS_NO, POSITION) VALUES ('{council_name}', {r}, 'General Member');"
    elif option == 'Remove Member':
        query = f"DELETE FROM COUNCIL_MEMBERS WHERE ROLLS_NO = {r} AND POSITION = 'General Member' AND COUNCIL_NAME = '{council_name}';"
    elif option =='Add coordinator':
        query = f"INSERT INTO COUNCIL_MEMBERS (COUNCIL_NAME, ROLLS_NO, POSITION) VALUES ('{council_name}', {r}, 'Coordinator');"
    elif option == 'Remove coordinator':
        query = f"DELETE FROM COUNCIL_MEMBERS WHERE ROLLS_NO = {r} AND POSITION = 'Coordinator' AND COUNCIL_NAME = '{council_name}';"
    
    try:
        cursor.execute(query)
        conn.commit()
        cursor.execute('''
            SELECT clubs.CLUB_NAME, clubs.DESCRIPTION, COUNT(CLUB_MEMBERS.ROLLS_NO) AS "TOTAL_MEMBERS"
            FROM clubs
            JOIN CLUB_MEMBERS ON clubs.CLUB_NAME = CLUB_MEMBERS.CLUBS_NAME
            WHERE clubs.COUNCIL_NAME = %s
            GROUP BY clubs.CLUB_NAME, clubs.DESCRIPTION;''',(council_name,))
        clubs = cursor.fetchall()
        conn.close()
        return render_template('council_members.html', council_name=council_name, show_form=show_form, clubs=clubs)

    except mysql.connector.IntegrityError as e:
        message=f"Error : {e}"
        render_template('council_members.html', council_name=council_name, show_form=show_form, clubs=[], message=message)

@app.route('/fetch_club_member/<club_name>', methods=['POST'])
def fetch_club_members(club_name):
    
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] != "Student" and session["loggedin"] != "Employee":
        session["message"] = "Log-in as student or employee to view."
        return redirect(url_for('login'))
    
    show_form = session.get("club_secretary") == club_name
    
    event_info = None
    if show_form:
        try:
            conn_ = mysql.connector.connect(**mysql_config)
            cursor_ = conn_.cursor(dictionary=True)
            
            query = '''
            SELECT
                e.EVENT_NAME,
                e.EDITION,
                e.BUDGET,
                a.APPROVAL_STATUS,
                a.EMPLOYEE_ID  AS Overseer,
                o.ROLL_NO AS Event_Lead
            FROM
                event e
            INNER JOIN
                conducts c ON e.EVENT_NAME = c.EVENTS_NAME AND e.EDITION = c.EDITIONS
            LEFT JOIN
                approval a ON e.EVENT_NAME = a.EVENT_NAME AND e.EDITION = a.EDITION
            LEFT JOIN
                organizers o ON e.EVENT_NAME = o.EVENTS_NAME AND e.EDITION = o.EDITIONS
            WHERE
                c.CLUB_NAME = %s
                AND o.RESPONSIBILITY = 'Event Lead'
            '''

            cursor_.execute(query, (club_name,))
            event_info = cursor_.fetchall()
            print(event_info)

        except mysql.connector.Error as e:
            message=f"Error : {e}"
            return render_template('clubs.html', data=[], club_name=club_name, show_form=show_form, event_info=[], message=message)
        finally:
            # Close database connection
            cursor_.close()
            conn_.close()
    
    option = request.form['option']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    query=""
    # Query to fetch data based on the selected option and club name
    if option == 'All member':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    elif option == 'General Members only':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.POSITION = 'GENERAL MEMBER' AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    elif option =='Coordinators':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.POSITION = 'COORDINATOR' AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    elif option == 'Secretary':
        query = f"SELECT STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, CLUB_MEMBERS.POSITION FROM STUDENTS, CLUB_MEMBERS WHERE CLUB_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND CLUB_MEMBERS.POSITION = 'SECRETARY' AND CLUB_MEMBERS.CLUBS_NAME = '{club_name}';"
    
    try:
        cursor.execute(query)
        data = cursor.fetchall()
    except mysql.connector.Error as e:
            message=f"Error : {e}"
            render_template('clubs.html', data=[], club_name=club_name, show_form=show_form, event_info=event_info)
    print(data)
    conn.close()
    return render_template('clubs.html', data=data, club_name=club_name, show_form=show_form, event_info=event_info)


@app.route('/update_club_members/<club_name>', methods=['POST'])
def update_club_members(club_name):
    
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] != "Student" and session["loggedin"] != "Employee":
        session["message"] = "Log-in as student or employee to view."
        return redirect(url_for('login'))
    
    show_form = session.get("club_secretary") == club_name

    event_info = None
    if show_form:
        try:
            conn_ = mysql.connector.connect(**mysql_config)
            cursor_ = conn_.cursor(dictionary=True)
            
            query = '''
            SELECT
                e.EVENT_NAME,
                e.EDITION,
                e.BUDGET,
                a.APPROVAL_STATUS,
                a.EMPLOYEE_ID  AS Overseer,
                o.ROLL_NO AS Event_Lead
            FROM
                event e
            INNER JOIN
                conducts c ON e.EVENT_NAME = c.EVENTS_NAME AND e.EDITION = c.EDITIONS
            LEFT JOIN
                approval a ON e.EVENT_NAME = a.EVENT_NAME AND e.EDITION = a.EDITION
            LEFT JOIN
                organizers o ON e.EVENT_NAME = o.EVENTS_NAME AND e.EDITION = o.EDITIONS
            WHERE
                c.CLUB_NAME = %s
                AND o.RESPONSIBILITY = 'Event Lead'
            '''

            cursor_.execute(query, (club_name,))
            event_info = cursor_.fetchall()
            print(event_info)

        except mysql.connector.Error as e:
            message=f"Error : {e}"
            render_template('clubs.html', club_name=club_name, show_form=show_form, event_info=[], message=message)
        finally:
            # Close database connection
            cursor_.close()
            conn_.close()

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
    
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
    except mysql.connector.Error as e:
        message=f"Error : {e}"
        render_template('clubs.html', club_name=club_name, show_form=show_form, event_info=event_info, message=message)
    return render_template('clubs.html', club_name=club_name, show_form=show_form, event_info=event_info)

# Function to fetch all table names from MySQL
def get_table_names():
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        # print(tables)
        # tables.remove("passwords")

        cursor.close()
        conn.close()
        return tables
    except mysql.connector.Error as e:
        message=f"Error : {e}"
        return message
    

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
    if type(tables)==str:
        return render_template('admin.html', tables=[],message=tables)
    print(tables)
    return render_template('admin.html', tables=tables)

@app.route('/view_table/<table_name>', methods=['GET', 'POST'])
def view_table(table_name):

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Employee" or session["loggedin"] == "Student":
        session["message"] = "Only admins can access this page."
        return redirect(url_for('login')) 

    # Establish a connection to MySQL
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    if table_name == "passwords":
        return render_template('login.html', message = "You don't have authority to view the data.\nRe-login to continue.")

    try:
        # Fetch column names for the specified table
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in cursor.fetchall()]
        
        cursor.execute(f"select * from {table_name}")
        data = cursor.fetchall()
    except:
        return render_template('admin.html', message = "Requested table does not exist.")

    if request.method == 'POST':
        action = request.form['action']
        try:
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
                message = "Inserted"
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
                message = "Deleted"
                conn.commit()  
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                conn.commit()

            elif action == 'rename':
                new_table_name = request.form['new_table_name']
                cursor=conn.cursor()
                cursor.execute(f"RENAME TABLE {table_name} TO {new_table_name}")
                message = "Renamed"
                conn.commit()
                return redirect('/view_table/' + new_table_name)
            # Close the cursor and connection
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            message = f"Error: {e}"
    # Render the HTML template with table name, column names, and data
        return render_template('view_table.html', table_name=table_name, columns=columns, data=data,message=message)
    else:
        return render_template('view_table.html', table_name=table_name, columns=columns, data=data)

@app.route('/addEvents', methods=['GET'])
def addEvents():
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee" or session["club_secretary"] == None:
        session["message"] = "Only Club Secretary can add an event."
        return redirect(url_for('login'))
    
    return render_template('addEvent.html')

@app.route('/addEvent', methods=['POST'])
def submit():
    if request.method == 'POST' and request.form['event_name'] and request.form['edition'] and request.form['mode_of_conduct'] and request.form['description'] and request.form['rulebook_link'] and request.form['budget'] and request.form['club_name'] and request.form['event_lead_roll_no'] and request.form['venue'] and request.form['team_member']:
        event_name = request.form['event_name']
        edition = int(request.form['edition'])
        employee_id = int(request.form['employee_id'])
        mode_of_conduct = request.form['mode_of_conduct']
        description = request.form['description']
        rulebook_link = request.form['rulebook_link']
        budget = float(request.form['budget'])

        event_lead_roll_no = int(request.form['event_lead_roll_no'])
        team_members = request.form.getlist('team_member')

        club_name = request.form['club_name']

        if mode_of_conduct == 'Offline':
            venue = request.form['venue']
            date = request.form['date']
            print(type(date))
            
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            print(type(start_time))
            print(end_time)
        else:
            venue = None
            date=None
            start_time = None
            end_time = None 


        try:
            cursor = conn.cursor()
            print(1)
            cursor.execute('''
                INSERT INTO event 
                (event_name, edition, mode_of_conduct, description, rulebook_link, budget) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (event_name, edition, mode_of_conduct, description, rulebook_link, budget))
            conn.commit()
            print(2)

            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ORGANIZERS
                           VALUES (%s, %s, %s,%s)
                           ''',(event_name,edition,event_lead_roll_no,'Event Lead'))
            conn.commit()
            cursor = conn.cursor()
            for team_member in team_members:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ORGANIZERS
                            VALUES (%s, %s, %s,%s)
                            ''',(event_name,edition,int(team_member),'Team Member'))
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
            cursor=conn.cursor()
            cursor.execute('''
                INSERT INTO approval 
                            VALUES (%s, %s,%s,%s)
                            ''',(event_name,edition,employee_id,'pending'))    
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
    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee":
        session["message"] = "Log-in as student to access Equipments page."
        return redirect(url_for('login'))
    
    return render_template('equipments.html', a=0)

@app.route('/equipmentaction', methods=['POST'])
def action():

    if 'loggedin' not in session:
        session["message"] = "Please log in first."
        return redirect(url_for('login'))
    
    print(session["loggedin"])
    
    if session["loggedin"] == "Admin" or session["loggedin"] == "Employee":
        session["message"] = "Log-in as student to access this page."
        return redirect(url_for('login'))

    option = request.form.get('option')
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    query=''
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
        message = "Not available at the moment"
        return render_template('equipments.html', message=message, a=0)
    
    else:
        id = eq[2]
        count = eq[1]

        query = f"insert into ISSUE values ({id},{session['userid']},'{datetime.now()}',NULL,'{sop}')"
        cursor.execute(query)

        query = f"select count(*) as c from ISSUE where EQUIPMENT_ID = {id} and RETURN_TIME IS NULL"
        cursor.execute(query)
        eq = cursor.fetchone()
        if eq[0]==count:
            query = f"update EQUIPMENT set AVAILABILITY = 0 where EQUIPMENT_ID = {id}"
            cursor.execute(query)
        conn.commit()
        conn.close()
        message = "Equipment Issued"
        return render_template('equipments.html', message=message, a=0)

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
