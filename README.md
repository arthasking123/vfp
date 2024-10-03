
# Video Formalization Processor

[中文版](README.md) | [English Version](README_EN.md)

## 概述
`Video Formalization Processor` 是一个多功能的Python应用程序，专为处理讲演视频和与之对应的PDF格式演讲文档而设计。它可以将视频和文档内容结合，生成图文混编形式的文本化文章，适用于会议记录、教学内容整理等场景。
流程：从视频中提取字幕->用户在字幕中添加对应PPT页得到字幕和图的混编文档->对混编文档中的字幕部分进行书面化处理形成最终文档

## 功能
- **视频处理**：加载讲演者视频文件。
- **文档处理**：加载与视频内容相关的PDF格式演讲文档。
- **字幕生成**：自动生成SRT格式的字幕，并允许用户在编辑框中进行校正。
- **图文混编**：支持在字幕编辑框中插入PDF文档中的页面。
- **查找和替换**：支持使用Ctrl+F进行查找，Ctrl+H进行替换，方便用户快速定位和修改文本内容。
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
8. **书面化处理**：选择API提供商API，如OpenAI和APIKEY，点击“书面化”按钮，即可将编辑好的内容转换成WORD文档。
9. **查找和替换**：支持使用Ctrl+F进行查找，Ctrl+H进行替换，方便用户快速定位和修改文本内容。

## 贡献
欢迎对 `Video Formalization Processor` 提出宝贵意见或贡献代码。请按照以下步骤进行贡献：

1. Fork 仓库。
2. 创建新分支 (`git checkout -b feature-branch`)。
3. 提交您的更改 (`git commit -am 'Add some feature'`)。
4. 将更改推送到分支 (`git push origin feature-branch`)。
5. 创建一个新的Pull Request。

## 近期TODO LIST

1. 语音识别加入识别评分，对评分有混淆的词语在编辑界面逐个提示用户校正，评分高的略过校正步骤，提升文本校正效率
2. 加入自定义词库，实现专有词汇的识别
3. 支持多种API对接，如GROQ
4. 生成文本后融合PDF内容对文本进行校正
5. 自定义转写生成模板
6. 根据视频截图将PDF文稿自动插入文本
7. 界面优化、代码结构调整
