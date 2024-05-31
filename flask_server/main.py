from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def Hello():
  # implement functionalities
  return "Hello there"

@app.route('/name')
def my_name():
  return "Yvonne Chemtai"

@app.route('/home')
def home():
    return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True, port='2024')
