from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g, current_app as app
from models.usuarios import Usuario, RoleEnum
from database import db
import secrets

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = Usuario.query.get(user_id)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash("Debes estar conectado para acceder a esta página", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash("Debes estar conectado para acceder a esta página", "error")
            return redirect(url_for('auth.login'))
        if g.user.role != 'admin':
            flash("No tienes permisos para acceder a esta página", "error")
            return redirect(url_for('tu_mundo'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        error = None
        
        if not username:
            error = 'El nombre de usuario es requerido.'
        elif not email:
            error = 'El email es requerido.'
        elif not password:
            error = 'La contraseña es requerida.'
        elif password != password_confirm:
            error = 'Las contraseñas no coinciden.'
        
        if error is None:
            try:
                user = Usuario(username=username, email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                app.logger.info(f"Nuevo usuario registrado localmente: {username} ({email})")
                flash("Registro exitoso. Por favor inicia sesión.", "success")
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                app.logger.warning(f"Error en registro: El email/usuario {email} ya existe.")
                error = 'El nombre de usuario o email ya existe.'
        
        if error:
            flash(error, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        error = None
        user = Usuario.query.filter_by(email=email).first()
        
        if user is None:
            error = 'Email no encontrado.'
            app.logger.warning(f"Intento de login fallido: Email {email} no encontrado.")
        elif not user.check_password(password):
            error = 'Contraseña incorrecta.'
            app.logger.warning(f"Intento de login fallido: Contraseña incorrecta para {email}.")
        
        if error is None:
            session.clear()
            session['user_id'] = user.id
            app.logger.info(f"Usuario {user.username} ha iniciado sesión correctamente.")
            flash(f'Bienvenido, {user.username}!', 'success')
            return redirect(url_for('tu_mundo'))
        
        flash(error, 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    app.logger.info(f"Sesión cerrada")
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('home'))