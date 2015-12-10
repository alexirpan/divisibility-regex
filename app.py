from flask import Flask, render_template, request

import divisibility_dfa

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/regex', methods=['POST'])
def generate_regex():
    form = request.form
    if 'base' not in form or 'divisor' not in form:
        return 'Missing form fields'

    base = form['base']
    div = form['divisor']
    if base not in ('binary', 'decimal', 'hexadecimal'):
        return 'Invalid base'
    if div not in [str(i) for i in range(1,10)]:
        return 'Invalid divisor'

    div = int(div)
    dfa = divisibility_dfa.build_dfa(base, div)
    dfa.set_start(div)
    return render_template(
        'regex.html',
        regex=divisibility_dfa.dfa_to_regex(dfa, 0),
    )


import os
debug = True
host = '127.0.0.1' if debug else '0.0.0.0'
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host=host, port=port, debug=debug)
