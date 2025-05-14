from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
import random
import string

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/password_generator_db"
mongo = PyMongo(app)

# Password generation function
def generate_password(length, use_upper, use_lower, use_digits, use_special):
    char_pool = ''
    if use_upper:
        char_pool += string.ascii_uppercase
    if use_lower:
        char_pool += string.ascii_lowercase
    if use_digits:
        char_pool += string.digits
    if use_special:
        char_pool += string.punctuation

    if not char_pool:
        raise ValueError("No character types selected!")

    password = ''.join(random.choice(char_pool) for _ in range(length))
    return password

# Password strength function
def password_strength(length):
    if length < 6:
        return "Weak"
    elif 6 <= length < 10:
        return "Moderate"
    else:
        return "Strong"

# Route for the main page (password generation)
@app.route('/')
def index():
    return render_template('index.html')

# Route for generating passwords
@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Retrieve form data
        length = int(request.form['length'])
        use_upper = 'upper' in request.form
        use_lower = 'lower' in request.form
        use_digits = 'digits' in request.form
        use_special = 'special' in request.form
        total = int(request.form['count'])

        if length <= 0 or total <= 0:
            raise ValueError("Password length and total count must be positive integers.")

        # Generate passwords
        passwords = []
        for _ in range(total):
            pwd = generate_password(length, use_upper, use_lower, use_digits, use_special)
            strength = password_strength(length)
            passwords.append({"password": pwd, "strength": strength})

        # Store generated passwords in MongoDB
        mongo.db.passwords.insert_many(passwords)

        # Pass passwords to the result page
        return render_template('result.html', passwords=passwords)

    except ValueError as e:
        return f"Error: {e}"

# Route for viewing stored passwords (optional)
@app.route('/view_all')
def view_all():
    passwords = mongo.db.passwords.find()  # Retrieve all passwords from MongoDB
    return render_template('result.html', passwords=passwords)

if __name__ == '__main__':
    app.run(debug=True)
