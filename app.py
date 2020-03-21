from flask import Flask, render_template, request, redirect
import templates.plotter as plotter

app = Flask(__name__)

@app.route('/')
def index():
    """ Render homepage """
    # Create some helpful text
    help_text = '''
    <br>
    <h3>
    Please fill out the form to generate a plot
    </h3>
    '''

    return render_template('index.html', plots_div=help_text)

@app.route('/about')
def about():
    """ Render 'about' page """
    return render_template('about.html')

@app.route('/index', methods=['POST'])
def read_form():
    """ Parses the webpage form """
    # Parse the form
    script, div = plotter.plot_stocks(request.form)
    symbols = request.form.get('sname')

    # Make sure to maintain the cbf being checked
    if bool(request.form.get('colorblind')):
        cbf = 'checked'
    else:
        cbf = 'unchecked'
    
    return render_template('index.html', 
                            plots_div=div, plots_script=script,
                            symbols=f"{symbols}", cbf=cbf)

if __name__ == '__main__':
    app.debug = False
    app.run(port=33507)
