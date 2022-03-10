from flask import Flask
from flask import render_template, request, redirect, url_for, make_response, json
from flaskext.mysql import MySQL
from datetime import datetime
import numpy as np
import pdfkit
from werkzeug.wrappers import response

app= Flask(__name__)
#Settings to connect to the database
mysql =MySQL()
app.config['MYSQL_DATABASE_HOST']='10.8.6.111'
app.config['MYSQL_DATABASE_USER']='gasegre'
app.config['MYSQL_DATABASE_PASSWORD']='ga.segre'
app.config['MYSQL_DATABASE_DB']='gasegre'
mysql.init_app(app)

#Getting all Google Analytics Accounuts
@app.route('/allAccounts')
def allAccounts():
    sql="SELECT * FROM `cuentas_ga`;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    cuentasGA = cursor.fetchall() 
    conn.commit()
    return cuentasGA
# This is the index of the website
@app.route('/')
def index():
    cuentasGA=allAccounts()
    return render_template('/index.html',cuentasGA=cuentasGA)

#Selecting just the name of one Account
@app.route('/consultaporNombre/<int:id>')
def consultaporNombre(id):
    conn=mysql.connect()
    cursor_name=conn.cursor()
    cursor_name.execute("SELECT nombre FROM  `cuentas_ga` WHERE `id`=%s",id)
    nombreCuenta = cursor_name.fetchall()  
    conn.commit()
    return nombreCuenta  

#It shows date, session duration and number of session for one Account
@app.route('/consultaCuenta/<int:id>', methods=['POST','GET'])
def consultaCuenta(id):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT \
    DATE_FORMAT(t1.`fecha`, '%%d-%%m-%%Y'),t1.`duracion_sesion`,t1.`sesiones`,t2.`nombre`\
    FROM sesiones_ga t1 INNER JOIN `cuentas_ga` t2 \
    ON t1.id_cuenta = t2.id WHERE t2.id=%s   GROUP BY sesiones DESC",id)
    registrosCuenta = cursor.fetchall() 
    conn.commit()  
    nombreCuenta=consultaporNombre(id)
    return render_template('/consultaCuenta.html',registrosCuenta=registrosCuenta,nombreCuenta=nombreCuenta,id=id)
# The purpose of this code is give details of each date in the future.
@app.route('/detalleFechaCuenta/<int:id>/<fecha>', methods=['POST','GET'])
def detalleFechaCuenta(id,fecha):
    datos=(fecha,id)
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT \
    DATE_FORMAT(t1.`fecha`, '%%d-%%m-%%Y'),t1.`duracion_sesion`,t1.`sesiones`,t2.`nombre`\
    FROM sesiones_ga t1 INNER JOIN `cuentas_ga` t2 \
    ON t1.id_cuenta = t2.id WHERE  STR_TO_DATE(fecha, '%%Y-%%m-%%d') = STR_TO_DATE(%s, '%%d-%%m-%%Y') AND (t2.id=%s)",datos)
    registrosCuenta = cursor.fetchall() 
    conn.commit()  
    nombreCuenta=consultaporNombre(id)
    print(registrosCuenta)
    return render_template('/detalleFechaCuenta.html',id=id,fecha=fecha) 

# It brings the top 100 dates with the highest sessions
@app.route('/top100/<int:id>', methods=['POST','GET'])
def top100(id):
    sql="SELECT DATE_FORMAT(fecha, '%%d/%%m/%%Y'), duracion_sesion, sesiones FROM sesiones_ga WHERE id_cuenta=%s ORDER BY sesiones DESC LIMIT 100;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,id)
    registrosTop100 = cursor.fetchall() 
    conn.commit()
    nombreCuenta=consultaporNombre(id)    
    return render_template('/top100.html',registrosTop100=registrosTop100,nombreCuenta=nombreCuenta)
