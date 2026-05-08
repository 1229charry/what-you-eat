# 🧠 智能健康建议引擎

## 引擎架构概览

```
┌─────────────────────────────────────────┐
│         用户输入和反馈数据               │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│         数据预处理和特征提取              │
│  ├─ 缺失值处理                         │
│  ├─ 异常值检测                         │
│  └─ 特征工程                           │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│         多模型推荐系统                   │
│  ├─ 协同过滤 (用户相似度)              │
│  ├─ 内容过滤 (食物营养相似度)          │
│  ├─ 知识图谱 (营养-健康关联)          │
│  └─ 个性化排序 (用户偏好权重)         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│         建议生成和排序                   │
│  ├─ 候选建议池                         │
│  ├─ 多因子排序                         │
│  └─ 多样性保证                         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│      个性化呈现和反馈收集                │
└─────────────────────────────────────────┘
```

## 1. 数据输入层

### 1.1 用户属性特征
```javascript
UserFeatures {
  // 人口统计特征
  age: Number,                    // 年龄段
  gender: String,                 // 性别
  bmi: Number,                    // 体质指数
  
  // 健康特征
  activityLevel: String,          // 活动水平: low/medium/high
  healthConditions: String[],     // 健康状况: diabetes, hypertension, etc.
  allergies: String[],            // 过敏食物
  
  // 目标特征
  goals: {
    primary: String,              // 减脂/增肌/养生等
    secondary: String[],
    timeline: Number              // 天数
  },
  
  // 偏好特征
  cuisinePreferences: String[],   // 菜系偏好
  dietaryRestrictions: String[],  // 饮食限制
  budget: String                  // 预算等级
}
```

### 1.2 历史饮食特征
```javascript
DietHistoryFeatures {
  // 最近N天的统计
  avgCalories: Number,
  avgProtein: Number,
  avgFat: Number,
  avgCarbs: Number,
  avgFiber: Number,
  
  // 食物多样性
  uniqueFoodsCount: Number,
  cuisineDiversity: Number,
  
  // 用餐模式
  mealsPerDay: Number,
  eatingTime: String[],           // 常见进食时间
  
  // 偏好
  frequentFoods: String[],        // 常吃的食物
  avoidedFoods: String[]          // 避免的食物
}
```

### 1.3 反馈特征
```javascript
FeedbackFeatures {
  // 最近反馈
  recentFeedback: {
    satisfactionScores: Number[],  // 最近10条反馈的满意度
    comfortScores: Number[],       // 消化舒适度
    energyLevels: Number[],        // 能量水平
    symptoms: String[]             // 报告的症状
  },
  
  // 反馈趋势
  satisfactionTrend: Number,       // 满意度趋势 (-1到1)
  symptomFrequency: {
    digestive: Number,             // 消化问题频率
    fatigue: Number,               // 疲劳频率
    skinIssues: Number             // 皮肤问题频率
  },
  
  // 食物-反应关联
  foodReactionMap: {
    [foodName]: {
      positiveReactions: Number,
      negativeReactions: Number
    }
  }
}
```

## 2. 推荐算法

### 2.1 协同过滤 (Collaborative Filtering)

**目标**：找到与当前用户最相似的其他用户，推荐他们喜欢的菜谱

```python
class CollaborativeFilteringEngine:
    def find_similar_users(self, user_id, n_similar=10):
        """
        基于用户特征和反馈历史找相似用户
        """
        # 1. 构建用户特征向量
        current_user_features = self.build_user_vector(user_id)
        
        # 2. 计算相似度
        similarities = {}
        for other_user_id in self.all_users:
            other_features = self.build_user_vector(other_user_id)
            # 使用余弦相似度
            sim = cosine_similarity(current_user_features, other_features)
            similarities[other_user_id] = sim
        
        # 3. 返回最相似的N个用户
        return sorted(
            similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n_similar]
    
    def recommend_from_similar_users(self, user_id):
        """
        从相似用户推荐菜谱
        """
        similar_users = self.find_similar_users(user_id, n_similar=5)
        
        # 收集相似用户喜欢的菜谱
        candidate_recipes = {}
        for similar_user, similarity_score in similar_users:
            liked_recipes = self.get_user_liked_recipes(similar_user)
            for recipe, rating in liked_recipes:
                if recipe not in candidate_recipes:
                    candidate_recipes[recipe] = 0
                # 权重 = 相似度 * 菜谱评分
                candidate_recipes[recipe] += similarity_score * rating
        
        # 排序并返回top菜谱
        return sorted(
            candidate_recipes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
```

