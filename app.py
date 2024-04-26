import os
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from flask import Flask, render_template
import yfinance as yf
import plotly.express as px


from werkzeug.security import generate_password_hash, check_password_hash

from flask import send_from_directory

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Optional: configure session lifetime
db_path = os.path.join(os.path.dirname(__file__), 'database/data.db')

DB_URI = 'sqlite:///{}'.format(db_path)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    visible = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer)

    def __repr__(self):
        return f"Blog('{self.title}', '{self.created_at}')"

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (current_user.is_authenticated):
        return redirect(url_for('blog_list'))
    if (request.method == 'POST'):
        email = request.form.get('email')
        password = request.form.get('password')
        if not password:
            flash(message="Password empty", category='error')
            return render_template('login.html')
        
        # Check db to see if user exists & if password is correct
        user = User.query.filter(or_(User.email==email, User.user_name==email)).first()
        if user:
            if user.password == password:
            # if check_password_hash(user.password, password):
                session.permanent = True
                login_user(user=user, remember=True)
                return redirect(url_for('blog_list'))
            else:
                message = 'Invalid credential used'
                flash(message=message, category='error')
        else:
            message = f'User not found'
            flash(message, category='error')
    
    return render_template('login.html', user=current_user)

@app.route('/blog_list')
@login_required
def blog_list():
    # Example: Fetching blog posts from a database (pseudo-code)
    #blog_posts = BlogPost.query.all()
    #return render_template("blog_list.html", blog_posts=blog_posts)
    return render_template("blog_list.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/get_radar')
def get_radar():
    return send_from_directory('docs', 'index.html')

@app.route('/docs/<path:path>')
def send_docs(path):
    return send_from_directory('docs', path)

@app.route('/dashboard')
def dashboard():
    posts = Blog.query.filter_by(visible=1).order_by(Blog.created_at.desc()).all()
    return render_template('dashboard.html', posts=posts)


#======= financial things =====

def get_stock_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def plot_stocks(data_dict):
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=[f"{title} Closing Prices" for title in data_dict.keys()])

    for i, (title, df) in enumerate(data_dict.items(), start=1):
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Close'], name=title),
            row=i, col=1
        )

    fig.update_layout(height=1200, title_text="Financial Data Over Time")
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Close Price')
    return fig.to_html()

@app.route('/visualize_financials')
def visualize_financials():
    sp500_data = get_stock_data("SPY")
    oil_data = get_stock_data("USO")
    gold_data = get_stock_data("GLD")
    
    data_dict = {
        "S&P 500": sp500_data,
        "Oil (USO)": oil_data,
        "Gold (GLD)": gold_data
    }

    graph_html = plot_stocks(data_dict)
    return render_template('financials.html', graph_html=graph_html)



if __name__ == '__main__':
    #db.create_all()  # Ensure all tables are created
    app.run(debug=True)