# This code feeds the individual chart for each account. It has defined the selected period (range of dates) chosen for this work.
@app.route('/chart/<int:id>/<int:sl>', methods=['POST','GET'])
def chart(id,sl):
    
    conn=mysql.connect()
    cursor=conn.cursor()
    if sl==0:
            cursor.execute("SELECT \
            DATE_FORMAT(t1.`fecha`, '%%d/%%m/%%Y'),t1.`duracion_sesion`,t1.`sesiones`,t2.`nombre`\
            FROM sesiones_ga t1 INNER JOIN `cuentas_ga` t2 \
            ON t1.id_cuenta = t2.id WHERE t2.id=%s AND fecha>='2021-08-09'ORDER BY fecha ASC LIMIT 7;",id)
    elif sl==1:
            cursor.execute("SELECT \
            DATE_FORMAT(t1.`fecha`, '%%d/%%m/%%Y'),t1.`duracion_sesion`,t1.`sesiones`,t2.`nombre`\
            FROM sesiones_ga t1 INNER JOIN `cuentas_ga` t2 \
            ON t1.id_cuenta = t2.id WHERE t2.id=%s AND fecha>='2021-07-17'ORDER BY fecha ASC LIMIT 30;",id)
    else:
            cursor.execute("SELECT \
            DATE_FORMAT(t1.`fecha`, '%%d/%%m/%%Y'),t1.`duracion_sesion`,t1.`sesiones`,t2.`nombre`\
            FROM sesiones_ga t1 INNER JOIN `cuentas_ga` t2 \
            ON t1.id_cuenta = t2.id WHERE t2.id=%s ORDER BY fecha",id)
        

    registrosCuenta = cursor.fetchall() 
    conn.commit()  
    nombreCuenta=consultaporNombre(id)
    return render_template('/chart.html',registrosCuenta=registrosCuenta,nombreCuenta=nombreCuenta,id=id) 
# Code to bring the information to make the comparison between data of Google Analytics Accounts
@app.route('/comparativo', methods=['GET', 'POST'])
def comparativo():
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT \
            DATE_FORMAT(t1.`fecha`, '%d/%m/%Y'),t1.`duracion_sesion`,t1.`sesiones`,t2.`nombre`,t2.`id`\
            FROM sesiones_ga t1 INNER JOIN `cuentas_ga` t2 \
            ON t1.id_cuenta = t2.id WHERE fecha>='2021-07-17'ORDER BY fecha ASC LIMIT 60;")
    
    registrosCuenta = cursor.fetchall() 
    
    conn.commit() 
    cuentasGA = allAccounts()
    etiquetas =[row[0] for row in registrosCuenta]
    
    
    listaTemp = []
 
    for x in etiquetas:
        if x not in listaTemp:
            listaTemp.append(x)
 
    etiquetas = listaTemp
    
    
    return render_template('/comparativo.html',cuentasGA=cuentasGA,etiquetas=etiquetas,registrosCuenta=registrosCuenta)   
#It shows the monthly balance for Single-session users for each Google Analytics Account                       
@app.route('/balance/<int:id>', methods=['POST','GET'])
def balance(id):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT \
    sum(t1.`usuarios`), DATE_FORMAT (t1.`fecha`,'%%M %%Y') AS fechaGrupo\
    FROM usuarios_unica_sesion_ga t1 INNER JOIN `cuentas_ga` t2 \
    ON t1.id_cuenta = t2.id WHERE  t2.id=%s GROUP BY fechaGrupo ORDER BY MONTHNAME(fechaGrupo) ",id)   
    registrosCuenta = cursor.fetchall() 
    valores=[int(row[0]) for row in registrosCuenta]
    conn.commit()  
    

    nombreCuenta=consultaporNombre(id)
    return render_template('/balance.html',registrosCuenta=registrosCuenta,nombreCuenta=nombreCuenta,id=id)        
         

    




if __name__=='__main__':
       app.run(debug=True)



  
