-- ============================================================
-- 服装推荐系统数据库初始化脚本
-- 执行: mysql -u root -p < init_db.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS clothes_recommend
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE clothes_recommend;

-- ── 用户表 ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT          NOT NULL AUTO_INCREMENT,
    username    VARCHAR(50)  NOT NULL,
    password    VARCHAR(255) NOT NULL,
    email       VARCHAR(100),
    avatar      VARCHAR(255) DEFAULT '',
    role        ENUM('user','admin') DEFAULT 'user',
    style_pref  JSON         DEFAULT (JSON_ARRAY()),
    size_info   JSON         DEFAULT (JSON_OBJECT()),
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email    (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── 商品表 ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id          INT            NOT NULL AUTO_INCREMENT,
    title       VARCHAR(200)   NOT NULL,
    category    VARCHAR(50),
    style       VARCHAR(50),
    price       DECIMAL(10,2)  DEFAULT 0.00,
    sales_count INT            DEFAULT 0,
    stock       INT            DEFAULT 0,
    is_on_sale  TINYINT(1)     DEFAULT 1,
    images      JSON           DEFAULT (JSON_ARRAY()),
    attributes  JSON           DEFAULT (JSON_OBJECT()),
    description TEXT,
    tags        JSON           DEFAULT (JSON_ARRAY()),
    created_at  DATETIME       DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_category    (category),
    INDEX idx_style       (style),
    INDEX idx_sales_count (sales_count),
    INDEX idx_is_on_sale  (is_on_sale)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── 用户行为日志表 ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_behaviors (
    id          BIGINT   NOT NULL AUTO_INCREMENT,
    user_id     INT      NOT NULL,
    product_id  INT      NOT NULL,
    action_type ENUM('view','collect','cart','purchase') NOT NULL,
    duration    INT      DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_user_id    (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_action_type(action_type),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── 推荐结果缓存表 ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recommendations (
    id         INT   NOT NULL AUTO_INCREMENT,
    user_id    INT   NOT NULL,
    product_id INT   NOT NULL,
    score      FLOAT NOT NULL,
    algo_type  ENUM('hot','cf','content','deepfm','hybrid') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_user_algo (user_id, algo_type),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── 初始管理员账号（密码: admin123，需在应用层做哈希处理后更新）────
INSERT IGNORE INTO users (username, email, role, password)
VALUES ('admin', 'admin@example.com', 'admin', 'PLACEHOLDER_HASH');

SELECT 'Database initialized successfully!' AS message;
