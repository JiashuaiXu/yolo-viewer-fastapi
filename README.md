
# 🧠 YOLO Viewer — FastAPI + React

> 一个轻量级、开箱即用的 **YOLO 标注可视化工具**，用于快速查看和验证 YOLOv5/v8 等格式的检测标注结果。

![Demo Placeholder](https://via.placeholder.com/640x480/1e1e1e/FFFFFF?text=YOLO+Viewer+Demo)

## 🎯 项目目标

- 快速加载本地 YOLO 数据集（`images/`, `labels/`, `classes.txt`）
- 在浏览器中可视化边界框（Bounding Boxes）和类别标签
- 支持多类别、不同颜色高亮显示
- 无需数据库，零配置启动，适合标注质检、模型调试

---

## ✅ 核心功能

- 📂 自动扫描 `dataset/images/` 中的图片（支持 `.jpg`, `.png`）
- 🏷️ 从 `dataset/labels/{id}.txt` 加载 YOLO 格式标注  
  （格式：`class_id center_x center_y width height [confidence]`）
- 🎨 从 `dataset/classes.txt` 读取类别名称，并为每个类别分配唯一颜色
- 🔍 前端下拉选择图片 ID，实时渲染标注结果
- 🌐 RESTful API 由 FastAPI 提供，前端通过 `/api` 访问数据
- 🚀 开发模式支持热重载（Vite + FastAPI）

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.9+、FastAPI、Uvicorn |
| **前端** | React 18、TypeScript、Vite、Canvas API |
| **通信** | REST API (`/api/classes`, `/api/images`, `/api/image/{id}`, `/api/label/{id}`) |
| **部署** | 本地开发 / Docker（可选） |

---

## 📦 项目结构

```bash
yolo-viewer-fastapi/
├── backend/               # FastAPI 服务
│   ├── main.py            # API 路由与逻辑
│   └── requirements.txt   # Python 依赖
├── frontend/              # React + TypeScript 前端
│   ├── src/
│   │   └── App.tsx        # 主组件：图片选择 + Canvas 渲染
│   ├── vite.config.ts     # 代理 /api → http://localhost:3001
│   └── ...
├── dataset/               # YOLO 数据集（用户自定义）
│   ├── images/            # 图片文件（001.jpg, 002.png, ...）
│   ├── labels/            # 对应标注文件（001.txt, 002.txt, ...）
│   └── classes.txt        # 类别名称列表（每行一个）
├── start.sh               # 一键启动脚本（Linux/macOS）
├── .gitignore
└── README.md
```

---

## 🚀 快速开始

### 前置依赖

- [Python 3.9+](https://www.python.org/)
- [Node.js 18+](https://nodejs.org/)
- （可选）`venv`（Python 虚拟环境）

### 启动步骤

```bash
# 1. 克隆项目
git clone https://github.com/yourname/yolo-viewer-fastapi.git
cd yolo-viewer-fastapi

# 2. 准备示例数据（可选）
mkdir -p dataset/images dataset/labels
echo -e "person\ncar\nbicycle" > dataset/classes.txt
# 可使用脚本生成测试图（见下方）

# 3. 一键启动（Linux/macOS）
chmod +x start.sh
./start.sh
```

> 💡 **Windows 用户**：请分别手动启动后端和前端（见下方说明）。

### 手动启动（通用）

```bash
# 启动后端（终端 1）
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 3001

# 启动前端（终端 2）
cd frontend
npm install
npm run dev
```

✅ 访问：[http://localhost:3000](http://localhost:3000)

---

## 📝 示例数据格式

### `dataset/classes.txt`
```txt
person
car
bicycle
```

### `dataset/labels/001.txt`
```txt
0 0.45 0.60 0.30 0.40
1 0.80 0.50 0.20 0.30
2 0.20 0.70 0.10 0.15
```

> 格式：`<class_id> <cx> <cy> <width> <height> [confidence]`  
> 坐标归一化（0~1），相对于图像宽高

---

## 🧪 生成测试图片（可选）

运行以下脚本生成 `dataset/images/001.jpg`：

```python
# generate_test_image.py
from PIL import Image, ImageDraw

img = Image.new('RGB', (640, 480), color=(30, 30, 30))
draw = ImageDraw.Draw(img)
draw.text((50, 200), "YOLO Viewer Test Image", fill=(255, 255, 255))
img.save('dataset/images/001.jpg')
print("✅ 生成测试图片: dataset/images/001.jpg")
```

安装依赖并运行：
```bash
pip install pillow
python generate_test_image.py
```

---

## 📬 API 接口文档

FastAPI 自动生成交互式文档：

👉 [http://localhost:3001/docs](http://localhost:3001/docs)

可用接口：
- `GET /api/classes` → `["person", "car", ...]`
- `GET /api/images` → `["001", "002", ...]`
- `GET /api/image/{id}` → 图片文件
- `GET /api/label/{id}` → 标注列表

---

## 🤝 贡献与扩展

欢迎提交 Issue 或 PR！可扩展方向：

- [ ] 支持置信度过滤滑块
- [ ] 对比 Ground Truth 与 Prediction（双 label 文件）
- [ ] 导出为 Pascal VOC / COCO JSON
- [ ] 添加搜索/分页功能
- [ ] Docker 部署支持

---

## 📄 许可证

MIT License — 自由使用、修改、分发。

---

> Made with ❤️ for computer vision engineers and data annotators.  
> Inspired by YOLO, FastAPI, and the joy of clean visualization.

--- 
