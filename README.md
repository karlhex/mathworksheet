# 数学练习生成器

## 功能
- 自动生成数学练习算式
- 可自定义练习数量和最大数值
- 支持选择运算符：加、减、乘、除
- 可选择是否允许负数结果
- 逐题练习模式
- 实时计时
- 练习结束后展示详细结果

## 特点
- 随机生成练习题
- 灵活的练习配置
- 即时答案检查
- 计算总用时和正确率
- 结果详细展示

## 本地开发环境

### 先决条件
- Python 3.13
- Docker (可选)
- PostgreSQL (可选)

### 本地运行

1. 克隆仓库
```bash
git clone https://github.com/yourusername/mathworksheet.git
cd mathworksheet
```

2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据库
- 创建 PostgreSQL 数据库
- 更新 `.env` 文件中的数据库连接信息

5. 运行应用
```bash
python app.py
```

## Docker 部署

### 构建并运行
```bash
docker-compose up --build
```

### 停止服务
```bash
docker-compose down
```

## 环境变量
- `SECRET_KEY`: Flask 应用密钥
- `SQLALCHEMY_DATABASE_URI`: 数据库连接字符串
- `FLASK_ENV`: 运行环境 (development/production)

## 数据库配置

### PostgreSQL 设置

1. 安装 PostgreSQL
```bash
# macOS (使用 Homebrew)
brew install postgresql

# 启动 PostgreSQL 服务
brew services start postgresql
```

2. 创建数据库和用户
```bash
# 进入 PostgreSQL
psql postgres

# 使用提供的数据库设置脚本
\i database_setup.sql
```

或手动执行：
```sql
-- 创建用户
CREATE USER mathuser WITH PASSWORD 'mathpassword';

-- 创建数据库
CREATE DATABASE mathworksheetdb;

-- 授权
GRANT ALL PRIVILEGES ON DATABASE mathworksheetdb TO mathuser;
```

3. 安装依赖
```bash
# 激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 运行步骤
1. 启动应用
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动应用
python app.py
```

2. 在浏览器中打开 `http://localhost:8090`

## 使用说明
1. 设置练习参数
   - 选择练习数量
   - 设置最大数值
   - 选择运算符（加、减、乘、除）
   - 可选是否允许负数结果

2. 开始练习
   - 逐题输入答案
   - 实时计时
   - 即时反馈对错

3. 完成练习
   - 查看总题数
   - 查看正确题数
   - 查看总用时
   - 查看详细结果列表

## 系统需求
- Python 3.7+
- Flask 2.3.2+
- PostgreSQL

## 注意事项

- 确保 PostgreSQL 服务正在运行
- 数据库连接信息在 `app.py` 中配置
- 首次运行会自动创建数据库表
- 默认使用 `localhost` 作为数据库地址
- 生产环境请更改默认密码
- 建议使用安全的 SECRET_KEY

## 许可
MIT 开源许可
