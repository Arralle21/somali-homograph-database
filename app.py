from flask import Flask, render_template, request, redirect, url_for
from somali_homograph_db import SomaliHomographDB

app = Flask(__name__)
db = SomaliHomographDB()

@app.route('/')
def index():
    homographs = db.list_all_homographs()
    return render_template('index.html', homographs=homographs)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    results = db.search_homographs(query)
    return render_template('search_results.html', query=query, results=results)

@app.route('/homograph/<word>')
def homograph_details(word):
    details = db.get_homograph(word)
    return render_template('homograph_details.html', word=word, details=details)

@app.route('/add', methods=['GET', 'POST'])
def add_homograph():
    if request.method == 'POST':
        word = request.form['word']
        definitions = request.form['definitions'].split('\n')
        db.insert_homograph(word, definitions)
        return redirect(url_for('index'))
    return render_template('add_homograph.html')

@app.route('/edit/<word>', methods=['GET', 'POST'])
def edit_homograph(word):
    if request.method == 'POST':
        new_definitions = request.form['definitions'].split('\n')
        db.update_homograph(word, new_definitions)
        return redirect(url_for('homograph_details', word=word))
    details = db.get_homograph(word)
    return render_template('edit_homograph.html', word=word, details=details)

@app.route('/delete/<word>', methods=['POST'])
def delete_homograph(word):
    db.delete_homograph(word)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)