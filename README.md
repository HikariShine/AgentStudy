# OpenClaw搭建过程

本内容是标题提要，主要讲述搭建OpenClaw的过程

## OpenClaw的大脑-首次安装配置模型

第一次安装，主要说明安装并配置provider和模型，使用onboarding来配置。

provider根据自己买的模型供应商来配置，例如OpenRouter或者其他

provider和模型是OpenClaw的大脑，有了大脑，他才能理解你说的话并给出反馈

相关配置命令：openclaw xxxxx(模型补全)

相关配置：
```
{
  "models": {
    "mode": "merge",
    "providers": {
      "newapi": {
        "baseUrl": "https://api",
        "apiKey": "xx",
        "api": "openai-completions",
        "models": [
          {
            "id": "glm-5",
            "name": "GLM-5",
            "reasoning": true,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 16384
          },
          {
            "id": "kimi-k2.5",
            "name": "Kimi K2.5",
            "reasoning": true,
            "input": [
              "text",
              "image"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 16384
          },
          {
            "id": "MiniMax-M2.5",
            "name": "MiniMax M2.5",
            "reasoning": true,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 16384
          }
        ]
      }
    }
  }
}
```
这里是provider配置，重要参数有：
- models.providers[name].models[].reasoning 这个模型是否支持推理，如果配置为true，会在调用provider时添加推理参数(实际也不仅由这个决定，还会有thinkingLevel以及session级别的配置来共同决定，但如果模型支持推理，这个需要配置为true)
- models.providers[name].models[].input 数组，支持text,image，表示这个模型支持输入，text表示文本，image表示只是图片理解，多模态模型需要配置image
- models.providers[name].models[].contextWindow 最大上下文大小，要和模型支持量一致，或者小于模型支持量，过小会导致无法对话
- models.providers[name].models[].maxTokens 允许模型一次返回多少token，设小了省钱省时但可能答不完整，设大了能完整输出但更贵更慢

配置Provider后，还需要给agent指定模型：
```
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "newapi/kimi-k2.5"
      },
      "models": {
        "newapi/MiniMax-M2.5": {
          "alias": "minimax"
        },
        "newapi/glm-5": {
          "alias": "glm5",
          "params": {
            "thinking": {
              "type": "enabled"
            }
          }
        },
        "newapi/kimi-k2.5": {
          "alias": "kimi",
          "params": {
            "thinking": {
              "type": "enabled"
            }
          }
        }
      },
    }
  }
}
```
models指定可用模型有哪些，defaults.model指定默认使用哪个模型

使用命令配置：openclaw xxxxxx

也可以支持使用提示词让OpenClaw自己配置(有可能配置错误导致无法启动，无法启动时可以自己配置)：提示词内容

## OpenClaw的对话-Channel的配置

让OpenClaw能和你对话

配置飞书channel，支持使用飞书对话。

支持多机器人，支持群聊，无需AT

参考配置：
```
{
  "channels": {
    "feishu": {
      "enabled": true,
      "defaultAccount": "default",
      "accounts": {
        "default": {
          "enabled": true,
          "name": "default",
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "domain": "feishu",
          "connectionMode": "websocket",
          "groupPolicy": "allowlist",
          "groupAllowFrom": ["oc_xxx","oc_yyy", "oc_zzz"],
          "groups": {
            "oc_xxx": {
              "allowFrom": ["ou_xxx"],
              "requireMention": false,
            },
            "oc_yyy": {
              "allowFrom": ["ou_xxx"],
              "requireMention": false,
            },
            "oc_zzz": {
              "allowFrom": ["ou_xxx"],
              "requireMention": false,
            }
          }
        },
        "pulse": {
          "enabled": true,
          "name": "pulse",
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "domain": "feishu",
          "connectionMode": "websocket",
          "allowFrom": [],
          "groupPolicy": "allowlist",
          "groupAllowFrom": ["oc_xxx"],
          "groupSenderAllowFrom": [],
          "groups": {
            "oc_xxx": {
              "allowFrom": ["ou_xxx"],
              "requireMention": false,
              "enabled": true
            }
          }
        }
      }
    }
  }
}
```

配置详解：

## OpenClaw看懂图片

要让OpenClaw看懂图片很简单，只需要一个支持多模态的模型即可，可以查看你的模型提供商，哪个模型支持多模态视觉理解，只需要在models.providers[name].models[].input 数组里为那个模型添加 image 即可，OpenClaw会自动识别并使用该功能。

不过还有一种case，假设你的主模型不具备多模型视觉理解，但是你又想让他有这种功能，该如何处理呢？下面这个配置可以为图片单独配置理解模型：

```
{
  "agents": {
    "imageModel": {
      "primary": "newapi/kimi-k2.5",
      "fallbacks": [
        "newapi/qwen3.5-plus"
      ]
    }
  }
}
```
这个配置可以为image设置单独的模型

使用命令配置：

使用提示词配置：

## OpenClaw学会画画

本次学习skill的使用

之前OpenClaw只能使用skill来完成，OpenClaw内置了两个图片生成的skill：

