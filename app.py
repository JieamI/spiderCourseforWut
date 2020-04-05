from flask import Flask, jsonify, request
from flask_cors import *
from flask_sqlalchemy import SQLAlchemy
from spiderCourse import SpiderCourse
import os
import sys
import json

app = Flask(__name__)
WIN = sys.platform.startswith('win') 
if WIN: 
    prefix = 'sqlite:///' 
else:
    prefix = 'sqlite:////'
  
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    usr = db.Column(db.String(30), primary_key = True)
    pwd = db.Column(db.String(30))
    event = db.Column(db.Text)
   
#ID验证并注册
@app.route('/login', methods=['POST'])
@cross_origin()
def user_login():
    data = json.loads(request.get_data(as_text = True))
    if 'usr' in data and 'pwd' in data and data['usr'] and data['pwd']:
        user = User.query.filter_by(usr = data['usr']).first()
        print(data['usr'])
        print(data['pwd'])
        if user:
            print('ok')
            try:
                SpiderCourse(data['usr'], data['pwd']).SoupParse()
                return jsonify({'status': 1})
            except:
                return jsonify({'status': 0})
        else:
            try:
                SpiderCourse(data['usr'], data['pwd']).SoupParse()
                db.session.add(User(usr = data['usr'], pwd = data['pwd']))
                db.session.commit()
                return jsonify({'status': 1})
            except:
                return jsonify({'status': 0})
    return jsonify({'status': 0})

# 课表获取API
@app.route('/course', methods=['POST'])
@cross_origin()
def get_tasks():
    data = json.loads(request.get_data(as_text=True))
    if 'usr' in data and 'pwd' in data and data['usr'] and data['pwd']:
        spirse = SpiderCourse(data['usr'], data['pwd'])
        try:
            dic = {'Mon': [], 'Tue': [], 'Wed': [], 'Thu': [], 'Fri': [], 'Sat': [], 'Sun': []}
            spirse.SoupParse()
            for each in spirse.res:
                index = 0
                for value in dic.values():
                    value.append(each[index])
                    index += 1
            return jsonify({'data': dic, 'status': 1})
        except:
            return jsonify({'status': 0})
    else:
        return jsonify({'status': 0})

#事项云端同步更新API
@app.route('/event', methods=['POST'])
@cross_origin()
def handleEvent():
    data = json.loads(request.get_data(as_text=True))
    if 'usr' in data and 'pwd' in data and data['usr'] and data['pwd']:
        user = User.query.filter_by(usr = data['usr']).first()
        if user.pwd == data['pwd']:
            if data['method'] == 'get':
                if user.event:
                    eventlis = user.event.split('&')
                    for index, val in enumerate(eventlis):
                        temp = eventlis[index].split('|')
                        eventlis[index] = {'content': temp[0], 'id': eval(temp[1])}
                        if temp[2] == 'true':
                            eventlis[index]['done'] = True
                        elif temp[2] == 'false':
                            eventlis[index]['done'] = False
                    return jsonify({'eventlis':eventlis, 'status':1})
                return jsonify({'status': 0})
            elif data['method'] == 'post':
                strlis = data['eventlis']['content'] + '|' + str(data['eventlis']['id']) + '|' + str(data['eventlis']['done']).lower()   
                if user.event:
                    user.event = user.event + '&' + strlis 
                else:
                    user.event = strlis
                db.session.commit()
                return jsonify({'status': 1})
        return jsonify({'status': 0})
    return jsonify({'status': 0})          

#事项状态更新API
@app.route('/switch', methods=['POST'])
@cross_origin()
def handleSwitch():
    data = json.loads(request.get_data(as_text=True))
    if 'usr' in data and 'pwd' in data and data['usr'] and data['pwd']:
        user = User.query.filter_by(usr = data['usr']).first()
        if user.pwd == data['pwd']:
            if data['eventlis']['done']:
                user.event = user.event.replace(str(data['eventlis']['id']) + '|' + 'false', str(data['eventlis']['id']) + '|' + "true")
            else:
                user.event = user.event.replace(str(data['eventlis']['id']) + '|' + 'true', str(data['eventlis']['id']) + '|' + "false")
            db.session.commit()
            print(user.event)
            return jsonify({'status': 1})
        return jsonify({'status': 0})
    return jsonify({'status': 0})

#逃生舱
@app.route('/outlast', methods=['GET'])
@cross_origin()
def outlast():
    msg = 'HELLOWORLD'
    return jsonify({'msg': msg})