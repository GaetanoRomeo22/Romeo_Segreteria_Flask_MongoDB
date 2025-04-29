from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import bcrypt


app = Flask(__name__)
app.secret_key = 'Gaetano22'

try:  # Tentativo di connessione al database MongoDB
    username = 'Gaetano22'
    password = 'Vittoria_30'
    client = MongoClient(
        f'mongodb+srv://{username}:{password}@segreteria.nzypczo.mongodb.net/?retryWrites=true&w=majority&appName=Segreteria')
    db = client['Segreteria']
except Exception as e:
    print(f"Errore connessione database: {e}")


@app.route('/')  # Route principale
def index():
    return render_template('index.html')


@app.route('/index')  # Route per la home page
def back_home():
    return render_template('index.html')


@app.route('/showRegister')  # Route per la pagina di registrazione
def show_register():
    return render_template('registrazione.html')


@app.route('/showRetrievePassword')  # Route per la pagina di recupero password
def show_retrieve_password():
    return render_template('recupero_password.html')


@app.route('/showAccount')  # Route per la pagina dell'account
def show_account():
    if 'user' not in session:  # Controlla se l'utente è loggato
        flash('Devi effettuare il login per accedere a questa pagina')
        return redirect(url_for('index'))
    return render_template('account.html')


@app.route('/showAvailableExams') # Route per la pagina degli esami prenotabili
def show_available_exams():
    if 'user' not in session:  # Controlla se l'utente è loggato
        flash('Devi effettuare il login per accedere a questa pagina')
        return redirect(url_for('index'))
    return render_template('appelli_disponibili.html')


@app.route('/showGivenExams') # Route per la pagina del libretto degli esami
def show_given_exams():
    if 'user' not in session:  # Controlla se l'utente è loggato
        flash('Devi effettuare il login per accedere a questa pagina')
        return redirect(url_for('index'))
    return render_template('libretto.html')


@app.route('/showBookedExams') # Route per la pagina degli esami prenotati
def show_booked_exams():
    if 'user' not in session:  # Controlla se l'utente è loggato
        flash('Devi effettuare il login per accedere a questa pagina')
        return redirect(url_for('index'))
    return render_template('appelli_prenotati.html')


@app.route('/login', methods=['POST'])  # Route per il login
def login():  # Funzione di login
    matricola = request.form['matricola']  # Recupera la matricola dal form
    password = request.form['password']  # Recupera la password dal form
    if not matricola or not password:  # Controlla se matricola e password sono vuoti
        flash('Matricola o password mancanti')
        return redirect(url_for('index'))
    else:
        try:
            user = db.users.find_one({'matricola': matricola, 'password': password})  # Cerca l'utente nel database
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):  # Se l'utente esiste
                session['user'] = matricola # Salva la matricola dello studente nella sessione
                return redirect(url_for('show_account'))  # Reindirizza alla pagina dell'account
            else:  # Se l'utente non esiste
                flash('Matricola o password errati')
                return redirect(url_for('index'))  # Resta alla pagina di login
        except Exception as exc:
            flash("Errore durante il login: " + str(exc))
            return redirect(url_for('index'))


@app.route('/register', methods=['POST'])  # Route per la registrazione
def register():  # Funzione di registrazione
    matricola = request.form['matricola']  # Recupera la matricola dal form
    password = request.form['password']  # Recupera la password dal form
    confirmPassword = request.form['confirm_password'] # Recupera la password di conferma dal form
    if not matricola or not matricola.isdigit() or len(matricola) != 10: # Controlla il formato della matricola
        flash('La matricola deve essere una stringa numerica di 10 cifre')
        return redirect(url_for('show_register'))
    if password != confirmPassword: # Controlla se le password coincidono
        flash('Le password non corrispondono')
        return redirect(url_for('show_register'))
    if not password or len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password): # Controlla il formato della password
        flash('La password deve essere lunga almeno 8 caratteri, contenere almeno una lettera maiuscola e un numero')
        return redirect(url_for('show_register'))
    else:
        try:
            user = db.users.find_one({'matricola': matricola})  # Cerca l'utente nel database
            if user:  # Se l'utente viene trovato significa che la matricola è già utilizzata
                flash('Matricola già utilizzata')
                return redirect(url_for('show_register'))  # Resta alla pagina di registrazione
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # Hashing della password
            db.users.insert_one({'matricola': matricola, 'password': hashed_password})  # Inserisce l'utente nel database
            return redirect(url_for('index'))  # Reindirizza alla pagina di login
        except Exception as exc:
            flash("Errore durante la registrazione: " + str(exc))
            return redirect(url_for('show_register'))


@app.route('/logout') # Route per il logout
def logout(): # Funzione di logout
    session.clear() # Rimuove tutti i dati dalla sessione
    return redirect(url_for('index')) # Reindirizza alla pagina di login


if __name__ == '__main__':
    app.run()