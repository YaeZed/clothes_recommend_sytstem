"""Flask 扩展单例 —— 避免循环导入"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db   = SQLAlchemy()
jwt  = JWTManager()
cors = CORS()
