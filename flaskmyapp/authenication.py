from flask import Flask, redirect, render_template, url_for, request, flash, Blueprint, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from argon2 import PasswordHasher
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, UserMixin
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length
from datetime import datetime
from logging import getLogger
from . import app, db, login_manager
    
bp = Blueprint('authenication', __name__) 
     
ph = PasswordHasher()

csrf = CSRFProtect
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)

logger = getLogger(__name__)
def setloglevel():
    logger.debug("debug_message_from_authenication.py")
    logger.info("info_message_from_authenication.py")
    logger.warning("warn_message_from_authenication.py!")

class User(db.Model, UserMixin):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now,
                           onupdate=datetime.now)

class chatrooms(db.Model):
    __tablename__ = "chatrooms"
    chat_room_name = db.Column(db.String(100))
    chat_room_id = db.Column(db.Integer, primary_key=True)
    chat_room_identifer = (db.String(10))
    password = (db.String(51))

class SignUpForm(FlaskForm):
    username = StringField("ユーザー名",validators=[DataRequired("ユーザー名を入力してください"),Length(1, 250, "250文字以内で入力してください")])
    email = EmailField("メールアドレス",validators=[DataRequired("メールアドレスを入力してください"),Email("メールアドレスの形式で入力してください")])
    password = PasswordField("パスワード",validators=[DataRequired("パスワードを入力してください"),Length(10, 50, "10文字以上50文字以内で入力してください")])
    submit = SubmitField("新規登録")
    

class LoginForm(FlaskForm):
    email = EmailField("メールアドレス",validators=[DataRequired("メールアドレスを入力してください"),Email("メールアドレスの形式で入力してください")])
    password = PasswordField("パスワード", validators=[DataRequired("パスワードを入力してください")])
    submit = SubmitField("ログイン")

class EnterRoomForm(FlaskForm):
    chatroomname = StringField("ユーザー名",validators=[DataRequired("ルーム名を入力してください"),Length(1, 16, "16文字以内で入力してください")])
    password = PasswordField("パスワード",validators=[DataRequired("パスワードを入力してください"),Length(1, 50, "50文字以内で入力してください")])
    submit = SubmitField("入る")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@bp.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username = form.username.data,
            email = form.email.data,
            password = ph.hash(form.email.data),
        )
    #メールアドレスの重複をチェック
        existing_user = User.query.filter(User.email == form.email.data).first()
        if existing_user is not None:
            flash("すでに登録済みのメールアドレスです")
            return redirect(url_for("authenication.sign_up"))
    #ユーザー情報を登録する
        db.session.add(user)
        try:
            db.session.commit
        except Exception as e:
            print(f"OperationalError1: {e}")
        Password = ph.hash(form.password.data)
        print(Password)
#セッションに登録
        login_user(user)
        return redirect(url_for('my_web_app.create_chatroom'))
    """
        next_ = request.args.get("next")
        if next_ is None or not next_.startswith("/"):
            next_ = url_for("")
        return redirect(next_)
    """
    return render_template("auth/sign_up.html", form=form)


@bp.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
#メールアドレスを取得
        user = User.query.filter_by(User.email == form.email.data).first()
        if user is not None:
            hash = user.password
            print(hash)
#ユーザーとパスワードが一致する場合はログインを許可する
            if user is not None and ph.verify(hash, form.password.data):
                login_user(user)
                print("vertify")
                if ph.check_needs_rehash(hash):
                    db.set_password_hash_for_user(user, ph.hash(form.password.data))
                return redirect(url_for("my_web_app.create_chatroom"))   
            else:
                flash("正しいメールアドレスとパスワードを入力してください")
                return redirect(url_for('authenication.sign_in'))
        else:
            flash("正しいメールアドレスとパスワードを入力してください")
            return redirect(url_for('authenication.sign_in'))
    return render_template("auth/sign_in.html", form=form)

@bp.route("/", methods=["GET", "POST"])
#チャットルームに入るための認証
def enter_chatroom():
    form = EnterRoomForm()
    if form.validate_on_submit():
        new_table_name = form.chatroomname.data
        room = chatrooms.query.filter_by(chatrooms.chat_room_name == new_table_name).first()
        print(room)
        if room is not None:
            hash = room.password
            print(hash)
            if new_table_name is not None and ph.verify(hash, form.password.data):
                print("vertify!")
                session['entered_chatroom'] = new_table_name
                return redirect(url_for("my_web_app.chatroom", new_table_name = new_table_name))
            else:
                flash("正しいメールアドレスとパスワードを入力してください")
                return redirect(url_for('authenication.enter_chatroom'))
        else:
                flash("正しいルーム名とパスワードを入力してください")
                return redirect(url_for('authenication.enter_chatroom'))
    return render_template("index.html", form =form)
