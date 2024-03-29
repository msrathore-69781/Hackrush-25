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
    event_name = request.args.get('event_name')
    try: 
        cursor = conn.cursor(dictionary=True)
        # Query to retrieve club information
        # this query joins the two table(council, COUNCIL_MEMBER) to find out number of member in a council
        cursor.execute('select * from EVENT where %s=',event_name)
        event = cursor.fetchone()
        print(event)
            # Render the template with club information
        return render_template('event.html', event=event)
    except mysql.connector.Error as e:
        return f"Error retrieving club information: {e}"
    finally:
        # Close database connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
