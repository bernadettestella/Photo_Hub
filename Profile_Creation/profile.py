from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

Photo_Hub = []

@app.route('/')
def index():
    return render_template('index.html', profiles=profiles)

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']

        # Create a new profile dictionary
        new_profile = {
            'name': name,
            'age': age,
            'email': email
        }

        # Add the new profile to the list
        profiles.append(new_profile)

        return redirect(url_for('index'))

    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)

