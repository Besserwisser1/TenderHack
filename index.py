from flask import Flask, render_template, url_for, request, session, g, redirect, abort, flash, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
import os
import re
import datetime
from models.models import *
# from plugins.plugins import *
import json
from schemas import *


# users_.create_table() # Созданиетаблицы пользователей 
# tasks_data.create_table() # Создание таблицы тасков

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('PYTHON_PROG_SETTINGS', silent=True) 
app.config['PERMANENT_SESSION_LIFETIME'] =  datetime.timedelta(minutes=20) # Время жизни сессии
engine = database()

# ГЛАВНАЯ
@app.route('/')
def main():
	bd_Session = sessionmaker(bind=engine)
	bd_session = bd_Session()
	query = bd_session.query(User.id, User.username, User.status).first()
	if not query:
		return redirect(url_for('sign_up'))
	if not session.permanent:
		return redirect(url_for('login'))
	else:
		return redirect(url_for('show_tender'))
# ---------------------------------------------------------------------------

# РЕГИСТРАЦИЯ 
@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
	error = None
	#Проверка типа запроса
	print(request.method)
	if request.method == 'POST':

		if request.form['username'] and request.form['password']:
				#Проверка на существование логина
			bd_Session = sessionmaker(bind=engine)
			bd_session = bd_Session()
			query = bd_session.query(User).filter(User.email == request.form['email']).first()
			# users_.select().where(users_.username == request.form['username'])
			if query:
				error = ['email адрес уже зарегистрирован']
				bd_session.close()
				return render_template('content/sign_up.html', error=error)
			else:
				#Проверка пароля на наличие латинских букв обоих регистров, цифр и спецсимволов, длиной не менее 6 символов
				if not re.match('(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}', request.form['password']):
					error=['Пароль должен состоять из 6 символов и содержать:',
						 '1.хотя бы одну цифру', '2.хотя бы один спецсимвол',
						 '3.хотя бы одну латинскую букву в нижнем и верхнем регистре']
					bd_session.close()
					return render_template('content/sign_up.html', error=error)
				passw = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt(14))
				
				query = bd_session.query(User.username).first()
				if not query:
					status_user = 'admin'
				elif session['status_user'] == 'admin':
					status_user = session['status_user']
				else:
					status_user = 'user'
				user = User(username=request.form['username'], password=passw, email=request.form['email'], status=status_user, default=False)
				bd_session.add(user)
				bd_session.commit()
				bd_session.close()
				# users_.create(username=request.form['username'], password=passw)
				return redirect(url_for('main'))
					#------------------------------------------------------------

			#----------------------------------------------------------------
				
		else:
			error=['Вы не ввели логин или пароль']
			return render_template('content/sign_up.html', error=error)
	#--------------------------------------------------------------------
	else:
		bd_Session = sessionmaker(bind=engine)
		bd_session = bd_Session()
		query = bd_session.query(User.id, User.username, User.status).first()
		bd_session.close() 
		return render_template('content/sign_up.html', error=error)
# ---------------------------------------------------------------------------

# АВТОРИЗАЦИЯ
@app.route('/login', methods=['POST', 'GET'])
def login():
	error = None
	#Проверка типа запроса
	if request.method == 'POST':

		#Проверка ввода логина и пароля
		if request.form['username'] and request.form['password']:
			bd_Session = sessionmaker(bind=engine)
			bd_session = bd_Session()
			query = bd_session.query(User).filter(User.username == request.form['username']).first()
			# query = users_.select().where(users_.username == request.form['username']) #SQL запрос(получить логин где логин равен введенному)

			# Проверка на существование логина
			if query:
				user_pass = query.password

				#Проверка на сходство паролей(введенный и существующий)
				if bcrypt.checkpw(request.form['password'].encode('utf-8'), user_pass):

					session.permanent = True
					session['user_id'] = query.id
					session['login_name'] = request.form['username']
					session['status_user'] = query.status
					bd_session.close()
					return redirect(url_for('main'))
				else:
					error=['неверный пароль']
					bd_session.close()
					return render_template('content/login.html', error=error) #Рендер на страницу
				#------------------------------------------------------------

			else:
				error=['Неверный логин']
				bd_session.close()
				return render_template('content/login.html', error=error) #Рендер на страницу
			#----------------------------------------------------------------

		else:
			error=['Вы не ввели логин или пароль']
			return render_template('content/login.html', error=error) #Рендер на страницу
		#--------------------------------------------------------------------

	#------------------------------------------------------------------------

	return render_template('content/login.html', error=error) #Рендер на страницу
# ---------------------------------------------------------------------------

# ВЫВОД ТЕНДЕРОВ
@app.route('/show_tender', methods=['GET'])
def show_tender():
	if request.method == 'GET':
		bd_Session = sessionmaker(bind=engine)
		bd_session = bd_Session()	

		tenders = bd_session.query(Tender).filter().all()
		# oferta = bd_session.query(Oferta).filter().all()
		oferta = bd_session.query(Category).filter().all()
		bd_session.close()
		return render_template('content/index.html', tenders=tenders, oferts=oferta)
# ---------------------------------------------------------------------------

