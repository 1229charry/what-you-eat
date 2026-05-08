from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

from models import db, User, Food, Recipe, RecipeFood, DietRecord, Feedback, RecipeRating
from recommender import FoodRecommender

app = Flask(__name__)

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

# 初始化
db.init_app(app)
CORS(app)
recommender = FoodRecommender()

# 创建表
with app.app_context():
    db.create_all()


# ============== 用户相关接口 ==============

@app.route('/api/users', methods=['POST'])
def create_user():
    """创建新用户"""
    data = request.get_json()
    
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            age=data.get('age'),
            gender=data.get('gender'),
            health_goal=data.get('health_goal')
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '用户创建成功',
            'data': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'msg': str(e)
        }), 400


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户信息"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    return jsonify({
        'code': 200,
        'data': user.to_dict()
    })


# ============== 食物相关接口 ==============

@app.route('/api/foods', methods=['GET'])
def list_foods():
    """获取所有食物列表"""
    foods = Food.query.all()
    return jsonify({
        'code': 200,
        'data': [f.to_dict() for f in foods]
    })


@app.route('/api/foods', methods=['POST'])
def create_food():
    """创建新食物"""
    data = request.get_json()
    
    try:
        food = Food(
            name=data['name'],
            category=data.get('category'),
            calories=data.get('calories'),
            protein=data.get('protein'),
            fat=data.get('fat'),
            carbs=data.get('carbs'),
            fiber=data.get('fiber')
        )
        db.session.add(food)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '食物创建成功',
            'data': food.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'msg': str(e)
        }), 400


# ============== 菜谱相关接口 ==============

@app.route('/api/recipes', methods=['GET'])
def list_recipes():
    """获取所有菜谱列表"""
    recipes = Recipe.query.all()
    return jsonify({
        'code': 200,
        'data': [r.to_dict() for r in recipes]
    })


@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """创建新菜谱"""
    data = request.get_json()
    
    try:
        recipe = Recipe(
            name=data['name'],
            description=data.get('description'),
            cuisine=data.get('cuisine'),
            difficulty=data.get('difficulty'),
            cook_time=data.get('cook_time'),
            servings=data.get('servings', 1)
        )
        
        # 添加食材
        for ingredient in data.get('ingredients', []):
            food = Food.query.get(ingredient['food_id'])
            if food:
                recipe_food = RecipeFood(
                    food_id=food.id,
                    quantity=ingredient['quantity']
                )
                recipe.foods.append(recipe_food)
        
        db.session.add(recipe)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '菜谱创建成功',
            'data': recipe.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'msg': str(e)
        }), 400


@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """获取菜谱详情"""
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        return jsonify({'code': 404, 'msg': '菜谱不存在'}), 404
    
    nutrition = recipe.get_nutrition()
    data = recipe.to_dict()
    data['nutrition'] = nutrition
    
    return jsonify({
        'code': 200,
        'data': data
    })


# ============== 饮食记录相关接口 ==============

@app.route('/api/users/<int:user_id>/diet-records', methods=['POST'])
def create_diet_record(user_id):
    """记录用户的饮食"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    data = request.get_json()
    
    try:
        record = DietRecord(
            user_id=user_id,
            recipe_id=data.get('recipe_id'),
            meal_type=data.get('meal_type'),
            quantity=data.get('quantity', 1),
            notes=data.get('notes')
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '饮食记录保存成功',
            'data': record.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'msg': str(e)
        }), 400


@app.route('/api/users/<int:user_id>/diet-records', methods=['GET'])
def list_diet_records(user_id):
    """获取用户的饮食记录"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    records = DietRecord.query.filter_by(user_id=user_id).order_by(DietRecord.eaten_at.desc()).all()
    
    return jsonify({
        'code': 200,
        'data': [r.to_dict() for r in records]
    })


# ============== 反馈相关接口 ==============

@app.route('/api/feedbacks', methods=['POST'])
def create_feedback():
    """提交饮食反馈"""
    data = request.get_json()
    
    try:
        feedback = Feedback(
            user_id=data['user_id'],
            diet_record_id=data['diet_record_id'],
            taste_score=data.get('taste_score'),
            comfort_score=data.get('comfort_score'),
            energy_score=data.get('energy_score'),
            has_allergy=data.get('has_allergy', False),
            symptoms=data.get('symptoms')
        )
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'msg': '反馈提交成功',
            'data': feedback.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 400,
            'msg': str(e)
        }), 400


@app.route('/api/users/<int:user_id>/feedbacks', methods=['GET'])
def list_user_feedbacks(user_id):
    """获取用户的所有反馈"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    feedbacks = Feedback.query.filter_by(user_id=user_id).order_by(Feedback.created_at.desc()).all()
    
    return jsonify({
        'code': 200,
        'data': [f.to_dict() for f in feedbacks]
    })


# ============== 推荐接口（核心功能）==============

@app.route('/api/users/<int:user_id>/recommendations', methods=['GET'])
def get_recommendations(user_id):
    """
    获取针对用户的个性化菜谱推荐
    核心流程：
    1. 分析用户的饮食历史
    2. 找出缺少的营养素
    3. 推荐能补充这些营养的菜谱
    4. 考虑用户的反馈（避免过敏等）
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    # 获取推荐
    recommendations = recommender.recommend_recipes(user_id, n=5)
    
    result = []
    for rec in recommendations:
        recipe = rec['recipe']
        nutrition = recipe.get_nutrition()
        
        result.append({
            'recipe_id': recipe.id,
            'recipe_name': recipe.name,
            'description': recipe.description,
            'cuisine': recipe.cuisine,
            'difficulty': recipe.difficulty,
            'cook_time': recipe.cook_time,
            'nutrition': nutrition,
            'reason': rec['reason'],
            'score': round(rec['score'], 2)
        })
    
    return jsonify({
        'code': 200,
        'msg': '获取推荐成功',
        'data': result
    })


# ============== 统计接口 ==============

@app.route('/api/users/<int:user_id>/nutrition-summary', methods=['GET'])
def get_nutrition_summary(user_id):
    """
    获取用户的营养摄入总结
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    
    nutrition_analysis = recommender.get_recent_user_nutrition(user_id, days=7)
    
    if not nutrition_analysis:
        return jsonify({
            'code': 200,
            'msg': '暂无饮食记录',
            'data': None
        })
    
    return jsonify({
        'code': 200,
        'data': {
            'avg_nutrition': nutrition_analysis['avg_nutrition'],
            'deficiencies': nutrition_analysis['deficiencies'],
            'recommended': nutrition_analysis['recommended']
        }
    })


# ============== 错误处理 ==============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'code': 404, 'msg': '页面不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'code': 500, 'msg': '服务器内部错误'}), 500


# ============== 主程序 ==============

if __name__ == '__main__':
    print("🚀 车吃了啥 - 饮食健康App")
    print("📱 API服务启动在 http://localhost:5000")
    print("📚 API文档详见 README.md")
    app.run(debug=True, host='0.0.0.0', port=5000)
