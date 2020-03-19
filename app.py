from flask import Flask, render_template, request, redirect
import templates.plotter as plotter

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/index', methods=['POST'])
def read_form():
  script, div = plotter.plot_stocks(request.form)
  return render_template('index.html', plots_div=div, plots_script=script)

if __name__ == '__main__':
  app.debug = True
  app.run(port=33507)

