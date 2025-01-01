from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
import random
import os
from sqlalchemy import func, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# PostgreSQL 数据库配置
db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://mathuser:mathpassword@host.docker.internal:5432/mathworksheetdb')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)

# 初始化数据库
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户模型
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    worksheets = db.relationship('Worksheet', backref='user', lazy=True)

# 练习记录模型
class Worksheet(db.Model):
    __tablename__ = 'worksheets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_problems = db.Column(db.Integer)
    correct_problems = db.Column(db.Integer)
    total_time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    problems = db.relationship('WorksheetProblem', backref='worksheet', lazy=True)

# 练习问题模型
class WorksheetProblem(db.Model):
    __tablename__ = 'worksheet_problems'
    id = db.Column(db.Integer, primary_key=True)
    worksheet_id = db.Column(db.Integer, db.ForeignKey('worksheets.id'), nullable=False)
    problem = db.Column(db.String(100), nullable=False)
    user_answer = db.Column(db.String(50), nullable=True)
    correct_answer = db.Column(db.String(50), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

# 用户加载函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 数据库初始化函数
def init_db():
    try:
        with app.app_context():
            db.create_all()
            print(f"数据库初始化成功，连接地址：{db_uri}")
    except Exception as e:
        print(f"数据库初始化失败: {e}")

# 在应用启动时尝试初始化数据库
try:
    init_db()
except Exception as e:
    print(f"应用启动时发生错误: {e}")

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # 验证邮箱
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError:
            return jsonify({'error': '无效的邮箱地址'}), 400

        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已被使用'}), 400

        # 创建新用户
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password_hash=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': '注册成功'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': '注册失败，请稍后重试'}), 500

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'message': '登录成功'}), 200
        else:
            return jsonify({'error': '用户名或密码错误'}), 401

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/start_worksheet', methods=['POST'])
@login_required
def start_worksheet():
    # 获取用户输入
    num_problems = int(request.json.get('num_problems', 10))
    max_number = int(request.json.get('max_number', 100))
    selected_operations = request.json.get('operations', ['+', '-', '*', '/'])
    allow_negative = request.json.get('allow_negative', False)
    
    # 生成数学练习算式
    problems = []
    
    for _ in range(num_problems):
        num1 = random.randint(1, max_number)
        num2 = random.randint(1, max_number)
        operation = random.choice(selected_operations)
        
        # 根据运算符生成算式和结果
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            # 是否允许负数结果
            if not allow_negative and num1 < num2:
                num1, num2 = num2, num1
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        else:  # '/'
            # 确保除法有整数结果
            if num1 < num2:
                num1, num2 = num2, num1
            # 确保能整除
            num1 = num2 * random.randint(1, max_number // num2)
            result = num1 // num2
        
        problem = f"{num1} {operation} {num2} = "
        problems.append({
            'problem': problem,
            'result': result
        })
    
    # 将问题存储在会话中
    session['problems'] = problems
    session['current_problem_index'] = 0
    session['user_answers'] = []
    
    # 返回第一个问题
    return jsonify({
        'problem': problems[0]['problem'],
        'total_problems': len(problems)
    })

@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    user_answer = request.json.get('answer')
    
    # 获取当前问题和正确答案
    problems = session.get('problems', [])
    current_index = session.get('current_problem_index', 0)
    
    if current_index >= len(problems):
        return jsonify({'error': '练习已完成'})
    
    correct_result = problems[current_index]['result']
    is_correct = str(user_answer).strip() == str(correct_result)
    
    # 记录用户答案
    user_answers = session.get('user_answers', [])
    user_answers.append({
        'problem': problems[current_index]['problem'],
        'user_answer': user_answer,
        'correct_answer': correct_result,
        'is_correct': is_correct
    })
    session['user_answers'] = user_answers
    
    # 移动到下一题
    session['current_problem_index'] += 1
    
    # 检查是否完成所有题目
    if session['current_problem_index'] >= len(problems):
        # 保存练习记录到数据库
        total_problems = len(problems)
        correct_problems = sum(1 for answer in user_answers if answer['is_correct'])
        
        worksheet = Worksheet(
            user_id=current_user.id,
            total_problems=total_problems,
            correct_problems=correct_problems,
            total_time=session.get('total_time', 0)
        )
        db.session.add(worksheet)
        db.session.flush()  # 获取新创建的worksheet的ID
        
        # 保存每个问题的详细信息
        for answer in user_answers:
            worksheet_problem = WorksheetProblem(
                worksheet_id=worksheet.id,
                problem=answer['problem'],
                user_answer=str(answer['user_answer']),
                correct_answer=str(answer['correct_answer']),
                is_correct=answer['is_correct']
            )
            db.session.add(worksheet_problem)
        
        db.session.commit()
        
        # 清理会话
        session.pop('problems', None)
        session.pop('current_problem_index', None)
        session.pop('user_answers', None)
        
        return jsonify({
            'completed': True,
            'total_problems': total_problems,
            'correct_count': correct_problems,
            'problems': user_answers
        })
    
    # 返回下一题
    return jsonify({
        'next_problem': problems[session['current_problem_index']]['problem'],
        'current_problem_number': session['current_problem_index'] + 1,
        'incorrect': not is_correct
    })

@app.route('/history')
@login_required
def worksheet_history():
    # 按日期汇总练习记录
    daily_summary = db.session.query(
        func.date_trunc('day', Worksheet.created_at).label('date'),
        func.sum(Worksheet.total_problems).label('total_problems'),
        func.sum(Worksheet.correct_problems).label('correct_problems'),
        func.count(Worksheet.id).label('worksheet_count')
    ).filter(
        Worksheet.user_id == current_user.id,
        Worksheet.created_at >= func.current_date() - text("interval '30 days'")
    ).group_by(func.date_trunc('day', Worksheet.created_at)) \
     .order_by(func.date_trunc('day', Worksheet.created_at).desc()) \
     .all()

    # 准备每日汇总数据
    daily_history = []
    for record in daily_summary:
        daily_history.append({
            'date': record.date.strftime('%Y-%m-%d'),
            'total_problems': record.total_problems,
            'correct_problems': record.correct_problems,
            'worksheet_count': record.worksheet_count,
            'accuracy': f"{record.correct_problems / record.total_problems * 100:.2f}%" if record.total_problems > 0 else "0%"
        })

    # 获取详细的每次练习记录
    worksheets = Worksheet.query.filter_by(user_id=current_user.id).order_by(Worksheet.created_at.desc()).all()
    
    detailed_history = []
    for worksheet in worksheets:
        # 获取每个练习的详细题目
        problems = WorksheetProblem.query.filter_by(worksheet_id=worksheet.id).all()
        
        detailed_history.append({
            'id': worksheet.id,
            'total_problems': worksheet.total_problems,
            'correct_problems': worksheet.correct_problems,
            'total_time': worksheet.total_time,
            'created_at': worksheet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'accuracy': f"{worksheet.correct_problems / worksheet.total_problems * 100:.2f}%" if worksheet.total_problems > 0 else "0%",
            'problems': [
                {
                    'problem': problem.problem,
                    'user_answer': problem.user_answer,
                    'correct_answer': problem.correct_answer,
                    'is_correct': problem.is_correct
                } for problem in problems
            ]
        })
    
    return render_template('history.html', 
                           daily_history=daily_history, 
                           detailed_history=detailed_history)

@app.route('/history/daily/<date>')
@login_required
def daily_worksheet_history(date):
    # 获取指定日期的所有练习记录
    worksheets = Worksheet.query.filter(
        Worksheet.user_id == current_user.id,
        func.date_trunc('day', Worksheet.created_at) == date
    ).order_by(Worksheet.created_at.desc()).all()
    
    # 准备详细记录
    detailed_history = []
    for worksheet in worksheets:
        # 获取每个练习的详细题目
        problems = WorksheetProblem.query.filter_by(worksheet_id=worksheet.id).all()
        
        detailed_history.append({
            'id': worksheet.id,
            'total_problems': worksheet.total_problems,
            'correct_problems': worksheet.correct_problems,
            'total_time': worksheet.total_time,
            'created_at': worksheet.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'accuracy': f"{worksheet.correct_problems / worksheet.total_problems * 100:.2f}%" if worksheet.total_problems > 0 else "0%",
            'problems': [
                {
                    'problem': problem.problem,
                    'user_answer': problem.user_answer,
                    'correct_answer': problem.correct_answer,
                    'is_correct': problem.is_correct
                } for problem in problems
            ]
        })
    
    return render_template('daily_history.html', 
                           date=date, 
                           detailed_history=detailed_history)

@app.route('/history/chart_data')
@login_required
def history_chart_data():
    # 获取最近30天的练习数据
    daily_summary = db.session.query(
        func.date_trunc('day', Worksheet.created_at).label('date'),
        func.sum(Worksheet.total_problems).label('total_problems'),
        func.sum(Worksheet.correct_problems).label('correct_problems'),
        func.count(Worksheet.id).label('worksheet_count')
    ).filter(
        Worksheet.user_id == current_user.id,
        Worksheet.created_at >= func.current_date() - text("interval '30 days'")
    ).group_by(func.date_trunc('day', Worksheet.created_at)) \
     .order_by(func.date_trunc('day', Worksheet.created_at).desc()) \
     .all()

    # 准备图表数据
    chart_data = {
        'labels': [],
        'total_problems': [],
        'accuracy_rates': []
    }

    for record in daily_summary:
        chart_data['labels'].append(record.date.strftime('%Y-%m-%d'))
        chart_data['total_problems'].append(record.total_problems)
        
        # 计算正确率
        accuracy = (record.correct_problems / record.total_problems * 100) if record.total_problems > 0 else 0
        chart_data['accuracy_rates'].append(round(accuracy, 2))

    return jsonify(chart_data)

if __name__ == '__main__':
    # 生产环境使用 gunicorn，这里仅用于开发
    app.run(host='0.0.0.0', port=8090, debug=False)
