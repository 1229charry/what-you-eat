from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    health_goal = db.Column(db.String(50))  # 减脂/增肌/养生
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    diet_records = db.relationship('DietRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'gender': self.gender,
            'health_goal': self.health_goal
        }


# 食物模型
class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50))  # 谷物、蛋白质、蔬菜等
    calories = db.Column(db.Float)  # 每100g的热量
    protein = db.Column(db.Float)  # 蛋白质(g)
    fat = db.Column(db.Float)  # 脂肪(g)
    carbs = db.Column(db.Float)  # 碳水化合物(g)
    fiber = db.Column(db.Float)  # 纤维素(g)
    
    # 关系
    recipes = db.relationship('RecipeFood', backref='food', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'calories': self.calories,
            'protein': self.protein,
            'fat': self.fat,
            'carbs': self.carbs,
            'fiber': self.fiber
        }


# 菜谱模型
class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cuisine = db.Column(db.String(50))  # 菜系
    difficulty = db.Column(db.String(20))  # 简单/中等/困难
    cook_time = db.Column(db.Integer)  # 分钟
    servings = db.Column(db.Integer)  # 人数
    
    # 关系
    foods = db.relationship('RecipeFood', backref='recipe', lazy=True, cascade='all, delete-orphan')
    diet_records = db.relationship('DietRecord', backref='recipe', lazy=True)
    ratings = db.relationship('RecipeRating', backref='recipe', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cuisine': self.cuisine,
            'difficulty': self.difficulty,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'foods': [rf.to_dict() for rf in self.foods]
        }
    
    def get_nutrition(self):
        """计算整道菜的营养信息"""
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_fiber = 0
        
        for rf in self.foods:
            total_calories += rf.quantity * rf.food.calories / 100
            total_protein += rf.quantity * rf.food.protein / 100
            total_fat += rf.quantity * rf.food.fat / 100
            total_carbs += rf.quantity * rf.food.carbs / 100
            total_fiber += rf.quantity * rf.food.fiber / 100
        
        return {
            'calories': round(total_calories, 1),
            'protein': round(total_protein, 1),
            'fat': round(total_fat, 1),
            'carbs': round(total_carbs, 1),
            'fiber': round(total_fiber, 1)
        }


# 菜谱和食物的关系
class RecipeFood(db.Model):
    __tablename__ = 'recipe_foods'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Float)  # 克数
    
    def to_dict(self):
        return {
            'food_name': self.food.name,
            'quantity': self.quantity,
            'unit': 'g'
        }


# 饮食记录模型
class DietRecord(db.Model):
    __tablename__ = 'diet_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    meal_type = db.Column(db.String(20))  # 早餐/午餐/晚餐/零食
    quantity = db.Column(db.Float, default=1)  # 份数
    eaten_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # 关系
    feedbacks = db.relationship('Feedback', backref='diet_record', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        nutrition = self.recipe.get_nutrition() if self.recipe else {}
        return {
            'id': self.id,
            'recipe_name': self.recipe.name if self.recipe else 'Unknown',
            'meal_type': self.meal_type,
            'quantity': self.quantity,
            'eaten_at': self.eaten_at.isoformat(),
            'nutrition': nutrition,
            'notes': self.notes
        }


# 反馈模型
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    diet_record_id = db.Column(db.Integer, db.ForeignKey('diet_records.id'), nullable=False)
    
    # 味道评分 (1-5)
    taste_score = db.Column(db.Integer)
    # 舒适度评分 (1-5) - 消化舒适度
    comfort_score = db.Column(db.Integer)
    # 能量评分 (1-5) - 吃完后的精力水平
    energy_score = db.Column(db.Integer)
    
    # 症状反应
    has_allergy = db.Column(db.Boolean, default=False)
    symptoms = db.Column(db.String(200))  # 过敏、腹胀、疲劳等
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipe_name': self.diet_record.recipe.name if self.diet_record.recipe else 'Unknown',
            'taste_score': self.taste_score,
            'comfort_score': self.comfort_score,
            'energy_score': self.energy_score,
            'has_allergy': self.has_allergy,
            'symptoms': self.symptoms,
            'created_at': self.created_at.isoformat()
        }


# 菜谱评分模型
class RecipeRating(db.Model):
    __tablename__ = 'recipe_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    rating = db.Column(db.Float)  # 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
