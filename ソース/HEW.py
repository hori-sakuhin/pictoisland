from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
import uuid
from datetime import date
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "secret"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="your database account",
        password="your database password",
        database="pictoisland"
    )




@app.route("/")
def index_page():
    return render_template("index.html")

#-------------------------------------------------------
# アカウント作成画面
#-------------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM Accountdata WHERE email=%s",
            (email,)
        )
        if cursor.fetchone():
            flash("このメールアドレスは既に登録されています")
            return redirect(url_for("signup"))

        cursor.execute(
            "INSERT INTO Accountdata (email, username, password_hash) VALUES (%s, %s, %s)",
            (email, username, password_hash)
        )
        
        conn.commit()
        
        session["user_id"] = cursor.lastrowid

        cursor.close()
        conn.close()

        return redirect(url_for("home_page"))

    return render_template("signup.html")



@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT id, password_hash FROM Accountdata WHERE email = %s",
        (email,)
    )
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        return redirect(url_for("home_page"))

    flash("メールアドレスかパスワードが違います")
    return redirect(url_for("index_page"))



#-------------------------------------------------------
# ホーム画面
#-------------------------------------------------------

@app.route("/home.html", methods=["GET", "POST"])
def home_page():

    if "user_id" not in session:
        return redirect(url_for("index_page"))

    target_user_id = request.args.get("user_id", type=int)

    if target_user_id is None:
        target_user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST" and target_user_id == session["user_id"]:
        selected_island = request.form.get("island")

        if selected_island:
            cur.execute("""
                UPDATE Accountdata
                SET island_image=%s
                WHERE id=%s
            """, (selected_island, session["user_id"]))
            conn.commit()

    cur.execute("""
        SELECT id, username, island_name, island_theme, island_image, house_image
        FROM Accountdata
        WHERE id=%s
    """, (target_user_id,))
    user = cur.fetchone()

    cur.execute("""
        SELECT image_path
        FROM posts
        WHERE user_id=%s
        AND DATE(created_at)=CURDATE()
        ORDER BY created_at DESC
        LIMIT 1
    """, (target_user_id,))
    post = cur.fetchone()

    cur.close()
    conn.close()    

    return render_template(
        "home.html",
        user=user,
        post=post if post else None,
        island_image=user["island_image"] if user and user["island_image"] else None,
        house_image=user["house_image"] if user and user["house_image"] else None,
        is_owner=(target_user_id == session["user_id"])
    )
# 家、美術館にページ内リンク、ページ外リンクを設定しアイコンクリックで島内のどこにあるかを指すようにする

# 島のビジュアル変更は、ページ内に収める。島の画像を三択くらいで選ばせ、変更した内容を保存できるようにする

# 24時間以内に投稿された画像があるのか、あったらその画像を表示、なければメッセージを表示


#-------------------------------------------------------
# 新規投稿画面
#-------------------------------------------------------

