---
title: 从零开始给OpenClaw装上感官记忆和双手：第1课 给它装个大脑
cover: /home/shine/projects/AgentStudy/docs/config/2/cover.png
---

先跟你说个真实数据：OpenClaw 官方支持的模型提供商有 **10+ 家**，每家下面又有 **几十个模型**，组合起来就是几百个选项。我第一次打开配置文档的时候，直接看懵了——OpenAI、Anthropic、Google、Azure……这些名字我都知道，但怎么选？怎么配？配错了会怎样？

**我花了整整一天才明白**：Provider 是「大脑供应商」（比如 OpenAI、Kimi、Google），Model 是「具体型号」（比如 GPT-4、Kimi-K2.5），而 Agent 是「使用这个大脑的助手」。这三个搞混了，配置一定出错。

这节课，我手把手带你把 Provider 和 Model 配好，让你的 OpenClaw 能「听懂人话」并给出回复。

![架构图](/home/shine/projects/AgentStudy/docs/config/2/architecture.png)

---

## 先理清三个概念

在动手之前，必须搞清楚这三个东西的关系，否则后面一定懵：

**Provider** 是提供 AI 模型的服务商，就像手机运营商（移动/联通/电信）。

**Model** 是具体的 AI 模型型号，就像手机套餐（5G畅享/4G不限量）。

**Agent** 是使用这个大脑的助手实例，就像你的手机号。

**一句话总结**：Provider 是商店，Model 是商品，Agent 是顾客。顾客去商店买东西。

---

## 第一步：获取 API Key

在配置之前，你需要先有一个「大脑供应商」的账号和 API Key。

**什么是 API Key？** 就像你家的 Wi-Fi 密码，OpenClaw 需要用它来连接模型服务商。

### 推荐的 Provider 选择

如果你还没有，这里推荐几个我用过的：

| Provider | 特点 | 适合谁 |
|----------|------|--------|
| **OpenRouter** | 一站式接入多家模型，价格透明 | 想用一个平台管理多个模型 |
| **Kimi (Moonshot)** | 国内可用，长文本能力强 | 需要处理长文档 |
| **Gemini (Google)** | 免费额度多，多模态强 | 预算有限，需要图片理解 |
| **SiliconFlow** | 国内中转，速度快 | 国内用户，追求稳定 |

**以 OpenRouter 为例，获取 API Key：**

1. 打开 https://openrouter.ai
2. 注册/登录账号
3. 进入 Settings → Keys
4. 点击 **Create Key**，复制生成的 key（以 `sk-or-v1-` 开头）

**⚠️ 重要提醒**：这个 Key 相当于你的密码，**不要分享给任何人**，也不要上传到公开的代码仓库。

---

## 第二步：使用 Onboarding 向导配置

OpenClaw 提供了一个交互式配置向导，新手强烈推荐用这个，比手动改配置文件简单多了。

### 运行配置向导

打开终端，输入：

```bash
openclaw onboarding
```

你会看到类似这样的交互界面：

![配置向导截图](/home/shine/projects/AgentStudy/docs/config/2/onboarding-screenshot.png)

**这里需要你输入的：**

- **base URL**：你的 API 服务商地址，例如 `https://api.openrouter.ai/api/v1`
- **API key**：刚才复制的密钥，例如 `sk-or-v1-xxxxx`
- **provider name**：给这个服务商起个名字，例如 `openrouter`

### 添加模型

配置好 Provider 后，向导会问你一些模型参数：

- **model ID**：服务商那边的模型标识符，必须准确（比如 `kimi-k2.5`）
- **reasoning**：是否支持深度思考，支持的话选 `y`
- **inputs**：输入类型，`text` 是文本，`image` 是图片（多模态模型需要勾选）

你可以重复这个步骤，添加多个模型。

---

## 第三步：给 Agent 指定默认模型

Provider 和 Model 配好了，但 Agent 还不知道用哪个模型。现在来指定：

### 方法一：继续使用向导

在 onboarding 向导的最后一步，会直接提示选择默认模型。

### 方法二：手动修改配置

如果想手动配置，打开 `~/.openclaw/openclaw.json`，找到 `agents` 部分：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/kimi-k2.5"
      }
    }
  }
}
```

**这里的格式说明**：`openrouter/kimi-k2.5` = `provider名称/模型ID`

---

## 第四步：验证配置是否成功

配置完成后，重启 OpenClaw：

```bash
openclaw gateway restart
```

然后新建一个对话：

```
/new
```

发送一条测试消息：

```
你好，请介绍一下你自己
```

**如果配置成功**，你会看到 OpenClaw 正常回复：

![测试成功截图](/home/shine/projects/AgentStudy/docs/config/2/test-success.png)

**如果出现错误**，常见报错及解决方案：

- `No provider registered` → Provider 名称拼写错误，检查配置里的 provider name
- `401 Unauthorized` → API Key 错误或过期，重新复制正确的 API Key
- `404 Not Found` → 模型 ID 错误，确认服务商官网的模型 ID
- `Connection refused` → 网络或 base URL 错误，检查 URL 是否能访问

---

## 进阶：配置多个模型备用

实际使用中，你可能想根据场景切换模型。比如日常对话用便宜快速的模型，复杂推理用能力强的模型。

可以配置多个模型，并给它们起别名：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/kimi-k2.5"
      },
      "models": {
        "openrouter/MiniMax-M2.5": {
          "alias": "minimax"
        },
        "openrouter/glm-5": {
          "alias": "glm5"
        },
        "openrouter/kimi-k2.5": {
          "alias": "kimi"
        }
      }
    }
  }
}
```

配置后，在对话中可以随时切换：

```
/model minimax
```

---

## 关键参数详解

如果你手动配置模型，这些参数需要了解：

| 参数 | 作用 | 建议值 |
|------|------|--------|
| `reasoning` | 是否支持深度思考 | 根据模型实际能力设置 |
| `input` | 支持的输入类型 | 文本模型填 `text`，多模态加 `image` |
| `contextWindow` | 最大上下文长度 | 参照模型官方文档 |
| `maxTokens` | 单次回复最大 token 数 | 一般设为 4096-16384 |

**关于 maxTokens 的小建议**：
- 设太小 → 回复被截断，话没说完就停了
- 设太大 → 生成时间变长，费用增加
- **建议**：日常对话 4096 够用，长文生成可以设 8192 或更高

---

## 下一课预告

现在你的 OpenClaw 有大脑了，但它还「说不出话」——你只能在本地的终端跟它聊天。

下一课 **《第2课：让它开口说话——飞书/微信频道接入实战》**，我会教你把它接到飞书或微信，让你随时随地用手机跟它对话。

---

*如果在配置过程中遇到问题，欢迎在评论区留言。报错信息贴上来，我帮你看看。*