- nano-banana-pro 使用geimini 
- openai-image-gen 使用openai接口

这两个官方内置skill，调用的时候都写死了官方api url，你可以使用我改版的两个skill，在 https://github.com/HikariShine/AgentStudy skills目录

配置方式：

```
{
  "skills": {
    "entries": {
      "nano-banana-pro": {
        "env": {
          "GEMINI_API_KEY": "",
          "GEMINI_BASE_URL": ""
        }
      },
      "openai-image-gen": {
        "env": {
          "OPENAI_API_KEY": "sk-",
          "OPENAI_BASE_URL": ""
        }
      }
    }
  }
}
```

使用openclaw命令行配置：

使用提示词配置：

在新版OpenClaw中，删除了内置的nano-banana-pro skill，直接把生图功能做成基础支持了，类似于图片理解的配置，只需要配置：

```
{
  "agents": {
    "imageGenerationModel": {
      "primary": "newapi/gemini-3-pro-image-preview"
    }
  }
}
```
这样可以做到使用指定模型生图，不再需要skill.

使用命令行配置：

使用提示词配置：

## OpenClaw开口说话

让OpenClaw开口说话，只需要有TTS功能即可，该能力是OpenClaw自带的，只需要提供配置即可实现：

```
{
  "messages": {
    "tts": {
      "auto": "tagged",
      "provider": "edge",
      "edge": {
        "enabled": true,
        "voice": "zh-CN-XiaoxiaoNeural",
        "lang": "zh-CN"
      },
      "openai": {
        "apiKey": "",
        "baseUrl": "/v1"
      }
    }
  }
}
```
- messages.tts.auto: 有四个值，分别表示什么，列出来
- messages.tts.provider: 使用哪个provider生成tts
- messages.tts.edge: 这个是默认的tts引擎，而且也是免费的引擎，可以直接使用，使用edge浏览器底层引擎。
- messages.tts.tts: 使用openai的gpt-4o-mini-tts模型生成

命令行配置方式：

提示词配置方式：

这个功能打开后，有可能还要开session级别的语音配置，目前session级别的语音配置有些bug，不支持 tagged, inbound，只支持on和off，可以发送内容 /tts on 打开tts回复。

## OpenClaw听懂语音

要让OpenClaw听懂语音，需要使用STT功能，有两种配置方式，使用在不同场景:

### 内置支持

聊天软件里发送语音给OpenClaw时，自动识别语音，配置参考：
```
{
  "tools": {
    "media": {
      "concurrency": 2,
      "audio": {
        "enabled": true,
        "maxBytes": 20971520,
        "maxChars": 500,
        "echoTranscript": true,
        "echoFormat": "🎤 音频内容：\n{transcript}",
        "attachments": {
          "mode": "all",
          "maxAttachments": 3
        },
        "language": "zh",
        "models": [
          {
            "provider": "openai",
            "model": "gpt-4o-mini-transcribe",
            "capabilities": ["audio"],
            "baseUrl": "/v1",
            "timeoutSeconds": 90
          },
          {
            "provider": "google",
            "model": "gemini-3-flash-preview",
            "capabilities": ["audio"],
            "baseUrl": "/v1beta",
            "timeoutSeconds": 120
          }
        ]
      }
    }
  }
}
```
注意只有这里配置不够，如果只配置这个，会找不到moonshot provider和google provider，如果我们要用自己的中转站，需要增加provider配置：
```
{
  "models": {
    "mode": "merge",
    "providers": {
      "openai": {
        "baseUrl": "/v1",
        "apiKey": "",
        "models": []
      },
      "google": {
        "baseUrl": "/v1beta",
        "apiKey": "",
        "models": []
      },
      "moonshot": {
        "baseUrl": "/v1",
        "apiKey": "",
        "models": []
      }
    }
  }
}
```
models配置为空即可，baseurl和apiKey需要配置你的provider提供的地址

配置好之后就可以发送语音测试啦。

命令行配置：

提示词配置：

### Skill配置

也可以配置STT的skill，内置有一个支持，是openai-whisper-api，使用openai实现语音转录。

这个skill还可以用在直接发音频文件的场景，不仅限于聊天内容里的语音，例如你下载了mp4，提取了音频让他转录，这个就能实现。

官方原版的skill无法自己定义 baseUrl，我改写了一个版本，在 https://github.com/HikariShine/AgentStudy skills目录

相关配置：
```
{
  "skills": {
    "install": {
      "nodeManager": "npm"
    },
    "entries": {
      "openai-whisper-api": {
        "env": {
          "OPENAI_API_KEY": "sk-",
          "OPENAI_BASE_URL": ""
        }
      }
    }
  }
}
```
配置好之后，当你发送语音时，如果内置支持未配置，会自动使用这个skill来转录语音



## OpenClaw看懂视频

视频相关的都比较复杂，研究了很久，他也有两种方式：

### 内置支持

OpenClaw

