from flask import Flask, render_template
app = Flask('ankiWebUI', static_folder='static', static_url_path='', template_folder='web/templates')

@app.route('/')
def root():
    return render_template('index.html')

app.run(host='0.0.0.0', port=8080, debug=True)