# СОЗДАНИЕ ТЕНДЕРА
@app.route('/new_tender', methods=['POST', 'GET'])
def new_tender():
    # error = None
    if request.method == 'POST':
        bd_Session = sessionmaker(bind=engine)
        bd_session = bd_Session()
        haract_arr = []
        for test in request.form:
            arr = {test: request.form[test]}
            haract_arr.append(arr)
        print(request.form)
        data = TenderBase(name=request.form['name'], view_product=request.form['view_product'],
                                  category=request.form['category'], discription=request.form['discription'],
                                  haract=str(haract_arr))

        tender = Tender(name=data.name, view_product=data.view_product,
                        category=data.category, discription=data.discription,
                        haract=data.haract, user=session['user_id'])

        bd_session.add(tender)
        bd_session.commit()
        bd_session.close()
        return Response(status=200)
    else:
    	bd_Session = sessionmaker(bind=engine)
    	bd_session = bd_Session()
    	tenders = bd_session.query(Tender).filter(Tender.user == session['user_id']).all()
    	oferta = bd_session.query(Category).filter().all()
    	bd_session.close()
    	return render_template('content/add_tender.html', tenders=tenders, oferts=oferta)
# ---------------------------------------------------------------------------------------------------------------------------

# СОЗДАНИЕ ОФЕРТЫ
@app.route('/offer', methods=['POST', 'GET'])
def offer():
    error = None
    # Проверка типа запроса
    if request.method == 'POST':
        bd_Session = sessionmaker(bind=engine)
        bd_session = bd_Session()
        haract_arr = []
        print(request.form)
        arr_valid = ['image', 'name', 'view_product', 'category', 'model', 'manufacturer', 
        			'unit', 'country', 'vendore_code', 'region_postavka', 'start_date',
        			'end_date', 'start_delivery', 'end_delivery', 'start_count', 'end_count', 'nds', 'price_nds']
        new_mass = {}

        for valid in request.form:
        	if valid not in arr_valid:
        		new_mass[valid] = request.form[valid]
        
        data = OfferBase(image=request.form['image'], offer_name=request.form['name'],
                                 view_product=request.form['view_product'], category=request.form['category'],
                                 model=request.form['model'], manufacturer=request.form['manufacturer'],
                                 unit_izmerenie=request.form['unit'], country=request.form['country'],
                                 vendore_code=request.form['vendore_code'],
                                 region_postavka=request.form['region_postavka'],
                                 date_start=request.form['start_date'],
                                 date_end=request.form['end_date'], delivery_time_from=request.form['start_delivery'],
                                 delivery_time_to=request.form['end_delivery'],
                                 left_border_of_products=request.form['start_count'],
                                 right_border_of_products=request.form['end_count'], nds=request.form['nds'],
                                 cost_of_unit=request.form['price_nds'], user_id=session['user_id'], status="modering",
                                 haract=new_mass)

        oferta = Offer(image=data.image, offer_name=data.offer_name, view_product=request.form['view_product'],
                       category=data.category,
                       model=data.model, manufacturer=data.manufacturer,
                       unit_izmerenie=data.unit_izmerenie, country=data.country,
                       vendore_code=data.vendore_code,
                       region_postavka=data.region_postavka,
                       date_start=data.date_start,
                       date_end=data.date_end, delivery_time_from=data.delivery_time_from,
                       delivery_time_to=data.delivery_time_to,
                       left_border_of_products=data.left_border_of_products,
                       right_border_of_products=data.right_border_of_products, nds=data.nds,
                       cost_of_unit=data.cost_of_unit, user_id=data.user_id, status=data.status,
                       haract=data.haract)

        bd_session.add(oferta)
        bd_session.commit()
        bd_session.close()
        print(haract_arr)
        return Response(status=200)

    else:
        bd_Session = sessionmaker(bind=engine)
        bd_session = bd_Session()
        oferta = bd_session.query(Category).filter().all()
        bd_session.close()
        return render_template('content/offer.html', oferts=oferta)
# --------------------------------------------------------------------------------------------------------------------------------------

# КАБИНЕТ МОДЕРАТОРА
@app.route('/moder', methods=['POST', 'GET'])
def moder():
    error = None
    # Проверка типа запроса
    if request.method == 'POST':
    	print(request.form)
    	bd_Session = sessionmaker(bind=engine)
    	bd_session = bd_Session()
    	oferta = bd_session.query(Offer).filter(Offer.id == request.form['id']).update({"status":request.form['status']})
    	bd_session.commit()
    	bd_session.close()
    	return Response(status=200)
    else:
    	bd_Session = sessionmaker(bind=engine)
    	bd_session = bd_Session()
    	oferta = bd_session.query(Offer).filter(Offer.status == "modering").all()
    	bd_session.close()
    	return render_template('content/moderator.html', oferts=oferta)

# ВЫХОД
@app.route('/logout')
def logout():
	if session.permanent:
	    session.permanent = None
	    session['login_name'] = None
	    session['status_user'] = None
	    session['user_id'] = None
	    return redirect(url_for('login'))
	else:
		return Response(status=404)
# ---------------------------------------------------------------------------