#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 20:38:05 2018

@author: justin b
"""
import pickle
import numpy as np

from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

#@app.route('/success/<name>')
#def success(name):
#   return 'welcome %s' % name
#
#@app.route('/hello/<user>')
#def hello_name(user):
#   return render_template('hello.html', name = user)
#
#if __name__ == '__main__':
#   app.run(debug = True)

# load model from file
model = pickle.load(open("av_xgb_181221_9003.pickle.dat", "rb"))

def conv_in_to_mm(inc):
    return inc/0.0393700787

def f_to_c(far):
    return (far - 32) * 5/9

def mph_to_ms(mph):
    return mph/2.237

def gen_aspects(aspect):
     aspects = ['Aspect_East','Aspect_North', 'Aspect_Northeast', 'Aspect_Northwest', 'Aspect_South',
       'Aspect_Southeast', 'Aspect_Southwest', 'Aspect_West']
     asps = []
     for asp in aspects:
        if aspect==asp:
             asps.append(1)
        else:
            asps.append(0)
     return asps

@app.route('/avalanche_model',methods = ['POST'])
def login():
   if request.method == 'POST':
      el = float(request.form['Elevation'])
      pr_in = float(request.form['Precipitation'])
      sd_in = float(request.form['Snow_Depth'])
      sf_in = float(request.form['Snowfall'])
      mx_f = float(request.form['Max_Temperature'])
      mn_f = float(request.form['Min_Temperature'])
      ws_mph = float(request.form['Max_Wind_Speed'])
      asp = request.form['Aspect']
      
      pr_mm = conv_in_to_mm(pr_in)
      sd_mm = conv_in_to_mm(sd_in)
      sf_mm = conv_in_to_mm(sf_in)
      mx_c = f_to_c(mx_f)
      mn_c = f_to_c(mn_f)
      ws_ms = mph_to_ms(ws_mph)
      
      aspects = gen_aspects(asp)
      
      inputs = [el, pr_mm, sd_mm, sf_mm, mx_c, mn_c, ws_ms]
      inputs.extend(aspects)
      inputs = np.array([inputs])
      
      slide = model.predict(inputs)
      slide = slide[0]
      probs = model.predict_proba(inputs)
      if slide==0:
          av = 'no avalanche'
      elif slide==1:
          av = 'avalanche'
      else:
          av='ERROR'
      
      probs = probs[0][slide]
      
      dic = {'Elevation':el, 'Precipitation':pr_in, 'Snow Depth': sd_in, 'Snowfall':sf_in,
             'Max Temperature':mx_f, 'Min Temperature':mn_f, 'Max Wind Speed':ws_mph,
             'Aspect':asp,
             'Avalanche': av, 'Probability': probs}
      
      
      
      return render_template('avalanche_output.html', result = dic)
#   else:
#      user = request.args.get('nm')
#      return render_template('avalanche.html', name = user) # redirect(url_for('success',name = user))

if __name__ == '__main__':
   app.run(debug = True)