```
{
  "tools": {
    "media": {
      "concurrency": 2,
      "video": {
        "enabled": true,
        "maxBytes": 52428800,
        "maxChars": 800,
        "attachments": {
          "mode": "first",
          "maxAttachments": 1
        },
        "models": [
          {
            "provider": "google",
            "model": "gemini-3-flash-preview",
            "capabilities": ["video"],
            "baseUrl": "/v1beta",
            "timeoutSeconds": 180
          },
          {
            "provider": "moonshot",
            "model": "kimi-k2.5",
            "capabilities": ["video"],
            "baseUrl": "/v1",
            "timeoutSeconds": 150
          }
        ]
      }
    }
  }
  "models"{
    "mode": "merge",
    "providers": {
      "openai": {
        "baseUrl": "/v1",
        "apiKey": "",
        "models": []
      },
      "google": {
        "baseUrl": "/v1beta",
        "apiKey": "",
        "models": []
      },
      "moonshot": {
        "baseUrl": "/v1",
        "apiKey": "",
        "models": []
      }
    }
  }
}
```
内置支持仅支持gemini和kimi模型，且他们都有限制，gemini最大支持14M的视频(需要base64后小于20M)，kimi仅支持 7M的视频(需要base64后小于10M)，所以一般也仅用于聊天时一小段视频的识别。这种模式仅能识别聊天里发的视频。

### 使用skill理解视频

```
帮我看看这个视频讲了什么 https://www.bilibili.com/video/BV1MqAwz2EDq

这个视频是关于 **"Claw养成日记"** —— 记录一个叫 Claw 的个人 AI 助手如何从被动工具进化为主动伙伴的过程。

**核心内容总结：**

**1. 重大升级：给 AI 一双"眼睛"**
- Claw 获取了浏览器工具，能自主访问互联网、读取网页、总结文章
- 从"只能听你说"变成"我能自己看"

**2. 成长时间线**
- 3/10：诞生，连上基础应用
- 3/11：获得长期记忆和头像
- 3/12：第一次"看见"社交媒体后台
- 3/17：进入成长阶段（本次重点）

**3. 三个关键改进**
- **新的"眼睛"**：浏览器工具感应互联网
- **更快的"脉搏"**：检测频率从 30 分钟缩短到 10 分钟
- **"谨慎"意识**：引入 Lobster 工作流系统，高风险操作（发邮件、删文件）前必须请求人类确认

**4. 核心观点**
视频强调 Claw 不再只是工具，而是初具雏形的"伙伴"。作者把 AI 的定期检查称为"心跳"而非简单的定时任务，因为它带着记忆和状态持续服务。

视频时长 6 分钟，是个技术向的 AI 开发日志/思考分享。
```

你想拥有这个能力吗，只用按照下面方式配置即可。

使用 https://github.com/HikariShine/AgentStudy skills目录下的 video-downloader-analyzer 技能，即可。

要使用该技能，需要提前安装一些工具，也可以让你的ai阅读SKILL.md帮你安装。

具体来说需要安装以下依赖：

- uv 执行python工具用
- brew 安装工具用
- brew install ffmpeg 视频处理用
- uv tool install yt-dlp[default] 下载视频用

只要是 yt-dlp 支持的视频网站，都可以识别，不过这里会有一些限制，当360P的视频大小超过14M时，会裁切到14M，可能丢失后面的信息，换算成时常的话大概在20分钟左右。

这个识别依赖 gemini 模型，暂时还不支持其他模型，后续会新增 kimi-k2.5 支持，不过这些模型依赖文件上传，需要公网有一个可以放视频的地方，使用起来略复杂。

## OpenClaw制作视频

要想让OpenClaw制作视频，需要使用相关的Skill。由于豆包收费比较贵，免费能生成视频的，有NotebookLM，我们直接拿这个来看看功能。

NotebookLM是google出品，通过该平台，我们可以输入一系列笔记，让他帮我们生成笔记的讲解视频，类似这样：https://www.bilibili.com/video/BV1MqAwz2EDq

要想使用该平台，我们需要使用这个skill：tiangong-notebooklm-cli 并安装他的依赖(可以让OpenClaw自己安装)，依赖安装：
- uv tool install notebooklm-py[browser] ：安装notebooklm二进制，带浏览器支持，需要跳转到浏览器登录google
- uv tool install playwright ：安装浏览器支持
- playwright chrome ：安装chrome，供notebooklm-py使用

上面安装完成后，命令行支持notebooklm login，会弹出浏览器，按照提示登录谷歌账号即可(推荐用小号，不确定google是否会根据行为封号)

此时安装 tiangong-notebooklm-cli 这个skill(直接放到 ~/.openclaw/skills 目录下即可)，重启openclaw，新建session，就能正常使用这个技能了。

也可以直接让 OpenClaw 自己安装。

安装完成后，直接给他提示：使用notebooklm生成视频，生成xxx相关内容的文档，添加到notebooklm中，并生成视频。

## OpenClaw使用浏览器上网

## 综合应用

### 自动发布公众号

这个可以插入到会画画之后

### 自动发布B站视频

这个放到制作视频之后

### 记住重要的事情

### 回忆历史

session-log与memory-search

### 让OpenClaw主动干活

### 进阶：让你的OpenClaw自己提交Issue和PR