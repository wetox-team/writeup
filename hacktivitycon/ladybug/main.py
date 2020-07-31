from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('home.html')


@app.route('/film/&lt;name&gt;/')
def film(name):
    assert name in [
        'park',
        'disney',
        'beach',
        'home',
    ]

    if 'home' in name:
        return render_template('home.html')

    if 'park' in name:
        return render_template('park.html')

    if 'disney' in name:
        return render_template('disney.html')

    if 'beach' in name:
        return render_template('beach.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
