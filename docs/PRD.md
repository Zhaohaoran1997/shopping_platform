# 线上商品交易平台 MVP 版本 PRD

## 1. 核心功能模块

### 1.1 用户认证（优先级：P0）
- 用户注册
  - 基本信息：用户名、密码、邮箱
  - 手机号验证（可选）
- 用户登录
  - 账号密码登录
  - 登录状态维护
- 用户信息管理
  - 查看/修改个人信息
  - 修改密码

### 1.2 商品模块（优先级：P0）
- 商品展示
- 商品列表页
    - 基础筛选：分类、价格区间
    - 排序：价格、销量、上架时间
  - 分页展示
- 商品详情页
    - 基本信息展示
  - 商品图片展示
  - 商品规格选择
- 商品搜索
  - 关键词搜索
  - 搜索结果排序

### 1.3 购物车模块（优先级：P0）
- 购物车管理
  - 添加商品到购物车
  - 修改商品数量
  - 删除购物车商品
  - 清空购物车
- 购物车结算
  - 选择商品
  - 计算总价

### 1.4 订单模块（优先级：P0）
- 订单创建
  - 选择收货地址
  - 选择支付方式
  - 确认订单信息
- 订单支付（Mock）
  - 模拟支付流程
  - 支付状态更新
- 订单管理
  - 查看订单列表
  - 查看订单详情
  - 取消未支付订单

### 1.5 消费券模块（优先级：P0）
- 消费券管理
  - 发放消费券
  - 查看可用消费券
  - 使用消费券
- 消费券规则
  - 使用条件
  - 有效期管理

### 1.6 退换货模块（优先级：P0）
- 退货功能
  - 申请退货
  - 退货原因选择
  - 退货状态跟踪
- 换货功能
  - 申请换货
  - 换货状态跟踪

## 2. 扩展功能模块（后续迭代）

### 2.1 商品评价模块（优先级：P1）
- 评价功能
  - 发表评价
  - 评分
  - 上传图片

## 3. 管理后台（优先级：P0）

### 3.1 商品管理
- 商品列表
  - 查看所有商品
  - 添加新商品
  - 编辑商品信息
  - 上下架商品
- 商品分类管理
  - 添加分类
  - 编辑分类
  - 删除分类

### 3.2 订单管理
- 订单列表
  - 查看所有订单
  - 订单状态管理
  - 订单详情查看

### 3.3 用户管理
- 用户列表
  - 查看用户信息
  - 用户状态管理

## 4. 技术架构

### 4.1 前端技术栈
- React/Vue.js
- Ant Design/Element UI
- Redux/Vuex
- Axios

### 4.2 后端技术栈
- Django REST framework
- MySQL/PostgreSQL
- Redis（缓存）
- JWT（认证）

### 4.3 部署架构
- 前后端分离
- RESTful API
- 数据库主从架构
- 缓存层

## 5. 数据模型（核心）

### 5.1 用户相关
- User（用户）
  - id: 主键
  - username: 用户名
  - password: 密码
  - email: 邮箱
  - phone: 手机号
  - created_at: 创建时间
  - updated_at: 更新时间

- Address（收货地址）
  - id: 主键
  - user_id: 用户ID
  - receiver: 收货人
  - phone: 联系电话
  - province: 省份
  - city: 城市
  - district: 区县
  - address: 详细地址
  - is_default: 是否默认地址

### 5.2 商品相关
- Category（商品分类）
  - id: 主键
  - name: 分类名称
  - parent_id: 父分类ID
  - level: 分类层级
  - is_active: 是否激活

- Product（商品）
  - id: 主键
  - category_id: 分类ID
  - name: 商品名称
  - description: 商品描述
  - price: 价格
  - stock: 库存
  - sales: 销量
  - status: 状态
  - is_active: 是否激活

- ProductImage（商品图片）
  - id: 主键
  - product_id: 商品ID
  - image_url: 图片URL
  - is_main: 是否主图

- ProductSpecification（商品规格）
  - id: 主键
  - product_id: 商品ID
  - name: 规格名称
  - value: 规格值

### 5.3 订单相关
- Order（订单）
  - id: 主键
  - user_id: 用户ID
  - order_no: 订单编号
  - total_amount: 总金额
  - status: 订单状态
  - created_at: 创建时间
  - updated_at: 更新时间

- OrderItem（订单项）
  - id: 主键
  - order_id: 订单ID
  - product_id: 商品ID
  - quantity: 数量
  - price: 单价
  - total_price: 总价

- Payment（支付记录）
  - id: 主键
  - order_id: 订单ID
  - amount: 支付金额
  - payment_method: 支付方式
  - status: 支付状态
  - created_at: 创建时间

## 6. 安全考虑
- 用户密码加密存储
- API 接口认证
- 数据验证和清洗
- XSS/CSRF 防护

## 7. 性能考虑
- 数据库索引优化
- 缓存策略
- 图片CDN
- 分页加载 