# 🥗 车吃了啥 - 饮食健康App

一个基于用户反馈的智能饮食建议应用

## 📱 功能介绍

### 1️⃣ 记录你吃的东西
- 拍照识别食物
- 手动输入菜谱
- 保存到饮食日记

### 2️⃣ 反馈你的体验
- 这道菜好吃吗？
- 吃完舒服吗？
- 有没有过敏不适？

### 3️⃣ 获得健康建议
- AI分析你的饮食
- 推荐适合你的菜谱
- 改善营养搭配

---

## 🚀 快速开始

### 前提条件
- Python 3.8+
- Node.js 14+ (如果用Web版)

### 安装和运行

```bash
# 克隆项目
git clone https://github.com/1229charry/what-you-eat.git
cd what-you-eat

# 安装依赖
pip install -r requirements.txt

# 运行后端
python app.py

# 或运行Web前端
cd frontend
npm install
npm start
```

然后访问：http://localhost:5000

---

## 📁 项目结构

```
what-you-eat/
├── backend/
│   ├── app.py                 # 主应用程序
│   ├── models.py              # 数据模型
│   ├── recommender.py         # 推荐引擎
│   ├── database.db            # 数据库
│   └── requirements.txt        # 依赖
├── frontend/
│   ├── index.html             # 网页界面
│   ├── style.css              # 样式
│   └── script.js              # 交互逻辑
└── README.md
```

---

## 💡 使用示例

### 记录饮食
```
1. 点击 "记录我的饮食"
2. 输入或拍照识别食物
3. 确认营养信息
4. 保存
```

### 反馈体验
```
1. 选择之前记录的饭菜
2. 评分：味道、舒适度、能量
3. 报告任何不适症状
4. 提交反馈
```

### 获取建议
```
1. 点击 "获得建议"
2. App分析你最近的饮食
3. 推荐改善方案
```

---

## 🔧 技术栈

- **后端**: Flask (Python)
- **数据库**: SQLite
- **推荐算法**: scikit-learn, pandas
- **前端**: HTML5 + CSS3 + JavaScript

---

## 📊 核心数据

### 支持的食物分类
- 谷物类
- 蛋白质类
- 蔬菜类
- 水果类
- 乳制品
- 油脂类

### 营养指标
- 热量 (kcal)
- 蛋白质 (g)
- 脂肪 (g)
- 碳水化合物 (g)
- 纤维素 (g)

---

## 📝 开发路线图

- [x] 基础数据模型
- [x] 后端API
- [x] 前端界面
- [ ] 食物识别(AI)
- [ ] 推荐算法优化
- [ ] 移动App版本
- [ ] 用户社区

---

## 📄 许可

MIT License

---

## 🤝 贡献

欢迎提交Issue和Pull Request！