@app.route("/newpost", methods=["GET", "POST"])
def newpost():
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    if request.method == "POST":

        image = request.files["image"]

        if image and image.filename != "":

            safe_name = secure_filename(image.filename)
            ext = os.path.splitext(safe_name)[1]
            filename = str(uuid.uuid4()) + ext

            upload_folder = os.path.join(app.root_path, "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)

            save_path = os.path.join(upload_folder, filename)
            image.save(save_path)

            image_path = "uploads/" + filename

            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO posts (user_id, image_path)
                VALUES (%s, %s)
                """,
                (session["user_id"], image_path)
            )
            conn.commit()
            cur.close()
            conn.close()

            
            return redirect(url_for("home_page"))

        else:
            flash("画像を選択してください")

    return render_template("newpost.html")
#-------------------------------------------------------
# 家表示画面
#-------------------------------------------------------

@app.route("/house", methods=["GET", "POST"])
def house_page():
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":

        image = request.files.get("house_image")

        if image and image.filename != "":

            safe_name = secure_filename(image.filename)
            ext = os.path.splitext(safe_name)[1]
            filename = str(uuid.uuid4()) + ext

            upload_folder = os.path.join(app.root_path, "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)

            save_path = os.path.join(upload_folder, filename)
            image.save(save_path)

            image_path = "uploads/" + filename

            cur.execute("""
                UPDATE Accountdata
                SET house_image=%s
                WHERE id=%s
            """, (image_path, session["user_id"]))

            conn.commit()
            flash("家の画像を変更しました！")
            return redirect(url_for("house_page"))

    cur.execute("""
        SELECT image_path
        FROM posts
        WHERE user_id=%s
        AND DATE(created_at)=CURDATE()
        ORDER BY created_at DESC
        LIMIT 1
    """, (session["user_id"],))

    today_post = cur.fetchone()

    cur.execute("""
        SELECT house_image
        FROM Accountdata
        WHERE id=%s
    """, (session["user_id"],))

    user = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "house.html",
        today_post=today_post,
        house_image=user["house_image"] if user else None
    )

#-------------------------------------------------------
# 美術館表示画面
#-------------------------------------------------------

@app.route("/museum")
def museum_page():
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    offset = request.args.get("offset", 0, type=int)

    cur.execute("""
        SELECT COUNT(*) as count
        FROM posts
        WHERE user_id=%s
    """, (session["user_id"],))
    total = cur.fetchone()["count"]

    cur.execute("""
        SELECT image_path, created_at
        FROM posts
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT 1 OFFSET %s
    """, (session["user_id"], offset))

    post = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "museum.html",
        post=post,
        offset=offset,
        total=total
    )


#-------------------------------------------------------
# ユーザー検索画面
#-------------------------------------------------------


# ユーザー名で検索できるようにする
# 他ユーザーの情報をデータベースから取得し、サムネ画像、島名、テーマ、ユーザー名を表示する
# カードクリックでその人の島に行けるようにする。（島の情報のみを表示）
@app.route("/search")
def search_page():
    keyword = request.args.get("keyword", "")
    my_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    

    if keyword:
        cursor.execute("""
            SELECT 
                a.id,
                a.username,
                a.island_name,
                a.island_theme,
                a.icon_path,
                CASE 
                    WHEN f.id IS NULL THEN 0
                    ELSE 1
                END AS is_following
            FROM accountdata a
            LEFT JOIN follows f
                ON f.followed_id = a.id
                AND f.follower_id = %s
            WHERE a.username LIKE %s
        """, (my_id, f"%{keyword}%"))

        users = cursor.fetchall()

        recommend_users = []

    else:
        users = []


        cursor.execute("""
            SELECT id, username, island_name, island_theme, icon_path
            FROM accountdata
            WHERE id != %s
            ORDER BY RAND()
            LIMIT 3
        """, (my_id,))

        recommend_users = cursor.fetchall()
        print("recommend_users:", recommend_users)


    return render_template(
        "search.html",
        users=users,
        recommend_users=recommend_users,
        keyword=keyword,
        my_id=my_id
    )

@app.route("/follow/<int:user_id>", methods=["POST"])
def follow(user_id):
    my_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM follows WHERE follower_id=%s AND followed_id=%s",
        (my_id, user_id)
    )
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "DELETE FROM follows WHERE follower_id=%s AND followed_id=%s",
            (my_id, user_id)
        )
    else:
        cursor.execute(
            "INSERT INTO follows (follower_id, followed_id, created_at) VALUES (%s, %s, NOW())",
            (my_id, user_id)
        )

    conn.commit()
    return redirect(url_for("search_page"))


#-------------------------------------------------------
# グループ画面
#-------------------------------------------------------

@app.route("/group.html")
def group_page():
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT g.id, g.group_name, g.island_image
        FROM usergroups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
    """, (session["user_id"],))

    groups = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("group.html", groups=groups)

# １．　島作成段階

# １－１　グループメンバーを相互フォロー中の中から選択し、選択し終えたら、島作成ボタンをクリック

# １－２　島名を入力　島のビジュアルを決める

# ２．　島選択段階

# ２－１　複数個ある場合にどの島にアクセスするかを選択させる

# ３．　インフォ

# ３－１　もしグループメンバーの誰かが新しく投稿をしていたら、「○○が新しい投稿をしました。」と表示
# 　　　　なければ「お知らせはありません」

# ４．　ページ内リンク

# ４－１　それぞれの家がわかるように色分けをする　家クリックで島内のどこにあるかわかりやすくする

