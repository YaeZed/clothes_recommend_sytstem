# 基于混合推荐算法的服装推荐系统

这是一个结合了协同过滤（CF）、矩阵分解（SVD）和深度学习模型（DeepFM）的服装推荐系统项目。支持用户注册登录、商品浏览、收藏、加购、支付下单以及管理员后台数据可视化。

## 1. 环境准备

在开始部署前，请确保您的电脑已安装以下软件：

- **Python 3.10+**
- **Node.js 18+** (建议使用最新的 LTS 版本)
- **MySQL 8.0+**
- **Git** (用于管理代码)

## 2. 数据库配置

1.  启动您的 MySQL 服务。
2.  创建一个新的数据库，例如 `clothes_recommend_system`：
    ```sql
    CREATE DATABASE clothes_recommend_system DEFAULT CHARACTER SET utf8mb4;
    ```
3.  在 `backend/.env` 文件中配置您的数据库连接信息（如果没有 `.env`，可以参考 `.env.example` 创建）：
    ```env
    DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/clothes_recommend_system
    JWT_SECRET_KEY=your_secret_key
    ```

## 3. 后端部署 (Flask)

1.  进入项目根目录。
2.  创建并激活虚拟环境：
    ```bash
    python -m venv venv
    # Windows 激活:
    .\venv\Scripts\activate
    # Linux/Mac 激活:
    source venv/bin/activate
    ```
3.  安装依赖：
    ```bash
    pip install -r backend/requirements.txt
    ```
4.  执行数据库迁移（初始化表结构）：
    ```bash
    python migrate_db.py
    ```
5.  注入演示数据（可选）：
    ```bash
    python create_demo_users.py
    ```
6.  启动后端服务：
    ```bash
    python run.py
    ```
    后端默认在 `http://127.0.0.1:5000` 运行。

## 4. 前端部署 (Vue 3)

1.  打开一个新的终端，进入 `frontend` 目录：
    ```bash
    cd frontend
    ```
2.  安装依赖包：
    ```bash
    npm install
    ```
3.  启动开发服务器：
    ```bash
    npm run dev
    ```
    前端默认在 `http://localhost:5173` 运行。

## 5. 项目结构声明

- `backend/`: 基于 Flask 的后端 API 源码。
- `frontend/`: 基于 Vue 3 + Vite 的前端 UI 源码。
- `notebooks/`: 包含算法的 Jupyter Notebooks (CF, SVD, DeepFM)。
- `data/`: 存放原始数据集和处理后的 CSV 文件。
- `md/`: 项目相关文档。

## 6. 算法部分说明

核心推荐算法位于 `notebooks/` 目录下：
1. `02_CF.ipynb`: 协同过滤实现。
2. `03_SVD.ipynb`: 矩阵分解实现。
3. `04_DeepFM_Hybrid.ipynb`: DeepFM 模型与混合融合方案。

算法训练后的结果会直接写入 MySQL 的 `recommendations` 表中，由后端接口读取并分发。

## 7. 管理员账号

- 账号：`admin`
- 密码：`admin123` (或者根据 `管理员.txt` 的记录)

---
毕业设计答辩辅助文档请参考：`md/答辩指南.md`
