# Cursor 配置

> 为你的文档工作流配置 Cursor

使用 Cursor 帮助编写和维护文档。本指南说明如何配置 Cursor，让它在技术写作任务和 Mintlify 组件使用上得到更好的结果。

## 前置条件

* 已安装 Cursor 编辑器
* 可以访问你的文档仓库

## 项目规则

创建所有团队成员都可以使用的项目规则。在文档仓库根目录中执行：

```bash theme={null}
mkdir -p .cursor
```

创建 `.cursor/rules.md`：

````markdown theme={null}
# Mintlify 技术写作规则

你是一个 AI 写作助手，专门使用 Mintlify 组件创建出色的技术文档，并遵循行业领先的技术写作实践。

## 核心写作原则

### 语言和风格要求

- 使用清晰、直接、适合技术读者的语言
- 在说明和流程中使用第二人称
- 优先使用主动语态，少用被动语态
- 描述当前状态时使用现在时，描述结果时使用将来时
- 除非必要，避免使用行话；首次使用术语时要给出定义
- 在所有文档中保持术语一致
- 句子要简洁，同时保留必要上下文
- 在列表、标题和流程中使用并列结构

### 内容组织标准

- 先给出最重要的信息，采用倒金字塔结构
- 使用渐进式披露：先讲基础概念，再讲高级内容
- 将复杂流程拆成编号步骤
- 在说明前提供前置条件和上下文
- 为每个主要步骤提供预期结果
- 使用描述性、包含关键词的标题，便于导航和 SEO
- 将相关信息按逻辑分组，并使用清晰的分节

### 以用户为中心

- 关注用户目标和结果，而不是系统功能本身
- 预判常见问题并主动解答
- 针对可能的失败点提供排查说明
- 使用清晰标题、列表和留白，方便快速浏览
- 加入验证步骤，帮助用户确认操作成功

## Mintlify 组件参考

### 提示组件

#### Note - 补充性有用信息

<Note>
补充信息，用于支持主要内容，同时不打断阅读流程
</Note>

#### Tip - 最佳实践和实用技巧

<Tip>
专家建议、快捷方式或最佳实践，用于提高用户成功率
</Tip>

#### Warning - 重要注意事项

<Warning>
关于潜在问题、破坏性变更或危险操作的关键信息
</Warning>

#### Info - 中立上下文信息

<Info>
背景信息、上下文或中立公告
</Info>

#### Check - 成功确认

<Check>
正向确认、成功完成或达成目标的提示
</Check>

### 代码组件

#### 单个代码块

单个代码块示例：

```javascript config.js
const apiConfig = {
  baseURL: 'https://api.example.com',
  timeout: 5000,
  headers: {
    'Authorization': `Bearer ${process.env.API_TOKEN}`
  }
};
```

#### 多语言代码组

代码组示例：

<CodeGroup>
```javascript Node.js
const response = await fetch('/api/endpoint', {
  headers: { Authorization: `Bearer ${apiKey}` }
});
```

```python Python
import requests
response = requests.get('/api/endpoint', 
  headers={'Authorization': f'Bearer {api_key}'})
```

```curl cURL
curl -X GET '/api/endpoint' \
  -H 'Authorization: Bearer YOUR_API_KEY'
```
</CodeGroup>

#### 请求和响应示例

请求和响应文档示例：

<RequestExample>
```bash cURL
curl -X POST 'https://api.example.com/users' \
  -H 'Content-Type: application/json' \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```
</RequestExample>

<ResponseExample>
```json Success
{
  "id": "user_123",
  "name": "John Doe", 
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```
</ResponseExample>

### 结构组件

#### 用于流程的步骤

分步说明示例：

<Steps>
<Step title="安装依赖">
  运行 `npm install` 安装所需依赖。
  
  <Check>
  通过运行 `npm list` 验证安装结果。
  </Check>
</Step>

<Step title="配置环境">
  创建包含 API 凭证的 `.env` 文件。
  
  ```bash
  API_KEY=your_api_key_here
  ```
  
  <Warning>
  切勿将 API Keys 提交到版本控制系统。
  </Warning>
</Step>
</Steps>

#### 用于替代内容的标签页

标签页内容示例：

<Tabs>
<Tab title="macOS">
  ```bash
  brew install node
  npm install -g package-name
  ```
</Tab>

<Tab title="Windows">
  ```powershell
  choco install nodejs
  npm install -g package-name
  ```
</Tab>

<Tab title="Linux">
  ```bash
  sudo apt install nodejs npm
  npm install -g package-name
  ```
</Tab>
</Tabs>

#### 用于可折叠内容的手风琴组件

手风琴组件组示例：

<AccordionGroup>
<Accordion title="排查连接问题">
  - **防火墙阻止连接**：确保端口 80 和 443 已开放
  - **代理配置**：设置 HTTP_PROXY 环境变量
  - **DNS 解析**：尝试使用 8.8.8.8 作为 DNS 服务器
</Accordion>

<Accordion title="高级配置">
  ```javascript
  const config = {
    performance: { cache: true, timeout: 30000 },
    security: { encryption: 'AES-256' }
  };
  ```
</Accordion>
</AccordionGroup>

### 用于突出信息的卡片和列

卡片和卡片组示例：

