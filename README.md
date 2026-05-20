# 🚀 Lanzou Cloud Upload Action

将文件上传到蓝奏云网盘的 GitHub Action。

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
    tags:
      - 'v*'

jobs:
  build-and-upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 构建项目
        run: |
          # 你的构建步骤...
          mkdir -p dist
          zip -r dist/release.zip .

      - name: 上传到蓝奏云
        id: lanzou
        uses: 1299172402/lanzou_release@main
        with:
          ylogin: ${{ secrets.LANZOU_YLOGIN }}
          phpdisk_info: ${{ secrets.LANZOU_PHPDISK_INFO }}
          folder_id: ${{ secrets.LANZOU_FOLDER_ID }}
          file_path: 'dist/*.zip'

      - name: 输出下载链接
        run: |
          echo "下载地址: ${{ steps.lanzou.outputs.download_url }}"
          echo "上传数量: ${{ steps.lanzou.outputs.uploaded_count }}"
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

## Inputs

| 参数 | 必填 | 说明 |
|------|------|------|
| `ylogin` | ✅ | 蓝奏云 Cookie 中的 `ylogin` 值 |
| `phpdisk_info` | ✅ | 蓝奏云 Cookie 中的 `phpdisk_info` 值 |
| `folder_id` | ✅ | 目标文件夹 ID |
| `file_path` | ✅ | 文件路径，支持 glob 模式（如 `dist/*.zip`） |
| `file_name` | ❌ | 自定义上传后的文件名（仅单文件时有效） |

## Outputs

| 输出 | 说明 |
|------|------|
| `download_url` | 第一个文件的下载链接 |
| `file_id` | 第一个文件的文件 ID |
| `uploaded_count` | 成功上传的文件数量 |

## 获取 Cookie

1. 浏览器登录 [蓝奏云](https://pc.woozooo.com)
2. 打开开发者工具 (F12) → Application → Cookies
3. 复制 `ylogin` 和 `phpdisk_info` 的值
4. 建议存入 GitHub Secrets

## 安全提示

⚠️ **强烈建议**将 Cookie 值存入 GitHub Secrets，不要明文写在 workflow 文件中：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 添加 `LANZOU_YLOGIN` 和 `LANZOU_PHPDISK_INFO`
3. 在 workflow 中用 `${{ secrets.LANZOU_YLOGIN }}` 引用