# ４－２　美術館にはそのグループメンバーとの思い出画像を展示するため、そのユーザーのハイライト
# 　　　　から選択できるようにする

#-------------------------------------------------------
# グループ作成画面
#-------------------------------------------------------

@app.route("/group_create", methods=["GET", "POST"])
def group_create():
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    if request.method == "POST":
        group_name = request.form["group_name"]
        island_image = request.form.get("island")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO usergroups (group_name, island_image, created_by)
            VALUES (%s, %s, %s)
        """, (group_name, island_image, session["user_id"]))

        group_id = cur.lastrowid

        cur.execute("""
            INSERT INTO group_members (group_id, user_id)
            VALUES (%s, %s)
        """, (group_id, session["user_id"]))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("group_page"))

    return render_template("group_create.html")

#-------------------------------------------------------
# グループ島画面
#-------------------------------------------------------
@app.route("/group/<int:group_id>", methods=["GET", "POST"])
def group_island(group_id):

    if "user_id" not in session:
        return redirect(url_for("index_page"))
    
    

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        selected_island = request.form.get("island")
        if selected_island:
            cur.execute("""
                UPDATE usergroups
                SET island_image=%s
                WHERE id=%s
            """, (selected_island, group_id))
            conn.commit()
    if request.method == "POST":
        print("POST受信:", request.form)

        selected_island = request.form.get("island")
        print("選択された島:", selected_island)

    cur.execute("""
        SELECT id, group_name, island_image
        FROM usergroups
        WHERE id=%s
    """, (group_id,))   
    group = cur.fetchone()

    cur.execute("""
        SELECT a.id, a.username, a.house_image
        FROM Accountdata a
        JOIN group_members gm ON a.id = gm.user_id
        WHERE gm.group_id=%s
    """, (group_id,))
    members = cur.fetchall()

    cur.execute("""
        SELECT a.username, p.image_path, p.user_id
        FROM posts p
        JOIN Accountdata a ON p.user_id = a.id
        JOIN group_members gm ON gm.user_id = a.id
        WHERE gm.group_id = %s
        AND DATE(p.created_at) = CURDATE()
        AND a.id != %s
        ORDER BY p.created_at DESC
    """, (group_id, session["user_id"]))

    today_posts = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "group_island.html",
        group=group,
        members=members,
        today_posts=today_posts)
#-------------------------------------------------------
# グループ島美術館画面
#-------------------------------------------------------

@app.route("/group/<int:group_id>/museum", methods=["GET", "POST"])
def group_museum(group_id):

    if "user_id" not in session:
        return redirect(url_for("index_page"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":

        file = request.files.get("image")
        comment = request.form.get("comment")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)

            image_path = f"uploads/{filename}"

            cur.execute("""
                INSERT INTO group_posts
                (group_id, user_id, image_path, comment)
                VALUES (%s, %s, %s, %s)
            """, (group_id, session["user_id"], image_path, comment))

            conn.commit()

    cur.execute("""
        SELECT gp.*, a.username
        FROM group_posts gp
        JOIN Accountdata a ON gp.user_id = a.id
        WHERE gp.group_id=%s
        ORDER BY gp.created_at DESC
    """, (group_id,))

    posts = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("group_museum.html",
                           posts=posts,
                           group_id=group_id)



#-------------------------------------------------------
# グループメンバー追加画面
#-------------------------------------------------------

@app.route("/group/<int:group_id>/add_member", methods=["POST"])
def add_group_member(group_id):
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    my_id = session["user_id"]
    username = request.form.get("username")

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT id FROM Accountdata WHERE username=%s",
        (username,)
    )
    user = cur.fetchone()

    if not user:
        return redirect(url_for("group_island", group_id=group_id))

    target_id = user["id"]

    cur.execute("""
        SELECT id FROM follows
        WHERE follower_id=%s AND followed_id=%s
    """, (my_id, target_id))

    if not cur.fetchone():
        return redirect(url_for("group_island", group_id=group_id))

    cur.execute("""
        SELECT id FROM group_members
        WHERE group_id=%s AND user_id=%s
    """, (group_id, target_id))

    if not cur.fetchone():
        cur.execute("""
            INSERT INTO group_members (group_id, user_id)
            VALUES (%s, %s)
        """, (group_id, target_id))
        conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("group_island", group_id=group_id))


#-------------------------------------------------------
# グループ退会画面
#-------------------------------------------------------

@app.route("/group/<int:group_id>/remove_member/<int:user_id>", methods=["POST"])
def remove_group_member(group_id, user_id):
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    if session["user_id"] != user_id:
        return redirect(url_for("group_island", group_id=group_id))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM group_members
        WHERE group_id=%s AND user_id=%s
    """, (group_id, user_id))
    conn.commit()

    cur.execute("""
        SELECT COUNT(*) FROM group_members
        WHERE group_id=%s
    """, (group_id,))
    count = cur.fetchone()[0]

    if count == 0:
        cur.execute("""
            DELETE FROM usergroups
            WHERE id=%s
        """, (group_id,))
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("group_page"))

    cur.close()
    conn.close()

    return redirect(url_for("group_island", group_id=group_id))