### 2.2 内容过滤 (Content-Based Filtering)

**目标**：推荐与用户已经喜欢的菜谱在营养/属性上相似的新菜谱

```python
class ContentBasedEngine:
    def build_recipe_vector(self, recipe_id):
        """
        为菜谱构建营养和属性向量
        """
        recipe = self.get_recipe(recipe_id)
        
        vector = {
            # 营养特征
            'calories': normalize(recipe['calories']),
            'protein': normalize(recipe['protein']),
            'fat': normalize(recipe['fat']),
            'carbs': normalize(recipe['carbs']),
            'fiber': normalize(recipe['fiber']),
            
            # 属性特征 (one-hot编码)
            'cuisine': one_hot_encode(recipe['cuisine']),
            'difficulty': normalize(recipe['difficulty']),
            'cookTime': normalize(recipe['cook_time']),
            
            # 食材特征
            'ingredients': self.ingredients_to_vector(recipe['ingredients'])
        }
        
        return vector
    
    def find_similar_recipes(self, recipe_id, n=10):
        """
        找相似的菜谱
        """
        recipe_vector = self.build_recipe_vector(recipe_id)
        
        similarities = {}
        for other_recipe_id in self.all_recipes:
            other_vector = self.build_recipe_vector(other_recipe_id)
            # 计算向量相似度
            sim = cosine_similarity(recipe_vector, other_vector)
            similarities[other_recipe_id] = sim
        
        return sorted(
            similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
    
    def recommend_based_on_liked_recipes(self, user_id):
        """
        基于用户喜欢的菜谱推荐相似菜谱
        """
        liked_recipes = self.get_user_liked_recipes(user_id)
        
        all_similar_recipes = {}
        for recipe_id, rating in liked_recipes:
            similar = self.find_similar_recipes(recipe_id, n=5)
            for similar_recipe, similarity in similar:
                if similar_recipe not in all_similar_recipes:
                    all_similar_recipes[similar_recipe] = 0
                # 权重 = 用户对原菜谱的评分 * 相似度
                all_similar_recipes[similar_recipe] += rating * similarity
        
        return sorted(
            all_similar_recipes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
```

### 2.3 知识图谱和规则引擎

**目标**：基于营养学知识推荐对用户有益的菜谱