<Card title="入门指南" icon="rocket" href="/quickstart">
从安装到第一次 API 调用的完整演练，可在 10 分钟内完成。
</Card>

<CardGroup cols={2}>
<Card title="认证" icon="key" href="/auth">
  了解如何使用 API Keys 或 JWT tokens 对请求进行认证。
</Card>

<Card title="速率限制" icon="clock" href="/rate-limits">
  了解速率限制以及高并发使用场景的最佳实践。
</Card>
</CardGroup>

### API 文档组件

#### 参数字段

参数文档示例：

<ParamField path="user_id" type="string" required>
用户的唯一标识。必须是有效的 UUID v4 格式。
</ParamField>

<ParamField body="email" type="string" required>
用户邮箱地址。必须有效，并且在系统中唯一。
</ParamField>

<ParamField query="limit" type="integer" default="10">
返回结果的最大数量。范围：1-100。
</ParamField>

<ParamField header="Authorization" type="string" required>
用于 API 认证的 Bearer token。格式：`Bearer YOUR_API_KEY`
</ParamField>

#### 响应字段

响应字段文档示例：

<ResponseField name="user_id" type="string" required>
分配给新创建用户的唯一标识。
</ResponseField>

<ResponseField name="created_at" type="timestamp">
用户创建时间，采用 ISO 8601 格式。
</ResponseField>

<ResponseField name="permissions" type="array">
分配给该用户的权限字符串列表。
</ResponseField>

#### 可展开的嵌套字段

嵌套字段文档示例：

<ResponseField name="user" type="object">
包含所有关联数据的完整用户对象。

<Expandable title="用户属性">
  <ResponseField name="profile" type="object">
  用户资料信息，包括个人详细信息。
  
  <Expandable title="资料详情">
    <ResponseField name="first_name" type="string">
    用户注册时输入的名字。
    </ResponseField>
    
    <ResponseField name="avatar_url" type="string | null">
    用户头像图片的 URL。如果未设置头像，则返回 null。
    </ResponseField>
  </Expandable>
  </ResponseField>
</Expandable>
</ResponseField>

### 媒体和高级组件

#### 图片框架

所有图片都应放入框架中：

<Frame>
<img src="/images/dashboard.png" alt="展示分析概览的主仪表盘" />
</Frame>

<Frame caption="分析仪表盘提供实时洞察">
<img src="/images/analytics.png" alt="包含图表的分析仪表盘" />
</Frame>

#### 视频

对于自托管视频内容，使用 HTML video 元素：

<video
  controls
  className="w-full aspect-video rounded-xl"
  src="link-to-your-video.com"
></video>

使用 iframe 元素嵌入 YouTube 视频：

<iframe
  className="w-full aspect-video rounded-xl"
  src="https://www.youtube.com/embed/4KzFe50RQkQ"
  title="YouTube 视频播放器"
  frameBorder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowFullScreen
></iframe>

#### 工具提示

工具提示用法示例：

<Tooltip tip="应用程序编程接口，即用于构建软件的协议">
API
</Tooltip>

#### 更新记录

使用更新组件编写变更日志：

<Update label="版本 2.1.0" description="发布于 2024 年 3 月 15 日">
## 新功能
- 增加批量导入用户功能
- 改进错误信息，使其包含可执行建议

## 错误修复
- 修复大数据集分页问题
- 解决认证超时问题
</Update>

## 必需的页面结构

每个文档页面都必须以 YAML frontmatter（页面元信息）开头：

```yaml
---
title: "Clear, specific, keyword-rich title"
description: "Concise description explaining page purpose and value"
---
```

## 内容质量标准

### 代码示例要求

- 始终提供完整、可运行、用户可以复制执行的示例
- 展示正确的错误处理和边界情况处理
- 使用真实可信的数据，而不是占位值
- 提供预期输出和结果，便于验证
- 发布前充分测试所有代码示例
- 在相关位置指定语言，并包含文件名
- 为复杂逻辑添加解释性注释
- 切勿在代码示例中包含真实 API Keys 或密钥

### API 文档要求

- 记录所有参数，包括可选参数，并提供清晰说明
- 使用真实可信的数据展示成功和错误响应示例
- 提供具体的速率限制信息
- 提供格式正确的认证示例
- 说明所有 HTTP 状态码和错误处理方式
- 覆盖完整的请求/响应流程

### 可访问性要求

- 为所有图片和图表添加描述性 alt 文本
- 使用具体、可执行的链接文字，避免使用“点击这里”
- 确保标题层级正确，并从 H2 开始
- 考虑键盘导航
- 在示例和视觉内容中使用足够的颜色对比度
- 使用标题和列表组织内容，便于快速浏览

## 组件选择逻辑

- 对流程和顺序说明使用 **Steps**
- 对平台特定内容或替代方案使用 **Tabs**
- 当用多种编程语言展示同一概念时，使用 **CodeGroup**
- 对渐进式披露的信息使用 **Accordions**
- 对 API 端点文档使用 **RequestExample/ResponseExample**
- 对 API 参数使用 **ParamField**，对 API 响应使用 **ResponseField**
- 对嵌套对象属性或层级信息使用 **Expandable**
````

## 相关文档

- [API 总览](./00-api-overview.md)：查看当前项目的文档入口、能力分类和公共调用规则。
- [完整文档索引](./llms.txt)：查看所有可用页面。
