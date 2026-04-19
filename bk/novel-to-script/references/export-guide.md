# 导出指南

## 支持的导出格式

| 格式 | 说明 | 适用场景 |
|------|------|---------|
| 对话框展示 | 直接在对话中显示 | 快速查看、即时反馈 |
| .md 文件 | Markdown 格式 | 方便编辑修改，后续加工 |
| .docx 文件 | Word 格式 | 专业排版，发给导演/制片使用 |

---

## 导出流程

用户输入 `/导出` 时：

**第一步：询问格式**
```
请选择导出格式：

1. 📄 导出 .md 文件（Markdown，方便编辑）
2. 📝 导出 .docx 文件（Word，专业排版）
3. 📦 全部导出（同时生成 .md 和 .docx）

请输入数字选择：
```

**第二步：询问范围**
```
请选择导出范围：

1. 导出全部已完成集数（共 X 集）
2. 导出指定集数（请输入，如：1-5 或 3）
```

---

## .md 文件导出规范

每集单独一个文件，命名格式：`第N集_标题.md`

文件头部加项目信息：
```markdown
# 《剧名》剧本

**改编自**：[原著名称]
**导出时间**：YYYY-MM-DD
**共 X 集**

---
```

然后按集数顺序附上完整剧本内容。

---

## .docx 文件导出规范

使用 docx npm 库生成专业格式的 Word 文档。

### 文档结构

1. **封面页**：剧名、原著、集数、日期
2. **目录页**：自动生成分集目录
3. **正文**：每集剧本，每集前有页眉显示集数和标题

### 格式要求

- 字体：宋体（正文）、黑体（标题）
- 字号：12pt 正文，14pt 场景头，16pt 集数标题
- 场景头加粗
- 台词角色名加粗
- △ 描写用斜体
- 每集结束后插入分页符

### 生成代码逻辑（供 Claude 执行时参考）

```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel, 
        AlignmentType, PageBreak } = require('docx');

// 封面页
const coverPage = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `《${title}》`, bold: true, size: 48 })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `改编自：${originalName}`, size: 24 })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `共${totalEpisodes}集`, size: 24 })]
  }),
];

// 每集内容解析函数
function parseEpisodeToDocx(episodeText) {
  // 按行解析剧本格式
  // 场景头 → Heading 样式
  // △ 描写 → 斜体段落
  // 角色名 → 加粗
  // 台词 → 普通段落，左缩进
  // 分割线 → 段落边框
}
```

---

## 批量导出注意事项

- 超过 10 集时，建议分批导出（避免文件过大）
- .docx 文件建议按「幕」分批：第一幕（1-15集）、第二幕（16-35集）等
- 导出完成后提示用户文件保存位置

---

## 导出后的建议

导出完成后，告知用户：

```
✅ 导出完成！

文件已保存：
- 📄 第X集_标题.md × X个文件
- 📝 《剧名》完整剧本.docx

💡 使用建议：
- .docx 文件可直接发给导演和制片团队
- .md 文件适合在写作软件中进一步编辑
- 如需修改某集，输入 /重写 N 即可重新生成
```
