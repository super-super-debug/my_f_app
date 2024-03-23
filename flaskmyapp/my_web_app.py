from flask import Flask, render_template, request, url_for, redirect, Blueprint, flash, session
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length 
from argon2 import PasswordHasher
import pymysql
from logging import getLogger
from . import app

logger = getLogger(__name__)
def log():
    logger.debug("debug_message_from_my_web_app.py")
    logger.info("info_message_from_my_web_app.py")
    logger.warning("warn_message_from_my_web_app.py!")

def getconnection():
    return pymysql.connect(host = "localhost", port = int(3306), db = "My_chatrooms", user = "root", password = "Ichimura$2002",charset = "utf8mb4")

bp = Blueprint('my_web_app', __name__)   


csrf = CSRFProtect
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)

class ChatForm(FlaskForm):
    chat = StringField("chat", validators=[DataRequired("テキストを入力してください")])

class CreateForm(FlaskForm):
    chatroomname = StringField("チャットルーム名",validators=[DataRequired("ルーム名を入力してください"),Length(1, 16, "16文字以内で入力してください")])
    password = PasswordField("パスワード",validators=[DataRequired("パスワードを入力してください")])
    submit = SubmitField("作成")


@bp.route("/create_chatroom", methods=["GET", "POST"])

#チャットルームの作成のため、データベースにテーブルを作成しデータを取得、送信
def create_chatroom():
    form = CreateForm()
    new_table_name = ""
    new_table_url = "None"
    
    if form.validate_on_submit():
        connection = getconnection()
        cursor = connection.cursor()
        Password = ph.hash(form.password.data)
        print(Password)
        Chat_room_name = form.chatroomname.data
        print(Chat_room_name)
#チャットルーム名の重複をチェック
        existing_name_query = f"SELECT chat_room_name FROM chatrooms WHERE chat_room_name = '{Chat_room_name}';"
        cursor.execute(existing_name_query)
        existing_name = cursor.fetchone()
        if existing_name is not None:
            flash("すでにチャットルーム名が登録されています")
            return redirect(url_for("my_web_app.create_chatroom"))
#現在のテーブル数を取得  
        show_query = ("SHOW TABLES;")
        try:
            cursor.execute(show_query)
        except Exception as e:
            print(f"ShowQueryError: {e}")
        current_tables = cursor.fetchall()
        current_table_count = len(current_tables)
        print(current_table_count)        

#テーブル名を生成
        new_table_name = f'table_{current_table_count + 1}'
        print(new_table_name)

#プライマリーキーを兼ねるURLを生成
        new_table_url = f'{current_table_count + 1}'
        print(new_table_url)

#新しいテーブルを作成
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {new_table_name} (user_id INTEGER, user_name VARCHAR(255), chat TEXT, chat_id INTEGER AUTO_INCREMENT PRIMARY KEY, written_on DATE);"
        try:
            cursor.execute(create_table_sql)
        except Exception as e:
            print(f"OperationalError1: {e}")

# 作成したテーブルの情報をchatroomsテーブルに挿入"
        convert_query = (f"INSERT INTO chatrooms(chat_room_id,chat_room_identifier,chat_room_name,password) VALUES ({new_table_url},'{new_table_name}','{Chat_room_name}','{Password}');")
        try:
            cursor.execute(convert_query)
        except Exception as e:
            print(f"OperationalError2: {e}") 
        connection.commit()
        cursor.close()
        connection.close()
        session['entered_chatroom'] = new_table_url
        print(session)
        print(session.get("entered_chatroom"))
        return redirect(url_for('my_web_app.chatroom', new_table_url=new_table_url, form=form))
    else:
        return render_template("createchatroom.html", form=form) 

@bp.route("/chatroom/<new_table_url>", methods=["POST", "GET"])

def chatroom(new_table_url):
    form = ChatForm()
    connection = getconnection()
    cursor = connection.cursor()
    chat_room_name = None
    contents = None
    post = ""
    print(new_table_url)
    print(session.get("entered_chatroom"))
    if session.get("entered_chatroom") is not None and session.get("entered_chatroom") == new_table_url:
        if new_table_url:
            try:
                table_name_query = "SELECT chat_room_name FROM chatrooms WHERE chat_room_id = %s;"
                cursor.execute(table_name_query, (new_table_url,))
                chat_room_name = cursor.fetchone()

        #if chat_room_name is None:
            # chat_room_idが見つからない場合の処理
        #    return render_template("chatroom_not_found.html")

                toridasu_chats_query = f"SELECT user_name, chat FROM table_{new_table_url} LIMIT 35;"
                cursor.execute(toridasu_chats_query)
                contents = cursor.fetchall()
                print(contents)
                for content in contents:
                    print(content)
                if form.validate_on_submit():
                    kariname = session.get("user_name")
                    if kariname is not None:
                        name = kariname
                    else:
                        name = "Anonimus"
                print(name)
                post = form.chat.data
                add_chat = f"INSERT INTO table_{new_table_url}(chat,user_name) VALUES ('{post}','{name}');"
                cursor.execute(add_chat)
                connection.commit()

            except pymysql.Error as e:
                print(f"オペレーショナルエラーです!!: {e}")

            finally:
                try:
                    connection.commit()
                except pymysql.Error as e:
                    print(f"Commit Error: {e}")
                cursor.close()
                connection.close()

                return render_template("chatroom.html", chat_room_name=chat_room_name, contents=contents, post=post, form=form)
        else:
            return render_template("chatroom.html", chat_room_name=chat_room_name, form=form)
        print("cookie_error")
    else:
        return redirect(url_for("authenication.enter_chatroom"))

# 3./で情報を登録してもリダイレクト、バリデーションされず、その状態で新規登録のページに飛ぶと、チャット名が登録済みのやつと正しいパスを入力しろがバリデーションされる。