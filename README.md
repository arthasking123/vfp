
# Video Formalization Processor

## 概述
`Video Formalization Processor` 是一个多功能的Python应用程序，专为处理讲演视频和与之对应的PDF格式演讲文档而设计。它可以将视频和文档内容结合，生成图文混编形式的文本化文章，适用于会议记录、教学内容整理等场景。

## 功能
- **视频处理**：加载讲演者视频文件。
- **文档处理**：加载与视频内容相关的PDF格式演讲文档。
- **字幕生成**：自动生成SRT格式的字幕，并允许用户在编辑框中进行校正。
- **图文混编**：支持在字幕编辑框中插入PDF文档中的页面。
- **文档保存**：可以将编辑的内容保存为HTML文档，方便后续加载和编辑。
- **书面化处理**：将编辑好的内容转换成标准化的WORD文档。

## 安装

克隆此仓库并安装所需依赖。

```bash
git clone https://github.com/arthasking123/vfp.git
cd vfp
pip install -r requirements.txt
```

## 使用方法

1. **加载视频**：选择并加载讲演者的视频文件。
2. **加载PDF文档**：加载与视频对应的PDF格式演讲文档。
3. **生成字幕**：点击“生成字幕”按钮，程序将自动生成字幕并显示在右侧编辑框中。用户可以在此编辑框中编辑和校正字幕。
4. **编辑字幕**：在视频播放时，对应字幕所在行的底色会变黄，方便用户定位和校正字幕。
5. **插入PDF内容**：双击界面左侧显示的PDF页面，即可将其插入到右侧编辑框中。
6. **保存HTML文档**：通过点击“保存HTML文档”按钮，可以将编辑框中的内容进行临时保存。
7. **加载HTML文档**：需要时可以通过点击“加载HTML文档”按钮来加载先前保存的内容。
8. **书面化处理**：点击“书面化”按钮，输入OPENAI KEY后，程序将转换内容生成最终的WORD文章。

## 贡献
欢迎对 `Video Formalization Processor` 提出宝贵意见或贡献代码。请按照以下步骤进行贡献：

1. Fork 仓库。
2. 创建新分支 (`git checkout -b feature-branch`)。
3. 提交您的更改 (`git commit -am 'Add some feature'`)。
4. 将更改推送到分支 (`git push origin feature-branch`)。
5. 创建一个新的Pull Request。

