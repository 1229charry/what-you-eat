// API 基础URL
const API_URL = 'http://localhost:5000/api';

// 当前用户ID (演示用)
let currentUserId = 1;

// 页面切换
function showPage(pageName) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示选中的页面
    const page = document.getElementById(pageName);
    if (page) {
        page.classList.add('active');
        
        // 页面加载时的初始化
        if (pageName === 'record') {
            loadRecipes();
            loadDietRecords();
        } else if (pageName === 'feedback') {
            loadDietRecordsForFeedback();
            loadFeedbacks();
        } else if (pageName === 'recommendations') {
            loadNutritionSummary();
            loadRecommendations();
        } else if (pageName === 'profile') {
            loadProfile();
        }
    }
}

// ========== 菜谱相关 ==========

async function loadRecipes() {
    try {
        const response = await fetch(`${API_URL}/recipes`);
        const result = await response.json();
        
        if (result.code === 200) {
            const select = document.getElementById('recipeSelect');
            select.innerHTML = '<option value="">-- 选择菜谱 --</option>';
            
            result.data.forEach(recipe => {
                const option = document.createElement('option');
                option.value = recipe.id;
                option.textContent = recipe.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载菜谱失败:', error);
        alert('加载菜谱失败');
    }
}

// ========== 饮食记录相关 ==========

async function submitDietRecord(event) {
    event.preventDefault();
    
    const recipeId = document.getElementById('recipeSelect').value;
    const mealType = document.getElementById('mealType').value;
    const quantity = document.getElementById('quantity').value;
    const notes = document.getElementById('notes').value;
    
    if (!recipeId || !mealType) {
        alert('请填写必要信息');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/users/${currentUserId}/diet-records`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipe_id: parseInt(recipeId),
                meal_type: mealType,
                quantity: parseFloat(quantity),
                notes: notes
            })
        });
        
        const result = await response.json();
        
        if (result.code === 200) {
            alert('✅ 饮食记录保存成功！');
            document.getElementById('dietForm').reset();
            loadDietRecords();
        } else {
            alert('❌ 保存失败: ' + result.msg);
        }
    } catch (error) {
        console.error('提交失败:', error);
        alert('提交失败');
    }
}

async function loadDietRecords() {
    try {
        const response = await fetch(`${API_URL}/users/${currentUserId}/diet-records`);
        const result = await response.json();
        
        if (result.code === 200) {
            const container = document.getElementById('dietRecordsList');
            
            if (result.data.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">还没有记录</p>';
                return;
            }
            
            container.innerHTML = result.data.map(record => `
                <div class="record-item">
                    <h4>🍽️ ${record.recipe_name}</h4>
                    <p><strong>时间:</strong> ${new Date(record.eaten_at).toLocaleString('zh-CN')}</p>
                    <p><strong>类型:</strong> ${record.meal_type}</p>
                    <p><strong>份数:</strong> ${record.quantity}份</p>
                    <p><strong>热量:</strong> ${record.nutrition.calories} kcal</p>
                    <p><strong>蛋白质:</strong> ${record.nutrition.protein}g | 
                       <strong>脂肪:</strong> ${record.nutrition.fat}g | 
                       <strong>碳水:</strong> ${record.nutrition.carbs}g</p>
                    ${record.notes ? `<p><strong>备注:</strong> ${record.notes}</p>` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载饮食记录失败:', error);
    }
}

async function loadDietRecordsForFeedback() {
    try {
        const response = await fetch(`${API_URL}/users/${currentUserId}/diet-records`);
        const result = await response.json();
        
        if (result.code === 200) {
            const select = document.getElementById('recordSelect');
            select.innerHTML = '<option value="">-- 选择饮食记录 --</option>';
            
            result.data.forEach(record => {
                const option = document.createElement('option');
                option.value = record.id;
                option.textContent = `${record.recipe_name} (${record.meal_type})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载饮食记录失败:', error);
    }
}

// ========== 反馈相关 ==========

async function submitFeedback(event) {
    event.preventDefault();
    
    const recordId = document.getElementById('recordSelect').value;
    const tasteScore = document.querySelector('input[name="taste"]:checked')?.value;
    const comfortScore = document.querySelector('input[name="comfort"]:checked')?.value;
    const energyScore = document.querySelector('input[name="energy"]:checked')?.value;
    const hasAllergy = document.getElementById('hasAllergy').checked;
    const symptoms = document.getElementById('symptoms').value;
    
    if (!recordId) {
        alert('请选择饮食记录');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/feedbacks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUserId,
                diet_record_id: parseInt(recordId),
                taste_score: tasteScore ? parseInt(tasteScore) : null,
                comfort_score: comfortScore ? parseInt(comfortScore) : null,
                energy_score: energyScore ? parseInt(energyScore) : null,
                has_allergy: hasAllergy,
                symptoms: symptoms
            })
        });
        
        const result = await response.json();
        
        if (result.code === 200) {
            alert('✅ 反馈提交成功！感谢你的反馈，这会帮助我们改进推荐！');
            document.getElementById('feedbackForm').reset();
            loadFeedbacks();
        } else {
            alert('❌ 提交失败: ' + result.msg);
        }
    } catch (error) {
        console.error('提交失败:', error);
        alert('提交失败');
    }
}

async function loadFeedbacks() {
    try {
        const response = await fetch(`${API_URL}/users/${currentUserId}/feedbacks`);
        const result = await response.json();
        
        if (result.code === 200) {
            const container = document.getElementById('feedbackList');
            
            if (result.data.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">还没有反馈</p>';
                return;
            }
            
            container.innerHTML = result.data.map(feedback => `
                <div class="record-item">
                    <h4>💬 ${feedback.recipe_name}</h4>
                    <p><strong>时间:</strong> ${new Date(feedback.created_at).toLocaleString('zh-CN')}</p>
                    ${feedback.taste_score ? `<p>👅 <strong>味道:</strong> ${feedback.taste_score}/5</p>` : ''}
                    ${feedback.comfort_score ? `<p>🤗 <strong>舒适度:</strong> ${feedback.comfort_score}/5</p>` : ''}
                    ${feedback.energy_score ? `<p>⚡ <strong>能量:</strong> ${feedback.energy_score}/5</p>` : ''}
                    ${feedback.has_allergy ? `<p>⚠️ <strong>过敏/不适:</strong> ${feedback.symptoms}</p>` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载反馈失败:', error);
    }
}

// 显示/隐藏症状输入框
document.addEventListener('change', function(e) {
    if (e.target.id === 'hasAllergy') {
        const symptomsGroup = document.getElementById('symptomsGroup');
        symptomsGroup.style.display = e.target.checked ? 'block' : 'none';
    }
});

// ========== 推荐相关 ==========

async function loadNutritionSummary() {
    try {
        const response = await fetch(`${API_URL}/users/${currentUserId}/nutrition-summary`);
        const result = await response.json();
        
        if (result.code === 200 && result.data) {
            const nutrition = result.data.avg_nutrition;
            const deficiencies = result.data.deficiencies;
            const recommended = result.data.recommended;
            
            const container = document.getElementById('nutritionSummary');
            
            let html = '';
            for (const [nutrient, value] of Object.entries(nutrition)) {
                const recommValue = recommended[nutrient];
                const unit = nutrient === 'calories' ? 'kcal' : 'g';
                const status = value < recommValue * 0.8 ? '⚠️ 不足' : '✅ 充足';
                
                html += `
                    <div class="nutrition-item">
                        <div class="label">${nutrient}</div>
                        <div class="value">${value.toFixed(1)}</div>
                        <div style="font-size: 12px; color: #999;">推荐: ${recommValue}${unit}</div>
                        <div style="font-size: 12px;">${status}</div>
                    </div>
                `;
            }
            
            if (deficiencies.length > 0) {
                html += `<div style="grid-column: 1/-1; background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    <strong>⚠️ 营养缺陷:</strong> ${deficiencies.join('、')} 不足，我们已为你推荐相关菜谱
                </div>`;
            }
            
            container.innerHTML = html;
        } else {
            document.getElementById('nutritionSummary').innerHTML = 
                '<p style="text-align: center; color: #999;">暂无数据，请先记录饮食</p>';
        }
    } catch (error) {
        console.error('加载营养摘要失败:', error);
    }
}

async function loadRecommendations() {
    try {
        const response = await fetch(`${API_URL}/users/${currentUserId}/recommendations`);
        const result = await response.json();
        
        if (result.code === 200) {
            const container = document.getElementById('recommendationsList');
            
            if (result.data.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">暂无推荐</p>';
                return;
            }
            
            container.innerHTML = result.data.map((rec, index) => `
                <div class="recipe-card">
                    <h4>🎯 ${index + 1}. ${rec.recipe_name}</h4>
                    <p><strong>理由:</strong> ${rec.reason}</p>
                    <p><strong>菜系:</strong> ${rec.cuisine} | <strong>难度:</strong> ${rec.difficulty} | <strong>时间:</strong> ${rec.cook_time}分钟</p>
                    <p>${rec.description}</p>
                    <div style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                        <strong>营养信息:</strong><br>
                        热量: ${rec.nutrition.calories} kcal | 
                        蛋白质: ${rec.nutrition.protein}g | 
                        脂肪: ${rec.nutrition.fat}g | 
                        碳水: ${rec.nutrition.carbs}g
                    </div>
                    <p style="margin-top: 10px; color: #667eea; font-weight: bold;">匹配度: ${(rec.score * 100).toFixed(0)}%</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载推荐失败:', error);
        alert('加载推荐失败');
    }
}

// ========== 个人资料相关 ==========

async function loadProfile() {
    try {
        const response = await fetch(`${API_URL}/users/${currentUserId}`);
        const result = await response.json();
        
        if (result.code === 200) {
            const user = result.data;
            document.getElementById('profileUsername').value = user.username;
            document.getElementById('profileAge').value = user.age || '';
            document.getElementById('profileGender').value = user.gender || '';
            document.getElementById('profileGoal').value = user.health_goal || '';
        }
    } catch (error) {
        console.error('加载个人资料失败:', error);
    }
}

async function updateProfile(event) {
    event.preventDefault();
    
    // 这里可以添加更新个人资料的逻辑
    alert('个人资料更新功能（演示版本未实现）');
}

// ========== 初始化 ==========

// 页面加载时显示首页
document.addEventListener('DOMContentLoaded', function() {
    showPage('home');
    
    // 创建演示用户（如果需要）
    createDemoData();
});

// 创建演示数据
async function createDemoData() {
    // 创建演示用户
    try {
        // 创建一些示例食物
        const foods = [
            { name: '米饭', category: '谷物', calories: 130, protein: 2.6, fat: 0.3, carbs: 28, fiber: 0.3 },
            { name: '鸡胸肉', category: '蛋白质', calories: 165, protein: 31, fat: 3.6, carbs: 0, fiber: 0 },
            { name: '西兰花', category: '蔬菜', calories: 34, protein: 2.8, fat: 0.4, carbs: 7, fiber: 2.4 },
            { name: '番茄', category: '蔬菜', calories: 18, protein: 0.9, fat: 0.2, carbs: 3.9, fiber: 1.2 },
            { name: '鸡蛋', category: '蛋白质', calories: 155, protein: 13, fat: 11, carbs: 1.1, fiber: 0 }
        ];
        
        // 检查是否已创建
        const foodsResponse = await fetch(`${API_URL}/foods`);
        const foodsResult = await foodsResponse.json();
        
        if (foodsResult.data.length === 0) {
            for (const food of foods) {
                await fetch(`${API_URL}/foods`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(food)
                });
            }
        }
    } catch (error) {
        console.error('创建演示数据失败:', error);
    }
}
