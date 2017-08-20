from flask import Flask,render_template

app = Flask(__name__)


@app.route('/')
def login():
    return render_template(template_name_or_list="login.html")


@app.route('/main')
def main():
    return render_template(template_name_or_list="main.html", activeMenu='dashboard')


@app.route('/account')
def account():
    return render_template(template_name_or_list="account.html", activeMenu='account')

if __name__ == '__main__':
    app.run(debug=True)
