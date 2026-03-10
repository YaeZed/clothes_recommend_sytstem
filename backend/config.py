import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── 基础 ──────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-must-be-at-least-32-bytes-in-prod")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # ── 数据库 ────────────────────────────────────────────
    DB_HOST     = os.getenv("DB_HOST",     "localhost")
    DB_PORT     = os.getenv("DB_PORT",     "3306")
    DB_USER     = os.getenv("DB_USER",     "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME     = os.getenv("DB_NAME",     "clothes_recommend")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 生产关闭，调试时可设为 True

    # ── JWT ───────────────────────────────────────────────
    JWT_SECRET_KEY          = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-must-be-at-least-32-bytes-in-prod")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # ── 推荐系统 ──────────────────────────────────────────
    # 行为权重（用于构建用户-商品评分矩阵）
    BEHAVIOR_WEIGHTS = {
        "view":     0.2,
        "collect":  0.4,
        "cart":     0.6,
        "purchase": 1.0,
    }
    # 混合推荐加权系数（alpha+beta+gamma=1）
    HYBRID_ALPHA = 0.35   # 协同过滤权重
    HYBRID_BETA  = 0.30   # 内容推荐权重
    HYBRID_GAMMA = 0.35   # 深度学习权重

    TOP_K = 20            # 默认推荐条数
