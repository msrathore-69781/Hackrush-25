from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import re

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Manvendra@04012002',
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
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        roll_no = request.form['password']
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM STUDENTS WHERE EMAIL = %s AND ROLL_NO = %s', (email, roll_no))
            user = cursor.fetchone()
            print("User:", user)  # Debugging print statement
            if user:
                session['loggedin'] = True
                session['userid'] = user['ROLL_NO']
                session['name'] = user['FIRST_NAME']
                session['email'] = user['EMAIL']
                message = 'Logged in successfully !'
                # Page you want to navigate to if logged in successfully
                return render_template('studentInfo.html', studentInfo = user)
            else:
                print('User not found or incorrect email / password!')  # Debugging print statement
        except Exception as e:
            print('Error:', e)  # Debugging print statement
            message = 'An error occurred during login.'
        finally:
            cursor.close()  # Always close the cursor


# we want to show the login page by default
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

#this is used to display council details 
@app.route('/councils')
def council():
    try:
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute(' Select council.COUNCIL_NAME ,council.DESCRIPTION, count(COUNCIL_MEMBERS.ROLLS_NO) as "TOTAL_MEMBERS" from council ,  COUNCIL_MEMBERS where council.COUNCIL_NAME = COUNCIL_MEMBERS.COUNCIL_NAME group by COUNCIL_MEMBERS.COUNCIL_NAME ')
        councils = cursor.fetchall()
        print(councils)
        session['councilName']= councils[0]['COUNCIL_NAME']
        print(session['councilName'])
        # Render the template with club information
        return render_template('councils.html', councils=councils)
    except mysql.connector.Error as e:
        return f"Error retrieving club information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()

@app.route('/events', methods = ['POST','GET'])
def events():
    try:
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute('select PLACE_AND_TIME.EVENTS_NAME, PLACE_AND_TIME.DATE, EVENT.DESCRIPTION from PLACE_AND_TIME , EVENT where PLACE_AND_TIME.EVENTS_NAME = EVENT.EVENT_NAME order by PLACE_AND_TIME.DATE DESC;')
        events = cursor.fetchall()
        # Render the template with club information
        return render_template('events.html',e=events)
    except mysql.connector.Error as e:
        return f"Error retrieving club information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()

@app.route('/event', methods = ['POST','GET'])
def event(event):
    # event_name = request.args.get('event_name')
    # print(event_name)
    conn = mysql.connector.connect(**mysql_config)
    try: 
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute('select * from EVENT where EVENT_NAME= %s', ('{event}'))
        event = cursor.fetchall()
        print(event)
            # Render the template with club information
        return render_template('event.html')
    except mysql.connector.Error as e:
        return f"Error retrieving event information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()
        
        
@app.route('/council_members')
def council_members():
        return render_template('council_members.html')

@app.route('/fetch_member', methods=['POST'])
def fetch_members():
    option = request.form['option']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    c= session['councilName']
    # Query to fetch data based on the selected option
    if option == 'All member':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO and COUNCIL_MEMBERS.COUNCIL_NAME = '{c}';"
    elif option == 'General Members only':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'GENERAL MEMBER' and COUNCIL_MEMBERS.COUNCIL_NAME = '{c}';"
    elif option =='Coordinators':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'COORDINATOR' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{c}';"
    elif option == 'Secretary':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'SECRETARY' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{c}';"
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    conn.close()
    return render_template('council_members.html', data=data)

@app.route('/equipment', methods=['POST','GET'])
def equipment():
    return render_template('equipments.html')


@app.route('/equipmentaction', methods=['POST','GET'])
def action():
    if request.method == 'POST':
        option = request.form['option']
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        # Query to fetch data based on the selected option
        if option == 'issue':
            query = f"select unique(CLUB_NAME) from OWNS;"
        cursor.execute(query)
        clubs = cursor.fetchall()
        conn.close()
        print(clubs)
        return render_template('equipments.html', clubs=clubs)
    return render_template('equipments.html')

@app.route('/selectclub', methods=['POST'])
def selectclub():
    option = request.form['option']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    # Query to fetch data based on the selected option
    query = f"select NAME from EQUIPMENT right join OWNS on OWNS.EQUIPMENT_ID = EQUIPMENT.EQUIPMENT_ID where OWNS.CLUB_NAME = {option};"
    cursor.execute(query)
    eq = cursor.fetchall()
    conn.close()
    return render_template('equipments.html', eq=eq)

@app.route('/issueequipment', methods=['POST'])
def issueequipment():
    option = request.form['option']
    sop = request.form['sop']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    # Query to fetch data based on the selected option
    
    query = f"select AVAILABILTY, QUANTITY, EQUIPMENT_ID from EQUIPMENT where NAME = {option};"
    cursor.execute(query)
    eq = cursor.fetchone()
    if (eq['AVAILABILITY']==0):
        conn.close()
        return "Not available at the moment"
    
    id = eq['EQUIPMENT_ID']
    count = eq['QUANTITY']

    query = f"insert into ISSUE ({id},{session['userid']},{datetime.now()},{None},{sop})"
    cursor.execute(query)

    query = f"select count(*) as c from ISSUE where EQUIPMENT_ID = {id} and RETURN_TIME = {None}"
    cursor.execute(query)
    eq = cursor.fetchone()
    if eq['c']==count:
        query = f"update EQUIPMENT set AVAILABILITY = 0 where EQUIPMENT_ID = {id}"
        cursor.execute(query)
    conn.close()
    return "Successfuly issued"



if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)
