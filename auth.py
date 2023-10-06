from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = '1234'  # Defina uma chave secreta para a sessão
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


@app.route('/')
def main():
    return render_template('home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and check_password_hash(usuario.password, password):
            session['user_id'] = usuario.id
            return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        existing_user = Usuario.query.filter_by(username=username).first()

        if existing_user:
            return jsonify({'message': 'Usuário já existe!'})
        
        if password != confirm_password:
            return jsonify({'message': 'Senhas não coincidem!'})
        
        novo_usuario = Usuario(username=username, password=generate_password_hash(password))

        db.session.add(novo_usuario)
        try:
            db.session.commit()  # Tente executar o commit aqui
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()  # Em caso de erro, faça um rollback
            return jsonify({'message': 'Erro ao salvar no banco de dados: ' + str(e)})

    return render_template('cadastro.html')

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)