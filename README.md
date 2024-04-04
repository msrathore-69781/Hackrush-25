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

### Operations on ADMIN view
 Admin can perform INSERT, DELETE and RENAME queries on the tables of the database.
 BEFORE : </br>
 ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/f9cd98f7-48ce-4889-b64d-24a143fcd1b7) </br>
 ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/6e0391af-5ff9-477f-955a-b787fe864437) </br>

1. Performing INSERT </br>
    We INSERT a club "Club_dummy" to our clubs table. Fill in all the fields and press INSERT button. Changes will reflect both on the webapp and database. </br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/e84ec765-ff34-4b2a-8f4c-7737fffa94c4) </br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/8dfbb7a9-21bf-4b52-8200-3646299043b3) </br>
2. Performing  DELETE </br>
    We DELETE the club "Club_dummy" which we earlier added. Just fill in the corresponding fields and press DELETE. </br>
    ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/e496a804-7a74-44b0-94cb-3e176b3a6c7a) </br>
    ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/7425238f-1b80-4d57-ac3f-998d83729a59) </br>
3. Performing RENAME </br>
    Admin can rename a table and it will reflect over the database and the webapp. </br>
    On pressing the RENAME button the following fields appears asking fora new name. Fill in the field and press enter.</br>
    ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/ff82ea9c-a551-4784-9573-d541b7ea030d) </br>

   Renaming clubs to clubs_of_iitgn.</br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/e7c00069-bf10-4bf8-baad-de0f8c2eb5ee)</br>
    Also reflected on the sql where now club_ms.clubs table doesn’t exist, instead club_ms.clubs_of_iitgn exists. Same can be tried out for other tables from the admin Page whose access only lies with admin (if you login as admin).</br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/f765f449-dbdc-457e-9546-f766a90ed031) </br>
   Also the main admin page has now changed </br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/2c05286d-8ab7-49c8-a8e5-e425ed326222)



   




   
