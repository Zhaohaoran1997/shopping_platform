# 线上商品交易平台 PRD

## 1. 项目概述

### 1.1 项目背景
本项目旨在开发一个功能完整的线上商品交易平台，为用户提供商品浏览、购买、订单管理等功能，同时支持消费券使用和退换货功能。管理员可以通过后台系统进行商品、订单和退换货的管理。

### 1.2 技术栈选择
- 前端：Vue.js 3 + Element Plus
- 后端：Django 4.x + Django REST framework
- 数据库：MySQL 8.0
- 缓存：Redis
- 认证：JWT (JSON Web Token)

### 1.3 系统架构
```
前端 (Vue.js + Element Plus) <-> API Gateway <-> 后端服务 (Django)
                                            |
                                            v
                                      数据库 (MySQL)
                                            |
                                            v
                                      缓存 (Redis)
```

## 2. 功能需求

### 2.1 用户端功能

#### 2.1.1 用户认证
- 用户注册
  - 邮箱/手机号注册
  - 密码强度验证
  - 验证码验证
- 用户登录
  - 账号密码登录
  - JWT token认证
- 找回密码
  - 邮箱验证码找回
  - 手机验证码找回

#### 2.1.2 商品浏览
- 商品列表页
  - 分页展示
  - 分类筛选
  - 价格排序
  - 销量排序
  - 搜索功能
- 商品详情页
  - 商品基本信息
  - 商品图片展示
  - 商品规格选择
  - 库存显示
  - 加入购物车

#### 2.1.3 购物车
- 购物车管理
  - 添加商品
  - 修改数量
  - 删除商品
  - 清空购物车
- 结算功能
  - 选择收货地址
  - 选择支付方式
  - 使用消费券
  - 计算总价

#### 2.1.4 订单管理
- 订单创建
  - 订单信息确认
  - 支付（Mock）
  - 订单状态更新
- 订单列表
  - 全部订单
  - 待付款
  - 待发货
  - 待收货
  - 已完成
  - 已取消
- 订单详情
  - 订单信息
  - 物流信息
  - 支付信息

#### 2.1.5 消费券
- 消费券列表
  - 可用券
  - 已使用
  - 已过期
- 消费券使用
  - 下单时选择
  - 金额抵扣
  - 使用规则验证

#### 2.1.6 退换货
- 退换货申请
  - 选择退货/换货
  - 填写原因
  - 上传图片
- 退换货记录
  - 申请列表
  - 处理进度
  - 退款状态

### 2.2 管理端功能

#### 2.2.1 商品管理
- 商品列表
  - 商品信息展示
  - 状态管理
  - 库存管理
- 商品操作
  - 添加商品
  - 编辑商品
  - 删除商品
  - 上下架

#### 2.2.2 订单管理
- 订单列表
  - 订单信息展示
  - 订单状态管理
  - 发货管理
- 订单操作
  - 查看详情
  - 发货处理
  - 取消订单

#### 2.2.3 退换货管理
- 退换货列表
  - 申请信息展示
  - 处理状态管理
- 退换货操作
  - 审核处理
  - 退款处理
  - 换货处理

#### 2.2.4 用户管理
- 用户列表
  - 用户信息展示
  - 账号状态管理
- 用户操作
  - 查看详情
  - 禁用/启用
  - 重置密码

#### 2.2.5 消费券管理
- 消费券列表
  - 券信息展示
  - 使用状态管理
- 消费券操作
  - 发放券
  - 批量发放
  - 作废券

## 3. 数据库设计

### 3.1 用户相关表
```sql
-- 用户表
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户地址表
CREATE TABLE user_addresses (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    receiver VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.2 商品相关表
```sql
-- 商品分类表
CREATE TABLE categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    parent_id BIGINT,
    level INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 商品表
CREATE TABLE products (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    sales INT DEFAULT 0,
    status TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 商品图片表
CREATE TABLE product_images (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    is_main BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.3 订单相关表
```sql
-- 订单表
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_no VARCHAR(50) NOT NULL UNIQUE,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    status TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_order_no (order_no),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单详情表
CREATE TABLE order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.4 消费券相关表
```sql
-- 消费券表
CREATE TABLE coupons (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type TINYINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    min_amount DECIMAL(10,2) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_time (start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户消费券表
CREATE TABLE user_coupons (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    coupon_id BIGINT NOT NULL,
    status TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    INDEX idx_user_id (user_id),
    INDEX idx_coupon_id (coupon_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 3.5 退换货相关表
```sql
-- 退换货申请表
CREATE TABLE return_requests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    type TINYINT NOT NULL,
    reason TEXT NOT NULL,
    status TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 退换货图片表
CREATE TABLE return_images (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    return_id BIGINT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (return_id) REFERENCES return_requests(id),
    INDEX idx_return_id (return_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 4. API接口设计

### 4.1 用户接口
```
POST /api/v1/users/register/ - 用户注册
POST /api/v1/users/login/ - 用户登录
GET /api/v1/users/profile/ - 获取用户信息
PUT /api/v1/users/profile/ - 更新用户信息
```

### 4.2 商品接口
```
GET /api/v1/products/ - 获取商品列表
GET /api/v1/products/{id}/ - 获取商品详情
GET /api/v1/categories/ - 获取商品分类
GET /api/v1/products/search/ - 搜索商品
```

### 4.3 购物车接口
```
GET /api/v1/cart/ - 获取购物车列表
POST /api/v1/cart/ - 添加商品到购物车
PUT /api/v1/cart/{id}/ - 更新购物车商品数量
DELETE /api/v1/cart/{id}/ - 删除购物车商品
```

### 4.4 订单接口
```
POST /api/v1/orders/ - 创建订单
GET /api/v1/orders/ - 获取订单列表
GET /api/v1/orders/{id}/ - 获取订单详情
PUT /api/v1/orders/{id}/cancel/ - 取消订单
PUT /api/v1/orders/{id}/confirm/ - 确认收货
```

### 4.5 消费券接口
```
GET /api/v1/coupons/ - 获取消费券列表
GET /api/v1/user-coupons/ - 获取用户消费券
POST /api/v1/coupons/receive/ - 领取消费券
```

### 4.6 退换货接口
```
POST /api/v1/returns/ - 申请退换货
GET /api/v1/returns/ - 获取退换货列表
GET /api/v1/returns/{id}/ - 获取退换货详情
```

## 5. 安全设计

### 5.1 用户认证
- 使用JWT进行身份认证
- Token有效期设置
- 密码加密存储

### 5.2 数据安全
- 敏感数据加密
- SQL注入防护
- XSS防护
- CSRF防护

### 5.3 接口安全
- 接口访问频率限制
- 参数验证
- 权限控制

## 6. 性能设计

### 6.1 缓存策略
- Redis缓存热点数据
- 页面静态化
- CDN加速

### 6.2 数据库优化
- 索引优化
- 分页查询
- 读写分离

## 7. 部署方案

### 7.1 开发环境
- Docker容器化
- 开发环境配置
- 测试环境配置

### 7.2 生产环境
- 服务器配置
- 负载均衡
- 监控告警

## 8. 项目进度规划

### 8.1 第一阶段（2周）
- 需求分析和设计
- 数据库设计
- 基础架构搭建

### 8.2 第二阶段（3周）
- 用户模块开发
- 商品模块开发
- 购物车模块开发

### 8.3 第三阶段（3周）
- 订单模块开发
- 支付模块开发
- 消费券模块开发

### 8.4 第四阶段（2周）
- 退换货模块开发
- 管理后台开发
- 系统测试

### 8.5 第五阶段（1周）
- 性能优化
- 部署上线
- 文档完善 