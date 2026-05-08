import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models import db, Recipe, RecipeRating, Feedback, Food
from datetime import datetime, timedelta

class FoodRecommender:
    """基于用户反馈的菜谱推荐引擎"""
    
    def __init__(self):
        self.recipes = []
        self.user_ratings = {}
    
    def get_recent_user_nutrition(self, user_id, days=7):
        """
        获取用户最近N天的营养摄入统计
        返回：平均营养值 + 缺少的营养素
        """
        from models import DietRecord
        
        start_date = datetime.utcnow() - timedelta(days=days)
        recent_records = DietRecord.query.filter(
            DietRecord.user_id == user_id,
            DietRecord.eaten_at >= start_date
        ).all()
        
        if not recent_records:
            return None
        
        # 统计营养
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'fiber': 0
        }
        
        for record in recent_records:
            if record.recipe:
                nutrition = record.recipe.get_nutrition()
                for key in total_nutrition:
                    total_nutrition[key] += nutrition[key]
        
        # 平均值
        days_count = len(set([r.eaten_at.date() for r in recent_records]))
        avg_nutrition = {
            k: v / days_count for k, v in total_nutrition.items()
        }
        
        # 推荐摄入量 (基于2000kcal)
        recommended = {
            'calories': 2000,
            'protein': 50,
            'fat': 70,
            'carbs': 250,
            'fiber': 25
        }
        
        # 找出缺少的营养
        deficiencies = []
        for nutrient, recommended_value in recommended.items():
            if avg_nutrition[nutrient] < recommended_value * 0.8:
                deficiencies.append(nutrient)
        
        return {
            'avg_nutrition': avg_nutrition,
            'deficiencies': deficiencies,
            'recommended': recommended
        }
    
    def get_user_feedback_summary(self, user_id, days=7):
        """
        获取用户最近的反馈总结
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        feedbacks = Feedback.query.filter(
            Feedback.user_id == user_id,
            Feedback.created_at >= start_date
        ).all()
        
        if not feedbacks:
            return None
        
        taste_scores = [f.taste_score for f in feedbacks if f.taste_score]
        comfort_scores = [f.comfort_score for f in feedbacks if f.comfort_score]
        energy_scores = [f.energy_score for f in feedbacks if f.energy_score]
        
        symptom_list = []
        for f in feedbacks:
            if f.symptoms:
                symptom_list.extend(f.symptoms.split(','))
        
        return {
            'avg_taste': np.mean(taste_scores) if taste_scores else None,
            'avg_comfort': np.mean(comfort_scores) if comfort_scores else None,
            'avg_energy': np.mean(energy_scores) if energy_scores else None,
            'common_symptoms': symptom_list,
            'allergy_count': sum(1 for f in feedbacks if f.has_allergy)
        }
    
    def recommend_recipes(self, user_id, n=5):
        """
        为用户推荐菜谱
        核心逻辑：
        1. 分析用户缺少的营养素
        2. 找富含这些营养素的菜谱
        3. 考虑用户的反馈历史（避免引起不适的食物）
        4. 返回排序后的推荐
        """
        # 获取用户营养需求
        nutrition_analysis = self.get_recent_user_nutrition(user_id)
        if not nutrition_analysis:
            # 如果没有饮食记录，返回热门菜谱
            return self._get_popular_recipes(n)
        
        # 获取用户反馈
        feedback_summary = self.get_user_feedback_summary(user_id)
        
        # 获取所有菜谱
        all_recipes = Recipe.query.all()
        if not all_recipes:
            return []
        
        recommendations = []
        
        for recipe in all_recipes:
            score = 0
            
            # 1. 营养匹配度 (占40%)
            recipe_nutrition = recipe.get_nutrition()
            nutrition_score = self._calculate_nutrition_match(
                recipe_nutrition,
                nutrition_analysis['avg_nutrition'],
                nutrition_analysis['deficiencies']
            )
            score += nutrition_score * 0.4
            
            # 2. 用户反馈历史 (占30%)
            if feedback_summary:
                feedback_score = self._calculate_feedback_score(
                    recipe,
                    feedback_summary,
                    user_id
                )
                score += feedback_score * 0.3
            
            # 3. 菜谱受欢迎程度 (占20%)
            popularity_score = self._calculate_popularity(
                recipe
            )
            score += popularity_score * 0.2
            
            # 4. 多样性加分 (占10%)
            diversity_score = 1.0  # 默认
            score += diversity_score * 0.1
            
            recommendations.append({
                'recipe': recipe,
                'score': score,
                'reason': self._generate_reason(
                    recipe,
                    nutrition_analysis['deficiencies'],
                    feedback_summary
                )
            })
        
        # 排序并返回top N
        recommendations = sorted(
            recommendations,
            key=lambda x: x['score'],
            reverse=True
        )[:n]
        
        return recommendations
    
    def _calculate_nutrition_match(self, recipe_nutrition, avg_nutrition, deficiencies):
        """
        计算菜谱与用户营养需求的匹配度
        """
        score = 0
        
        for nutrient in deficiencies:
            if recipe_nutrition[nutrient] > avg_nutrition[nutrient]:
                # 菜谱能补充这个营养素
                ratio = min(recipe_nutrition[nutrient] / avg_nutrition[nutrient], 3)
                score += ratio
        
        if score > 0:
            score = score / len(deficiencies)
        else:
            score = 0.5  # 即使没有缺陷也有基础分
        
        return min(score, 1.0)
    
    def _calculate_feedback_score(self, recipe, feedback_summary, user_id):
        """
        基于用户历史反馈计算评分
        """
        # 查找用户对这道菜的历史反馈
        from models import DietRecord
        
        user_feedbacks = []
        records = DietRecord.query.filter(
            DietRecord.user_id == user_id,
            DietRecord.recipe_id == recipe.id
        ).all()
        
        for record in records:
            for feedback in record.feedbacks:
                user_feedbacks.append(feedback)
        
        if not user_feedbacks:
            # 没有反馈记录，返回中立分数
            return 0.5
        
        # 计算平均评分
        taste_scores = [f.taste_score for f in user_feedbacks if f.taste_score]
        comfort_scores = [f.comfort_score for f in user_feedbacks if f.comfort_score]
        
        score = 0
        if taste_scores:
            score += np.mean(taste_scores) / 5 * 0.5
        if comfort_scores:
            score += np.mean(comfort_scores) / 5 * 0.5
        
        # 检查过敏
        if any(f.has_allergy for f in user_feedbacks):
            return 0  # 有过敏，不推荐
        
        return score
    
    def _calculate_popularity(self, recipe):
        """
        计算菜谱的受欢迎程度
        """
        if not recipe.ratings:
            return 0.5
        
        avg_rating = np.mean([r.rating for r in recipe.ratings])
        return avg_rating / 5
    
    def _generate_reason(self, recipe, deficiencies, feedback_summary):
        """
        生成推荐理由的文本说明
        """
        reasons = []
        
        recipe_nutrition = recipe.get_nutrition()
        
        for nutrient in deficiencies:
            if recipe_nutrition.get(nutrient, 0) > 100:
                nutrient_name = {
                    'protein': '蛋白质',
                    'fiber': '纤维素',
                    'carbs': '碳水化合物',
                    'fat': '脂肪',
                    'calories': '热量'
                }.get(nutrient, nutrient)
                reasons.append(f"富含{nutrient_name}")
        
        if not reasons:
            reasons.append("营养均衡")
        
        return '、'.join(reasons)
    
    def _get_popular_recipes(self, n=5):
        """
        返回最受欢迎的菜谱
        """
        recipes = Recipe.query.all()
        if not recipes:
            return []
        
        # 简单按评分排序
        rated_recipes = [(r, np.mean([x.rating for x in r.ratings]) if r.ratings else 0) 
                        for r in recipes]
        rated_recipes = sorted(rated_recipes, key=lambda x: x[1], reverse=True)
        
        return [
            {
                'recipe': recipe,
                'score': score,
                'reason': '热门菜谱'
            }
            for recipe, score in rated_recipes[:n]
        ]