```python
class KnowledgeGraphEngine:
    def __init__(self):
        # 定义营养和健康的关联关系
        self.health_rules = {
            'low_energy': {
                'deficiency': ['carbs', 'iron', 'b_vitamins'],
                'recommended_foods': ['whole_grains', 'red_meat', 'nuts'],
                'score_boost': 0.8
            },
            'poor_digestion': {
                'excess': ['fat', 'fiber_too_much'],
                'recommended_foods': ['light_soup', 'steamed_vegetables'],
                'score_boost': 0.9
            },
            'weight_loss': {
                'high_priority': ['calories', 'sugar'],
                'recommended_foods': ['lean_protein', 'vegetables'],
                'avoid_foods': ['fried', 'sugary'],
                'score_boost': 1.0
            },
            'muscle_gain': {
                'deficiency': ['protein'],
                'recommended_foods': ['chicken', 'eggs', 'fish', 'legumes'],
                'score_boost': 1.0
            }
        }
    
    def diagnose_nutritional_needs(self, user_id):
        """
        诊断用户的营养需求
        """
        user_data = self.get_user_data(user_id)
        diagnosis = {}
        
        for condition, rules in self.health_rules.items():
            score = 0
            
            # 检查缺乏的营养素
            if 'deficiency' in rules:
                for nutrient in rules['deficiency']:
                    if user_data[nutrient] < recommended[nutrient]:
                        score += 1
            
            # 检查过量的营养素
            if 'excess' in rules:
                for nutrient in rules['excess']:
                    if user_data[nutrient] > recommended[nutrient]:
                        score += 1
            
            if score > 0:
                diagnosis[condition] = score
        
        return sorted(
            diagnosis.items(),
            key=lambda x: x[1],
            reverse=True
        )
    
    def recommend_based_on_rules(self, user_id):
        """
        根据诊断结果推荐菜谱
        """
        diagnoses = self.diagnose_nutritional_needs(user_id)
        
        recommendations = {}
        for condition, severity in diagnoses:
            rules = self.health_rules[condition]
            
            # 找包含推荐食物的菜谱
            for recipe_id in self.all_recipes:
                recipe = self.get_recipe(recipe_id)
                
                match_score = 0
                # 计算食物匹配度
                for ingredient in recipe['ingredients']:
                    if ingredient in rules['recommended_foods']:
                        match_score += 1
                
                # 避免避禁食物
                avoid_score = 0
                if 'avoid_foods' in rules:
                    for ingredient in recipe['ingredients']:
                        if ingredient in rules['avoid_foods']:
                            avoid_score -= 1
                
                final_score = (match_score + avoid_score) * rules['score_boost'] * severity
                
                if recipe_id not in recommendations:
                    recommendations[recipe_id] = 0
                recommendations[recipe_id] += final_score
        
        return sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
```

### 2.4 个性化排序

```python
class PersonalizedRanking:
    def rank_recommendations(self, user_id, candidate_recipes, weights=None):
        """
        使用多个信号对候选菜谱进行排序
        """
        if weights is None:
            weights = {
                'collaborative': 0.3,
                'content_based': 0.2,
                'knowledge_graph': 0.3,
                'popularity': 0.1,
                'diversity': 0.1
            }
        
        # 获取各种推荐分数
        collab_scores = self.get_collaborative_scores(user_id, candidate_recipes)
        content_scores = self.get_content_scores(user_id, candidate_recipes)
        kg_scores = self.get_knowledge_graph_scores(user_id, candidate_recipes)
        pop_scores = self.get_popularity_scores(candidate_recipes)
        div_scores = self.get_diversity_scores(candidate_recipes, top_n=5)
        
        # 合并分数
        final_scores = {}
        for recipe in candidate_recipes:
            final_scores[recipe] = (
                weights['collaborative'] * collab_scores.get(recipe, 0) +
                weights['content_based'] * content_scores.get(recipe, 0) +
                weights['knowledge_graph'] * kg_scores.get(recipe, 0) +
                weights['popularity'] * pop_scores.get(recipe, 0) +
                weights['diversity'] * div_scores.get(recipe, 0)
            )
        
        # 排序
        return sorted(
            final_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
    
    def ensure_diversity(self, recommendations, top_n=10):
        """
        保证推荐的多样性（不同菜系、营养、口味）
        """
        selected = []
        remaining = list(recommendations)
        
        # 第一个总是分数最高的
        selected.append(remaining.pop(0))
        
        # 贪心地选择与已选项目多样性最大的
        while len(selected) < top_n and remaining:
            max_diversity_idx = 0
            max_diversity_score = -1
            
            for i, candidate in enumerate(remaining):
                diversity_score = self.compute_diversity(
                    candidate,
                    selected
                )
                
                if diversity_score > max_diversity_score:
                    max_diversity_score = diversity_score
                    max_diversity_idx = i
            
            selected.append(remaining.pop(max_diversity_idx))
        
        return selected
```

## 3. 建议生成引擎

### 3.1 建议文本生成

