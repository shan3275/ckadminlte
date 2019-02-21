from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello World'

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/json/<cid>',methods=['GET'])
def json(cid):
    ip = request.remote_addr
    return jsonify({'cid':cid,'ip':ip})

@app.route('/cookie/<cid>',methods=['GET'])
def cookie(cid):
    ip = request.remote_addr
    #cookie = {'dy_did':"d7856e88c7d85b5ce124dce900081501", 'PHPSESSID':"e5dc4rldj5nvlup3astiaqls86", 'acf_auth':"94b6p%2Fib5pn8Ta0hTBS%2FV8hmsViXiZbHryWBOG00q76X0tWJY2pLkvustZhq1RkNhkbT2esi4wyN41%2FjlTdVvQNuk993ldMCvnwH0o%2BETmuM%2BI4eZhGkH80", 'wan_auth37wan':"8d58ce9bcc18S1ICHo5I1yfuT3uGtnVq%2FNjY3r2ss9F%2FeppMSUD5fyH%2B7Td8xoVUiuvBw%2F3zFvCLbF%2BYKJsD99aXOJh%2BsqcnleZl2nwPmTDoGg7AloQ", 'acf_uid':"213373476", 'acf_username':"213373476", 'acf_nickname':"%E6%96%97%E9%B1%BC%E7%94%A8%E6%88%B7ZeyUP4aK", 'acf_own_room':"0", 'acf_groupid':"1", 'acf_phonestatus':"1", 'acf_avatar':"https%3A%2F%2Fapic.douyucdn.cn%2Fupload%2Favatar%2Fdefault%2F07_", 'acf_ct':"0", 'acf_ltkid':"84366870", 'acf_biz':"1", 'acf_stk':"8a2ccec55964f1d6", 'smidV2':"201807171811435d14347d8ddca7a2d85b8611babdd81500e5bf31d89b52a50", 'acf_did':"d7856e88c7d85b5ce124dce900081501", 'Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7':"1531822301,1531832176", 'Hm_lpvt_e99aee90ec1b2106afe7ec3b199020a7':"1531832229"}
    cookie = "acf_ccn=9ebda13b7007e85c4ac78fbdd806a292; PHPSESSID=ufnuaeveatuk14qutld41gh835; acf_auth=48b4yMj4XJ%2BCCLr0y1ZJhIobmo3xT24faoZ7l7HefWL%2BPunwlhVlpHdAqNBzp9ZYO2Noj%2FqeJmTj7ffDU1dGt0%2FzLA%2FjoSjqAknXVxxdm5isS%2Be9SDEcLA8; wan_auth37wan=20dc61d4b8f4gKp4CpvWwgy2yDuKl%2FWJ51UTqGxtjCgNxdBcy8S7GpHKWH2LsUDR%2FtmOIkd5jFi1OSOsMZmPN12Jo%2F%2B1q0RQ5BMpWSrVd6pbJyS1OIo; acf_uid=213906007; acf_username=213906007; acf_nickname=%E6%B8%A9%E5%8D%87%E8%B1%AA%E5%B0%8F%E9%9D%9E%E9%85%8Bouj571; acf_own_room=0; acf_groupid=1; acf_phonestatus=0; acf_avatar=https%3A%2F%2Fapic.douyucdn.cn%2Fupload%2Favatar%2Fdefault%2F07_; acf_ct=0; acf_ltkid=88751537; acf_biz=1; acf_stk=78b018849a4af582; acf_devid=6f2dee74ed18a31897f7f2420117e036"
    return jsonify({'cid':cid,'ip':ip, 'cookie': cookie})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
