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
        print("Received email:", email)  # Debugging print statement
        print("Received roll number:", roll_no)  # Debugging print statement
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
        return render_template('events.html', events=events)
    except mysql.connector.Error as e:
        return f"Error retrieving club information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()

@app.route('/event', methods = ['POST','GET'])
def event():
    # event_name = request.args.get('event_name')
    # print(event_name)
    try: 
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute('select * from EVENT;')
        event = cursor.fetchall()
        print(event)
            # Render the template with club information
        return render_template('event.html', events=event)
    except mysql.connector.Error as e:
        return f"Error retrieving event information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()
        
        
# # Dummy Data (for demonstration)
# all_members = [
#     {"Name": "Taylor Swift", "Role": "Member", "Email": "swifttailor@iign.ac.in"},
#     # Add more member data as needed
# ]

# # Function to Fetch Members from Database
# def fetch_members_from_database(selected_value):
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor(dictionary=True)

#     # Query database based on selected value
#     if selected_value == 'All member':
#         cursor.execute("SELECT * FROM COUNCIL_MEMBERS")
#     elif selected_value == 'General Members only':
#         cursor.execute("SELECT * FROM COUNCIL_MEMBERS WHERE POSITION = 'GENERAL MEMBER'")
#     elif selected_value == 'Secretary':
#         cursor.execute("SELECT * FROM COUNCIL_MEMBERS WHERE POSITION = 'SECRETARY'")
#     elif selected_value == 'Coordinators':
#         cursor.execute("SELECT * FROM COUNCIL_MEMBERS WHERE POSITION ='COORDINATOR''")

#     members = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return members

# # Route to Fetch Members and Render Template
# @app.route('/council_members', methods=['POST'])
# def fetch_members():
#     selected_option = request.form['option']
#     fetched_members = fetch_members_from_database(selected_option)
#     return render_template('council_members.html', members=fetched_members)

# def get_data_from_mysql(option):
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     query = f"SELECT * FROM COUNCIL_MEMBERS WHERE POSITION = '{option}'"
#     cursor.execute(query)
#     data = cursor.fetchall()
#     conn.close()
#     return data

# # Route for the home page with dropdown menu
# @app.route('/council_members')
# def index():
#     return render_template('tr.html')

# # Route to handle form submission and display data
# @app.route('/submit_council_members', methods=['POST'])
# def submit():
#     option = request.form['option']
#     member = get_data_from_mysql(option)
#     print(member)
#     return render_template('result.html', data=member)
@app.route('/council_members/<council>')
def council_members(council):
    return render_template('council_members.html',council=council)

@app.route('/fetch_member/<council>', methods=['POST'])
def fetch_members(council):
    print(council)
    
    print("hhi")
    print(council)
    option = request.form['option']
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    # Query to fetch data based on the selected option
    if option == 'All member':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO and COUNCIL_MEMBERS.COUNCIL_NAME = '{council}';"
    elif option == 'General Members only':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'GENERAL MEMBER' and COUNCIL_MEMBERS.COUNCIL_NAME = '{council}';"
    elif option =='Coordinators':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'COORDINATOR' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council}';"
    elif option == 'Secretary':
        query = f"select STUDENTS.ROLL_NO, STUDENTS.EMAIL, STUDENTS.CONTACT_NO, STUDENTS.FIRST_NAME, COUNCIL_MEMBERS.POSITION from STUDENTS, COUNCIL_MEMBERS where COUNCIL_MEMBERS.ROLLS_NO = STUDENTS.ROLL_NO AND COUNCIL_MEMBERS.POSITION = 'SECRETARY' AND COUNCIL_MEMBERS.COUNCIL_NAME = '{council}';"
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)
    conn.close()
    return render_template('council_members.html', data=data)



if __name__ == "__main__":
    app.run(debug=True)
