from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import pickle
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.secret_key = "toplevelsecret"

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bug1'
}

# Function to establish MySQL connection
def connect_to_mysql():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print("Error connecting to MySQL:", err)
        return None

# Function to clean text
def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return ' '.join(filtered_tokens)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('employee_dashboard.html')

@app.route('/emplogin', methods=['GET', 'POST'])
def emplogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_to_mysql()
        if conn:
            cursor = conn.cursor()
            query = "SELECT id FROM employees WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            employee_id = cursor.fetchone()
            query = "insert into employee_id values (%s)"
            cursor.execute(query, (int(employee_id[0]),))
            cursor.close()
            conn.close()
            if employee_id:
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid username or password"
                return render_template('emplogin.html', error=error)
        else:
            error = "Database connection error"
            return render_template('emplogin.html', error=error)
    else:
        return render_template('emplogin.html')

@app.route('/view_bugs')
def view_bugs():
    connection = connect_to_mysql()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM bugass WHERE Progress = 'open' OR Progress = 'inprogress';"
            cursor.execute(query)
            bug_data1 = cursor.fetchall()
        except mysql.connector.Error as err:
            print("Error fetching bug details:", err)
        finally:
            cursor.close()
            connection.close()
    return render_template('view_bugs.html', bug_data=bug_data1)

@app.route('/')
def manager_dashboard():
    return render_template('manager_dashboard.html')

@app.route('/add-employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO employees (username, password, full_name, email) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (username, password, name, email))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('manager_dashboard'))
            except mysql.connector.Error as err:
                print("Error executing SQL query:", err)
                return render_template('error.html', error="Error adding employee to the database")
    return render_template('add_employee.html')

@app.route('/add-Tester', methods=['GET', 'POST'])
def add_tester_form():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO testers (username, password, full_name, email) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (username, password, name, email))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('manager_dashboard'))
            except mysql.connector.Error as err:
                print("Error executing SQL query:", err)
                return render_template('error.html', error="Error adding tester to the database")
    return render_template('add_tester.html')

@app.route('/teslogin', methods=['GET', 'POST'])
def teslogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_to_mysql()
        if conn:
            cursor = conn.cursor()
            query = "SELECT * FROM testers WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            tester = cursor.fetchone()
            cursor.close()
            conn.close()
            if tester:
                return redirect(url_for('tsdashboard'))
            else:
                error = "Invalid username or password"
                return render_template('teslogin.html', error=error)
        else:
            error = "Database connection error"
            return render_template('teslogin.html', error=error)
    else:
        return render_template('teslogin.html')

@app.route('/report_bug', methods=['GET'])
def report_bug():
    return render_template('report bug.html')



@app.route('/backend/fetch_testers_endpoint', methods=['GET'])
def fetch_testers_endpoint():
    conn = connect_to_mysql()
    tester_data = []
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT id, full_name FROM testers"
            cursor.execute(query)
            tester_rows = cursor.fetchall()
            for row in tester_rows:
                tester_data.append({"id": row[0], "name": row[1]})
        except mysql.connector.Error as err:
            print("Error fetching testers:", err)
        finally:
            cursor.close()
            conn.close()
    return jsonify(tester_data)

# Load the model
with open('your_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Load the vectorizer
with open('your_vectorizer.pkl', 'rb') as file:
    vectorizer = pickle.load(file)



@app.route('/add_bug', methods=['POST'])
def add_bug():
    if request.method == 'POST':
        
        bug_description = request.form.get('description')
        cleaned_bug_description = clean_text(bug_description)
        bug_description_tfidf = vectorizer.transform([cleaned_bug_description])
        predicted_priority = model.predict(bug_description_tfidf)[0]
        tester_name = request.json.get('formData')
        # Store data in the database
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO BugAss (Description, Priority, AssignedTo) VALUES (%s, %s, %s)"
                cursor.execute(query, (bug_description, predicted_priority, tester_name))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('dashboard'))
            except mysql.connector.Error as err:
                print("Error adding bug:", err)
                return render_template('error.html', error="Error adding bug to the database")

    return redirect(url_for('dashboard'))

@app.route('/tsdashboard',methods=['POST'])
def tester_dashboard():
    conn = connect_to_mysql()
    bug_list = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT bugid, Description, Progress, priority FROM bugass"
            cursor.execute(query)
            bug_list = cursor.fetchall()
        except mysql.connector.Error as err:
            print("Error fetching bug details:", err)
        finally:
            cursor.close()
            conn.close()
    return render_template('bug_list.html', bug_list=bug_list)

# Route for working on a bug
@app.route('/work_on_bug/<int:bug_id>',methods=['GET','POST'])
def work_on_bug(bug_id):
        progress = request.form.get('progress')
        suggestion = request.form.get('suggestion')
        conn = connect_to_mysql()
        if conn:
            try:
                cursor = conn.cursor()
                update_query = "UPDATE bugass SET Progress = %s,suggestion=%s WHERE bugid = %s"
                cursor.execute(update_query, (progress,suggestion,bug_id))
               
            except mysql.connector.Error as err:
                print("Error fetching bug details:", err)
            finally:
                cursor.close()
                conn.close()
        return render_template('work_on_bug.html',bug_id=bug_id)
@app.route('/logout')
def logout():

    return redirect(url_for('teslogin')) 

if __name__ == '__main__':
    app.run(debug=True)
