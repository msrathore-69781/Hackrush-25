# DBMS Assignment 3 - Club Management System Webapp

## Made with Flask and MySQL

### Setup (G1 and G2)

1. Install Python
2. Install MySQL
3. Install the required packages for python: 

    ```bash
    pip install flask
    pip install flask-mysql
    pip install flask-session
    pip install mysql.connector
    ```

4. Create the database `CLUB_MS`.
    In order to do login in to MYSQL Workbench using your root user and run the 'studentdb.sql' file in your SQL Workbench. This will create the database and populate it with the required tables and data.

5. Now update the mysql configurations in 'app.py' file.
    If you are using root user like us you can enter your root password for the password key below in the 'app.py' file, however, it should be best to rather use some other user and and passowrd, but for that you need to run the script 'studentdb.sql' with the same user.
    ```py
    mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'DBMS_mysql@0204',    #Enter ur password for root
    'database': 'CLUB_MS'
    }
    ```

### Running the Webapp

After setting up the database and configuration, we can run our webapp. To do that:
1. Open your terminal window in the folder 'Database-Project/' and run the following:
    ```bash
    python web_app.py
    ```
2. Open your browser and go to the URL that is displayed in the terminal, like this:
    ```bash
    http://127.0.0.1:5000
    ```

Now your home page is opened which is a login page for our Club Management System where you can login as a student, employee or admin (person with all permissions).
