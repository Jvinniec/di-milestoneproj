from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/index', methods=['POST'])
def read_form():
  ret = dict()
  ret['stocks'] = request.form.get('sname')
  ret['plotinfo'] = request.form.get('plotinfo')
  ret['djia']     = bool(request.form.get('djia'))
  ret['sp500']    = bool(request.form.get('sp500'))
  ret['nasdaq']   = bool(request.form.get('nasdaq'))
  print(ret['stocks'])
  return ret

if __name__ == '__main__':
  app.debug = True
  app.run(port=33507)
