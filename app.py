from flask import Flask
from flask import render_template, request, redirect, url_for
from flaskext.mysql import MySQL

app= Flask(__name__)
mysql =MySQL()
app.config['MYSQL_DATABASE_HOST']='10.8.6.111'
app.config['MYSQL_DATABASE_USER']='gasegre'
app.config['MYSQL_DATABASE_PASSWORD']='ga.segre'
app.config['MYSQL_DATABASE_DB']='gasegre'
mysql.init_app(app)

@app.route('/')
def index():
    sql="SELECT * FROM `cuentas_ga`;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)
    cuentasGA = cursor.fetchall() 
    conn.commit()
    return render_template('/index.html',cuentasGA=cuentasGA)

@app.route('/consultaporNombre/<int:id>')
def consultaporNombre(id):
    conn=mysql.connect()
    cursor_name=conn.cursor()
    cursor_name.execute("SELECT nombre FROM  `cuentas_ga` WHERE `id`=%s",id)
    nombreCuenta = cursor_name.fetchall()  
    conn.commit()
    return nombreCuenta  


@app.route('/consultaCuenta/<int:id>')
def consultaCuenta(id):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT \
    t1.`fecha`,t1.`duracion_sesion`,t1.`sesiones`,t2.`nombre`\
    FROM sesiones_ga t1 INNER JOIN `cuentas_ga` t2 \
    ON t1.id_cuenta = t2.id WHERE t2.id=%s   GROUP BY sesiones DESC",id)
    registrosCuenta = cursor.fetchall() 
    conn.commit()  
    nombreCuenta=consultaporNombre(id)
    return render_template('/consultaCuenta.html',registrosCuenta=registrosCuenta,nombreCuenta=nombreCuenta)

 


@app.route('/top100/<int:id>')
def top100(id):
    sql="SELECT fecha, duracion_sesion, sesiones FROM sesiones_ga WHERE id_cuenta=%s ORDER BY sesiones DESC LIMIT 100;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,id)
    registrosTop100 = cursor.fetchall() 
    conn.commit()
    nombreCuenta=consultaporNombre(id)    
    return render_template('/top100.html',registrosTop100=registrosTop100,nombreCuenta=nombreCuenta)
   

if __name__=='__main__':
    app.run(debug=True)

#SELECT * FROM sesiones_ga WHERE id_cuenta=93372212 ORDER BY sesiones DESC LIMIT 100;    
