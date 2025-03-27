from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from flask import Flask, render_template, redirect, url_for, flash ,request
from forms import RegisterForm, LoginForm  # forms.py에서 폼 가져오기
from models import Comment
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '아무_문자열_넣기'  # 보안 키 (세션에 필요)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 설정 추가
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB 제한
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# 유효한 파일 확장자 검사
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


db.init_app(app)
migrate = Migrate(app, db)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('회원가입 완료! 이제 로그인 해보세요.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('로그인 성공!', 'success')
            return redirect(url_for('home'))
        else:
            flash('아이디 또는 비밀번호가 잘못되었습니다.', 'danger')
    return render_template('login.html', form=form)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask_login import login_required, current_user

@app.route('/mypage')
@login_required
def mypage():
    return render_template('mypage.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('home'))

from models import Post
from flask_login import login_required, current_user
@app.route('/board')
def board():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('board.html', posts=posts)

@app.route('/board/write', methods=['GET', 'POST'])
@login_required
def write():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_file = request.files.get('image')
        filename = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

        new_post = Post(title=title, content=content, image=filename, author_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('board'))

    return render_template('write.html')


@app.route('/board/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('로그인 후 댓글을 작성할 수 있습니다.', 'warning')
            return redirect(url_for('login'))
        content = request.form['content']
        new_comment = Comment(content=content, author_id=current_user.id, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('post_detail.html', post=post)

@app.route('/board/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('board'))

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('edit.html', post=post)

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes = (post.likes or 0) + 1  # ← None이면 0으로 처리
    db.session.commit()
    return redirect(url_for('board'))

@app.route('/board/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author_id != current_user.id:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('board'))

    db.session.delete(post)
    db.session.commit()
    flash('게시글이 삭제되었습니다.', 'success')
    return redirect(url_for('board'))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.author_id != current_user.id:
        flash('댓글 삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('post_detail', post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()
    flash('댓글이 삭제되었습니다.', 'info')
    return redirect(url_for('post_detail', post_id=comment.post_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

