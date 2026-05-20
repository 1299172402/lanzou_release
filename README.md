# 🚀 Lanzou Cloud Upload Action

将文件上传到蓝奏云网盘（蓝奏云/woozooo）的 GitHub Action。

可用于为 中国大陆用户 提供 Release 发布、构建产物上传等场景，支持单文件和多文件上传。

通过 Docker 容器运行，基于 Python 3.12 + requests，自动解析 glob 模式匹配多个文件并逐一上传。

## 使用方法

### 基本用法

```yaml
- name: 上传到蓝奏云
  uses: 1299172402/lanzou_release@main
  with:
    ylogin: ${{ secrets.LANZOU_YLOGIN }}
    phpdisk_info: ${{ secrets.LANZOU_PHPDISK_INFO }}
    folder_id: ${{ secrets.LANZOU_FOLDER_ID }}
    file_path: 'dist/*.zip'
```

### 完整示例

```yaml
name: 构建并上传到蓝奏云

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build-and-upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: 构建项目
        run: |
          # 你的构建步骤...
          mkdir -p dist
          touch dist/example.txt
          zip -r dist/release.zip .
          zip -r dist/example.zip dist/example.txt

      - name: 上传到蓝奏云
        id: lanzou
        uses: 1299172402/lanzou_release@main
        with:
          ylogin: ${{ secrets.LANZOU_YLOGIN }}
          phpdisk_info: ${{ secrets.LANZOU_PHPDISK_INFO }}
          folder_id: ${{ secrets.LANZOU_FOLDER_ID }}
          file_path: 'dist/*.zip'

      - name: 输出上传状态
        run: |
          echo "上传状态: ${{ steps.lanzou.outputs.uploaded_status }}"

```

### 多文件上传

```yaml
- name: 上传多个文件
  uses: 1299172402/lanzou_release@main
  with:
    ylogin: ${{ secrets.LANZOU_YLOGIN }}
    phpdisk_info: ${{ secrets.LANZOU_PHPDISK_INFO }}
    folder_id: ${{ secrets.LANZOU_FOLDER_ID }}
    file_path: 'release/*.zip'
```

### 自定义文件名

```yaml
- name: 上传并重命名
  uses: 1299172402/lanzou_release@main
  with:
    ylogin: ${{ secrets.LANZOU_YLOGIN }}
    phpdisk_info: ${{ secrets.LANZOU_PHPDISK_INFO }}
    folder_id: ${{ secrets.LANZOU_FOLDER_ID }}
    file_path: 'dist/app.exe'
    file_name: 'MyApp-v1.0.exe'
```

## Inputs

| 参数 | 必填 | 说明 |
|------|------|------|
| `ylogin` | ✅ | 蓝奏云登录 Cookie 中的 `ylogin` 值 |
| `phpdisk_info` | ✅ | 蓝奏云登录 Cookie 中的 `phpdisk_info` 值 |
| `folder_id` | ✅ | 目标文件夹 ID |
| `file_path` | ✅ | 文件路径，支持 glob 模式（如 `dist/*.zip`） |
| `file_name` | ❌ | 自定义上传后的文件名（可选，默认使用原文件名，仅单文件时有效） |

## Outputs

| 输出 | 说明 |
|------|------|
| `uploaded_status` | 上传状态：`success` 表示全部成功，`partial` 表示部分成功 |

## 注意事项

- 📦 **文件大小限制**：蓝奏云普通用户单文件上限约 100MB，超过此限制可能被拒绝上传
- 📁 **多文件匹配**：`file_path` 支持 glob 模式（如 `*.zip`、`dist/**/*`），会按文件名排序后逐一上传
- 🔤 **自定义文件名**：`file_name` 仅在上传单个文件时生效，多文件上传时将使用原文件名

## 获取 Cookie

1. 浏览器登录 [蓝奏云](https://pc.woozooo.com)
2. 打开开发者工具（F12）→ Application → Cookies
3. 复制 `ylogin` 和 `phpdisk_info` 的值
4. 建议存入 GitHub Secrets

## 安全提示

⚠️ **强烈建议**将 Cookie 值存入 GitHub Secrets，不要明文写在 workflow 文件中：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 添加 `LANZOU_YLOGIN` 和 `LANZOU_PHPDISK_INFO`
3. 在 workflow 中用 `${{ secrets.LANZOU_YLOGIN }}` 引用

## 技术栈

- **运行时**：Python 3.12（Alpine Docker 镜像）
- **依赖**：[requests](https://pypi.org/project/requests/)
- **上传接口**：蓝奏云 PC 端 HTML5 上传 API (`pc.woozooo.com`)