```python
class RecommendationExplainer:
    def generate_explanation(self, user_id, recipe, why_score):
        """
        为推荐生成解释文本
        """
        user = self.get_user(user_id)
        recipe_data = self.get_recipe(recipe)
        
        explanations = []
        
        # 根据推荐理由生成不同的解释
        if why_score['nutritional_match'] > 0.8:
            explanations.append(
                f"这道菜包含你最近缺乏的{why_score['missing_nutrients']}，"
                f"非常适合你现在的营养需求。"
            )
        
        if why_score['user_preference_match'] > 0.8:
            explanations.append(
                f"这道菜与你最近喜欢的菜谱在风味和口感上很相似。"
            )
        
        if why_score['health_goal_match'] > 0.8:
            explanations.append(
                f"这道菜特别适合{user['primary_goal']}目标。"
            )
        
        if why_score['similarity_to_liked'] > 0.7:
            explanations.append(
                f"与你之前评价为{recipe_data['similar_to']}的菜谱很相似。"
            )
        
        return " ".join(explanations)
```

## 4. 反馈循环

### 4.1 建议反馈收集

```python
class FeedbackLoop:
    def collect_recommendation_feedback(self, user_id, recipe_id, feedback):
        """
        收集用户对推荐的反馈，用于改进算法
        """
        feedback_record = {
            'user_id': user_id,
            'recipe_id': recipe_id,
            'timestamp': datetime.now(),
            'clicked': feedback.get('clicked', False),
            'tried': feedback.get('tried', False),
            'rating': feedback.get('rating', None),
            'relevant': feedback.get('relevant', None)
        }
        
        # 保存反馈
        self.save_feedback(feedback_record)
        
        # 如果用户尝试了菜谱，触发反馈收集
        if feedback.get('tried'):
            self.trigger_experience_feedback(user_id, recipe_id)
```

### 4.2 模型重训练

```python
class ModelRetraining:
    def should_retrain(self):
        """
        判断是否需要重新训练模型
        """
        # 条件1：新增一定数量的反馈数据
        if self.new_feedback_count > 1000:
            return True
        
        # 条件2：定期重训练（每周）
        if (datetime.now() - self.last_retrain_time).days >= 7:
            return True
        
        # 条件3：推荐准确率下降
        if self.compute_ndcg() < self.acceptable_ndcg:
            return True
        
        return False
    
    def retrain_models(self):
        """
        使用最新数据重新训练所有推荐模型
        """
        # 获取最新的训练数据
        train_data = self.get_recent_feedback_data()
        
        # 重新训练各个模型
        self.retrain_collaborative_filtering(train_data)
        self.retrain_content_based_model(train_data)
        self.retrain_ranking_model(train_data)
        
        # 验证新模型性能
        val_data = self.get_validation_data()
        performance = self.evaluate(val_data)
        
        # 如果性能更好，部署新模型
        if performance['ndcg'] > self.current_performance['ndcg']:
            self.deploy_new_models()
```

## 5. 监控和评估

### 5.1 关键指标

```python
class RecommendationMetrics:
    def compute_ndcg(self, user_id, n=10):
        """
        Normalized Discounted Cumulative Gain
        衡量推荐排序质量
        """
        recommendations = self.get_recommendations(user_id, n=n)
        ground_truth = self.get_ground_truth(user_id)
        
        dcg = 0
        for i, recipe in enumerate(recommendations):
            if recipe in ground_truth:
                dcg += ground_truth[recipe] / log2(i + 2)
        
        # 计算理想DCG
        ideal_ranking = sorted(
            ground_truth.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
        idcg = sum(
            score / log2(i + 2)
            for i, (recipe, score) in enumerate(ideal_ranking)
        )
        
        return dcg / idcg if idcg > 0 else 0
    
    def compute_coverage(self):
        """
        推荐系统覆盖的菜谱比例
        """
        recommended_recipes = set()
        for user_id in self.all_users:
            recs = self.get_recommendations(user_id)
            recommended_recipes.update(recs)
        
        return len(recommended_recipes) / len(self.all_recipes)
    
    def compute_diversity(self, user_recommendations):
        """
        推荐列表的多样性
        """
        # 计算菜谱之间的平均相似度
        similarities = []
        for i, rec1 in enumerate(user_recommendations):
            for rec2 in user_recommendations[i+1:]:
                sim = self.recipe_similarity(rec1, rec2)
                similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities)
        diversity = 1 - avg_similarity
        
        return diversity
```

---

**版本历史**
- v1.0 - 2026-05-08 - 初始发布

