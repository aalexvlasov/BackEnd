from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_BINDS'] = {
   'mortality1': 'sqlite:///mortality1.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Mortality1(db.Model):
    __bind_key__ = 'mortality1'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String)
    year = db.Column(db.Integer)
    week = db.Column(db.Integer)
    sex = db.Column(db.String)
    d14 = db.Column(db.Float)
    d64 = db.Column(db.Float)
    d74 = db.Column(db.Float)
    d84 = db.Column(db.Float)
    dp = db.Column(db.Float)
    dall = db.Column(db.Float)
    r14 = db.Column(db.Float)
    r64 = db.Column(db.Float)
    r74 = db.Column(db.Float)
    r84 = db.Column(db.Float)
    rp = db.Column(db.Float)
    rall = db.Column(db.Float)
    split = db.Column(db.Integer)
    #Были ли данные изначально разделены по нужным возрастным группам
    splitsex = db.Column(db.Integer)
    forecast = db.Column(db.Integer)
    #Прогнозы использовались для расчетов показателей смертности

    def __repr__(self):
        return '<Mortality1>' % self.id
    def __str__(self):
        return f"Mortality1({self.id, self.country, self.sex})"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<user{self.id}>"

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=6, max=100, message="Пароль должен быть от 6 до 100 символов")])
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    username = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=6, max=100, message="Пароль должен быть от 6 до 100 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=('POST', 'GET'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('lk', id_lk=current_user.id))
    form = RegisterForm()
    if form.validate_on_submit():
        try:

            hash = generate_password_hash(form.psw.data)
            u = User(username=form.username.data, email=form.email.data, psw=hash)
            db.session.add(u)
            db.session.flush()
            db.session.commit()
            user = User.query.filter_by(email=form.email.data).first()
            login_user(user)
            return redirect(url_for('lk', id_lk=current_user.id))

        except:
            db.session.rollback()
            flash("Ошибка добавления в БД")

        # здесь должна быть проверка корректности введенных данных
        # email должен быть уникальным
        # psw должен состоять из английских символов и разрешенных знаков
        # psw и psw2 должны должны совпадать
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.psw, request.form['psw']):
            login_user(user)
            return redirect(url_for('lk', id_lk=current_user.id))
        else:
            flash('Неверный email или пароль')

    return render_template('login.html', form=form)
# Проверить, чтобы id пользователя было доступно только ему.


@app.route('/lk/<id_lk>')
@login_required
def lk(id_lk):
    return render_template('lk.html', name=current_user.username, email=current_user.email, date=current_user.date)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/databases')
def databases():
    return render_template('databases.html')

@app.route('/databases/<name_db>')
def show_db(name_db):
    if name_db == "mortality":
        rows = Mortality1.query.limit(20).all()
        rows_new = [("id", "Страна", "Год", "Неделя", "Пол", "Кол-во смертей в неделю (0-14 л.)", "Кол-во смертей в неделю (15-64 л.)", "Кол-во смертей в неделю (65-74 л.)", "Кол-во смертей в неделю (75-84 л.)", "Кол-во смертей в неделю (85+ л.)", "Всего смертей", "Коэффициент смертности (0-14 л.)", "Коэффициент смертности (15-64 л.)", "Коэффициент смертности (65-74 л.)", "Коэффициент смертности (75-84 л.)", "Коэффициент смертности (85+ л.)", "Коэффициент смертности (Общий)", "Деление по возрасту", "Деление по полу", "Ипользование прогнозов" )] + [(row.id, row.country, row.year, row.week, row.sex, row.d14, row.d64, row.d74, row.d84, row.dp, row.dall, row.r14, row.r64, row.r74, row.r84, row.rp, row.rall, row.split, row.splitsex, row.forecast) for row in rows]
        return render_template('show_database.html', database_name="Mortality DB", db=rows_new)
    else:
        return "Нет такой бд"


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
