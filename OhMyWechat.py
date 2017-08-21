import json
from flask import Flask, render_template, Response, session
from System.Wechat.Login.Login import Login
app = Flask(__name__)
app.secret_key = 'HmS*A#k358A3Jr4NspPV2Jdd@PF30*He'

@app.route('/')
def login():
    return render_template(template_name_or_list="login.html")


@app.route('/main')
def main():
    return render_template(template_name_or_list="main.html", activeMenu='dashboard')


@app.route('/account')
def account():
    return render_template(template_name_or_list="account.html", activeMenu='account')


@app.route('/api/getQrCode')
def getqrcode():
    qrcode_obj = Login().get_qrcode()
    if qrcode_obj['code'] == 200:
        uuid = qrcode_obj['uuid']
        qrcode = qrcode_obj['qrcode']
        session['uuid'] = uuid
    return Response(qrcode, mimetype="image/jpeg")


@app.route('/api/checkLoginStatus')
def checkloginstatus():
    result = dict()
    if 'uuid' in session:
        status_obj = Login().check_login_status(uuid=session['uuid'])
        return json.dumps(status_obj)
    else:
        result['code'] = 404
        result['reason'] = "uuid已经过期，请重新获取二维码"
        return json.dumps(result)

if __name__ == '__main__':
    app.run(debug=True)
