import os
import sys
import click
from flask import Flask, escape, render_template, request, flash, redirect, url_for
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'databases/data.db')

db = SQLAlchemy(app)

tb_movies = db.Table('tb_movies', 
                  db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                  )

class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    name = db.Column(db.String(20), nullable=False)  # 名字
    nick_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.String(4), default='male')
    city = db.Column(db.String(150), nullable=True)
    mobile = db.Column(db.String(11), nullable=False, comment='telephone')
    watched_movies = db.relationship('Movie', secondary=tb_movies, backref=db.backref('users', lazy='dynamic'))

class Movie(db.Model):  # 表名将会是 movie
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60), nullable=False)  # 电影标题
    year = db.Column(db.String(4), nullable=True)  # 电影年份
    content = db.Column(db.String(500), nullable=True)
    

# name = 'Nova Lu'
# movies = [
#     {'title': 'My Neighbor Totoro', 'year': '1988'},
#     {'title': 'Dead Poets Society', 'year': '1989'},
#     {'title': 'A Perfect World', 'year': '1993'},
#     {'title': 'Leon', 'year': '1994'},
#     {'title': 'Mahjong', 'year': '1996'},
#     {'title': 'Swallowtail Butterfly', 'year': '1996'},
#     {'title': 'King of Comedy', 'year': '1999'},
#     {'title': 'Devils on the Doorstep', 'year': '1999'},
#     {'title': 'WALL-E', 'year': '2008'},
#     {'title': 'The Pork of Music', 'year': '2012'},
# ]

@app.route('/index')
def hello():
    return '<h1>Hello Totoro!</h1><img src="https://39.99.218.12:8888/images/web_site/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)

@app.route('/')
def index():
    user = User.query.filter_by(name="Nova Lu").first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)

@app.route('/users')
def show_user():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/new_user', methods = ['GET', 'POST'])
def add_new_user():
    if request.method == 'POST':
      if not request.form['name'] or not request.form['nick_name'] or not request.form['mobile']:
        flash('Please enter all the fields', 'error')
      else:
        if request.form['watched_movies']:
            movie = Movie(title = request.form['watched_movies'], content = request.form['watched_movies'])
            db.session.add(movie)
            db.session.commit()
        user = User(request.form['name'], request.form['nick_name'],  request.form['age'], 
                    request.form['sex'], request.form['city'], request.form['mobile'], request.form['watched_movies'] )
        db.session.add(user)
        db.session.commit()
        flash('Record was successfully added')
        return redirect(url_for('index'))
    return render_template('new_user.html')

@app.route('/new_movie', methods = ['GET', 'POST'])
def new_movie():
    if request.method == 'POST':
      if not request.form['title'] or not request.form['content']:
        flash('Please enter all the fields', 'error')
      else:
        movie = User(request.form['title'], request.form['year'], request.form['content'])
        db.session.add(movie)
        db.session.commit()
        flash('Record was successfully added')
        return redirect(url_for('index'))
    return render_template('new_movie.html')
    

@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

if __name__=='__main__':
    app.run(debug=True)