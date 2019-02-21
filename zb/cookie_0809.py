import sys
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello'

records = []

def fetch_record(ip):
    for record in records:
        if record['ip'] == "":
            record['ip'] = ip
            return record

    return None

GCNT = 0
def get_record(ip):
    global GCNT
    for record in records:
        if record['ip'] == ip:
            return record

    newrecord = None

    GCNT += 1

    if GCNT % 5 == 1:
        newrecord = fetch_record(ip)

    return newrecord

def clear_records():
    cnt = 0
    for record in records:
        if record['ip'] != "":
            record['ip'] = ""
            cnt += 1

    return cnt

@app.route('/clear',methods=['GET'])
def clear():
    cnt = clear_records()

    ip = request.remote_addr

    rep = {'ip':ip, 'cnt': cnt}

    print "rep: ", rep

    return jsonify(rep)


@app.route('/cookie',methods=['GET'])
def cookie():
    ip = request.remote_addr

    record = get_record(ip)
    if record == None:
        cookie = "None"
    else:
        cookie = record['cookie']

    rep = {'ip':ip, 'cookie': cookie}

    print "rep: ", rep

    return jsonify(rep)


def cookie_load(path):
    FILE = open(path, 'rb')

    idx = 0
    for line in FILE:
        cookie = line.strip('\n')
        record = {'ip':"", 'cookie':cookie, 'idx':idx}
        records.append(record)
        idx += 1

    random.shuffle(records)

    for record in records:
        print "idx %d cookie: %s" %(record['idx'], record['cookie'])

if __name__ == '__main__':
    cookie_load(sys.argv[1])
    app.run(host='0.0.0.0', port=8888)
