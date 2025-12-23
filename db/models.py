from . import db
from flask_login import UserMixin
from datetime import datetime

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(30), nullable = False, unique = True)
    password = db.Column(db.String(162), nullable = False)

class articles(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    login_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(50), nullable = False)
    article_text = db.Column(db.Text, nullable = False)
    is_favorite = db.Column(db.Boolean)
    is_public = db.Column(db.Boolean)
    likes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с пользователем
    user = db.relationship('users', backref=db.backref('articles', lazy=True))
    
    # Метод для поиска статей
    @staticmethod
    def search_articles(search_query, current_user_id=None, include_public=True):
        """
        Поиск статей по заголовку и тексту.
        
        Args:
            search_query: строка для поиска
            current_user_id: ID текущего пользователя (если авторизован)
            include_public: включать ли публичные статьи других пользователей
        """
        if not search_query or not search_query.strip():
            return []
        
        # Регистронезависимый поиск
        query = search_query.strip()
        
        # Базовый запрос
        base_query = articles.query
        
        # Если пользователь авторизован
        if current_user_id:
            # Сначала ищем свои статьи
            own_articles = base_query.filter(
                db.and_(
                    articles.login_id == current_user_id,
                    db.or_(
                        articles.title.ilike(f'%{query}%'),
                        articles.article_text.ilike(f'%{query}%')
                    )
                )
            )
            
            # Затем публичные статьи других пользователей
            if include_public:
                public_articles = base_query.filter(
                    db.and_(
                        articles.login_id != current_user_id,
                        articles.is_public == True,
                        db.or_(
                            articles.title.ilike(f'%{query}%'),
                            articles.article_text.ilike(f'%{query}%')
                        )
                    )
                )
                return own_articles.union(public_articles).all()
            else:
                return own_articles.all()
        
        # Для неавторизованных пользователей - только публичные статьи
        else:
            return base_query.filter(
                db.and_(
                    articles.is_public == True,
                    db.or_(
                        articles.title.ilike(f'%{query}%'),
                        articles.article_text.ilike(f'%{query}%')
                    )
                )
            ).all()
        