#-------------------------------------------------------
# プロフィール画面
#-------------------------------------------------------

@app.route("/prof/<int:user_id>")
def prof(user_id):

    from_search = request.args.get("from_search")
    

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT id, username, comment,island_theme, icon_path,is_public
        FROM Accountdata
        WHERE id=%s
    """, (user_id,))

    user = cur.fetchone()

    if not user:
        return "ユーザーが存在しません"

    is_following = None
    if "user_id" in session and session["user_id"] != user_id:
        cur.execute("""
            SELECT 1 FROM follows
            WHERE follower_id=%s AND followed_id=%s
        """, (session["user_id"], user_id))
        is_following = cur.fetchone()

    cur.execute("""
        SELECT COUNT(*) AS count
        FROM follows
        WHERE follower_id=%s
    """, (user_id,))
    follow_count = cur.fetchone()["count"]

    cur.execute("""
        SELECT COUNT(*) AS count
        FROM follows
        WHERE followed_id=%s
    """, (user_id,))
    follower_count = cur.fetchone()["count"]

    cur.execute("""
        SELECT a.id, a.username
        FROM follows f
        JOIN Accountdata a ON f.followed_id = a.id
        WHERE f.follower_id=%s
    """, (user_id,))
    follow_users = cur.fetchall()

    cur.execute("""
        SELECT a.id, a.username
        FROM follows f
        JOIN Accountdata a ON f.follower_id = a.id
        WHERE f.followed_id=%s
    """, (user_id,))
    follower_users = cur.fetchall()



    cur.close()
    conn.close()

    return render_template(
        "prof.html",
        from_search=from_search,
        user=user,
        is_following=is_following,
        follow_users=follow_users,
        follower_users=follower_users,
        follow_count=follow_count,
        follower_count=follower_count
    )




#-------------------------------------------------------
# プロフィール編集画面
#-------------------------------------------------------

@app.route("/prof_edit", methods=["GET", "POST"])
def prof_edit():
    if "user_id" not in session:
        return redirect(url_for("index_page"))

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":

        username = request.form["username"]
        comment = request.form["comment"]
        island_name = request.form["island_name"]
        island_theme = request.form["island_theme"]
        is_public = request.form.get("is_public")

        cur.execute("""
            SELECT icon_path
            FROM Accountdata
            WHERE id=%s
        """, (session["user_id"],))
        user = cur.fetchone()
        icon_path = user["icon_path"]

        file = request.files.get("icon")


        if file and file.filename != "":
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            icon_path = f"uploads/{filename}"

        cur.execute("""
            UPDATE Accountdata
            SET
                username=%s,
                comment=%s,
                island_name=%s,
                island_theme=%s,
                icon_path=%s,
                is_public=%s
            WHERE id=%s
        """,
        (username, comment, island_name, island_theme, icon_path, is_public, session["user_id"]))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("prof", user_id=session["user_id"]))

    cur.execute("""
        SELECT
            id,
            username,
            comment,
            island_name,
            island_theme,
            icon_path,
            is_public
        FROM Accountdata
        WHERE id=%s
    """, (session["user_id"],))

    user = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("prof_edit.html", user=user)






if __name__ == "__main__":
    app.run(debug=True)

