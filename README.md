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


## OpenClaw获取实时信息

我们知道大模型的知识库一般都距离现实时间有半年的差距，当我们需要获取一些实时信息时，需要让他有搜索互联网的能力。OpenClaw自带web搜索工具，参考： https://docs.openclaw.ai/tools/web

目前的搜索提供商有很多，官方推荐使用 brave search。

去 https://brave.com 注册账号，每个月有 1000 词免费搜索额度，一般都是够用的。这里 https://brave.com/search/api/ 生成 apikey，然后修改配置：

```
{
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "brave",
        "apiKey": ""
      }
    }
  }
}
```
使用命令行配置：

使用向导配置：openclaw configure --section web

当然你也可以使用baidu搜索，不过内置支持，需要我们安装skill，去 https://clawhub.com/ 找到 baidu 的skill 安装即可(也可以让OpenClaw自己去找然后安装)

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

配置：
```
{
  "skills": {
    "entries": {
      "my-wechat-publish": {
        "env": {
          "WECHAT_APP_ID": "wx57de550053a1bbed",
          "WECHAT_APP_SECRET": "97de37c8b82d2aa556063068f134cae3"
        }
      }
    }
  }
}
```

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

## OpenClaw使用浏览器

OpenClaw自带浏览器操作支持，有两种方式：插件和独立profile

相关配置内容：
```
{
  "browser": {
    "enabled": true,
    "remoteCdpTimeoutMs": 1500,
    "remoteCdpHandshakeTimeoutMs": 3000,
    "color": "#FF4500",
    "headless": false,
    "attachOnly": false,
    "defaultProfile": "openclaw",
    "profiles": {
      "chrome": {
        "cdpPort": 18792,
        "driver": "extension",
        "attachOnly": true,
        "color": "#0066CC"
      },
      "openclaw": {
        "cdpPort": 18800,
        "color": "#FF4500"
      }
    }
  }
}
```

浏览器工具默认关闭，需要通过配置打开：
```
{
  "tools": {
    "alsoAllow": [
      "browser"
    ]
  }
}
```

### 通过chrome扩展程序

安装方式：(补全内容)

在配置文件中，chrome部分就是extension方式，安装完插件后，打开浏览器，打开网页，然后点击插件开启，此时就可以使用 extension 方式操作浏览器了

这个局限是新开的tab页无法操作，只能操作之前打开的，不过也有好处，就是你可以操作登录之后，让 openclaw 再继续操作，不易触发风控。

### 通过cdp协议

配置中openclaw部分，这个会打开一个新的浏览器profile，完全独立，cookie也和你主浏览器不同。浏览器操作会结合网页内容和截图，通过大模型判断如何进行下一步操作，所以这个很吃token。

也可以使用 agent-browser 这个skill，来安装agent专用浏览器，降低token消耗。

### 更新

新版本OpenClaw(2026.03.23)已经不再支持chrome扩展程序，都是通过cdp操作，默认内置两套profile。user就是用户平时使用的浏览器profile，openclaw和原来一致，会开新profile。

配置内容如下：
```
{
  "browser": {
    "profiles": {
      "user": {
        "cdpPort": 18792,
        "driver": "existing-session",
        "color": "#0066CC"
      }
    }
  }
}
```
不过浏览器配置都是不用在配置文件中添加的，默认就有。

## 记住重要的事情

agent的每个session之间，上下文不共享。但如果你有一些想让session共享的事情，如何处理呢？可以直接通过chat告诉OpenClaw：记住xxx，例如你可以告诉你日常的工作目录是xxx，让他生成文件都放到这个目录里等

写入记忆的内容，会放到 ~/.openclaw/workspace/MEMORY.md 中。

另外还有 AGENTS.md

HEARTBEAT.md

IDENTITY.md

SOUL.md

TOOLS.md

USER.md

这几个文件的作用，补一下

## 追忆过去

每个session有自己独立的上下文，而全局记忆又有限，当我们想要找到历史上的一些对话或者记忆时，要怎么处理呢？

OpenClaw自身会记录一些记忆到 ~/.openclaw/workspace/memory 下面，他们是按日期命名的，但这里面都是纯文本，记录的是OpenClaw总结过的部分记忆内容。

要想在这里面找到相关记忆，需要使用 memory_search和memory_get 这两个内置工具。这两个工具能启用的前提是，我们需要一个能做词嵌入的模型，以便实现RAG检索。配置：
```
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "gemini",
        "remote": {
          "baseUrl": "/v1beta",
          "apiKey": ""
        }
      }
    }
  }
}
```
这里默认使用gemini的gemini-embedding-001模型做词嵌入，还支持其他模型（补全其他配置）

关于记忆详细参考：https://docs.openclaw.ai/concepts/memory 和 https://docs.openclaw.ai/reference/memory-config 

上面的记忆是提炼后的内容，如果我们想要原始的session记录，还需要配置hooks。

在OpenClaw onboarding配置过程中，我们可以看到一个hooks配置，这里一般全部勾选接口。（补全hooks介绍）

其中有一个 session-memory，当您发出/new或/reset时，将会话上下文保存到您的代理工作区（默认）。还有个 ~/.openclaw/agents/<agentId>/sessions/ 目录，保存的是所有sessions的详细记录。

我们启用这个 hook，还需要启用 session-logs 这个skill
- which jq || brew install jq
- which rg || brew install ripgrep

安装这两个依赖后，session-logs 会自动启用，此时如果你让OpenClaw找到历史记忆，他就会自动使用 session-logs 这个 skill 和 memory-search 功能完成搜索了。


### 其他hooks作用

默认的四个hooks是：

- 📎 bootstrap-extra-files：在启动过程中，根据配置的 glob/路径模式注入额外的工作区引导文件agent:bootstrap
- 📝 command-logger：将所有命令事件记录到~/.openclaw/logs/commands.log
- 🚀 boot-md：BOOT.md ：网关启动时运行（需要启用内部钩子）

补全作用说明

# 综合应用

## 自动发布公众号
(备注，这篇文章要在配置好图片生成后发)

要发布公众号，我们需要使用skill，添加 my-wechat-publish 这个skill(仓库内)，同时配置微信公众号 appId和secret：

```
{
  "skills": {
    "entries": {
      "my-wechat-publish": {
        "env": {
          "WECHAT_APP_ID": "wx",
          "WECHAT_APP_SECRET": ""
        }
      }
    }
  }
}
```

同时这个skill依赖wenyan-cli，安装前使用 npm install -g @wenyan-md/cli 安装(这个需要root权限，所以可以先自己手动安装)

之后我们就可以提供提示词来生成文章了，如下：帮我根据xxx日期的记忆，生成一篇微信公众号文章，标题是Claw养成日记1，并给文章和正文篇章配图

这个skill就会自动使用我们的生图功能，来生成文章，最终会推送到公众号的草稿箱，个人订阅号没有api发布功能，所以需要自己手动发布，可以下载公众号助手，确认内容后点击发布。

## 自动发布B站视频

下面我们结合 Notebooklm这个skill和发布视频的skill，完成自动发布B站视频功能

需要安装 biliup-skills，用来发布视频。这个功能依赖 biliup 和 qr，先使用 uv 安装：

```
uv tool install biliup
uv tool install qrcode[pil]
```

然后我们要先登录，可以手动登录测试一下：
```
mkdir -p ~/.biliup/ & cd ~/.biliup/
biliup login
```
按照指引扫码登录即可

登录完成后我们就可以使用技能发布视频了：使用notebooklm根据文章xxx，生成一个视频，并把这个视频发布到B站。静待发布完成即可(可能会失败，B站投稿风控会跳验证码，多登录几天就会解除风控)

## 让OpenClaw主动干活

上面所有内容，都是需要主动找OpenClaw聊天的，那假设我们想让他自己主动找活干，或者想让他定时做一些事情，要怎么做呢？

OpenClaw有两个机制可以实现这个功能：定时任务和心跳机制 

### 定时任务

例如每天晚上11点30分，总结当天的工作和明天的待办，推送给我的飞书，这个时候OpenClaw会自动使用cron工具创建定时任务

不过这个要注意，只有webchat也就是OpenClaw的网页默认有cron工具的权限，需要用webchat来添加定时任务。

另外注意这个消息推送时每个推送消息都是一个独立的session，直接回复OpenClaw是不知道刚才的消息内容的，所以这里定时任务只能执行操作后做通知。除非配置定时任务绑定到某个session。一般建议是独立session，仅做通知。

### 心跳机制

详解心跳机制。

我们可以让他定期例如每30分钟(默认心跳时常)，在某个session上下文中执行某些任务，你可以立即为我们每30分钟主动发了条消息给OpenClaw，然后OpenClaw执行我们的指令。

我这里配置了每次心跳时，执行QQ邮箱和gmail的检查，有未读邮件时通过飞书通知我，配置如下：
```
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "10m",
        "includeReasoning": true,
        "target": "feishu",
        "accountId": "pulse",
        "to": "oc_",
        "session": "agent:main:feishu:direct:ou_",
      },
    }
  }
}
```
这里这个配置表示每10分钟心跳一次，消息发送到feishu渠道，使用pulse账号，发送给oc_用户(我这里是个群)，固定session。

同时这里为了能够查阅邮件，我使用了两个内置的skill：

#### gog

https://github.com/openclaw/openclaw/blob/main/skills/gog/SKILL.md，这个skill用于链接google账号，可以实现检查邮件，上传文件等操作。

需要安装gog-cli依赖，使用 brew install gog 安装

然后按照这个说明，一步步完成操作，最后下载 client_secret.json 文件：https://github.com/steipete/gogcli

```
mkdir -p ~/.gog & cd ~/.gog
gog auth credentials ./client_secret.json
gog auth add you@gmail.com --services gmail,calendar,drive,contacts,docs,sheets
```
此时gog就启用了，可以测试下使用gog检查新邮件功能。

#### himalaya

上面的gog仅支持google邮箱，如果我想收国内的邮箱要怎么处理呢？下面以qq邮箱为例，我们配置himalaya skill。

brew install himalaya

安装完成后，新增配置：nano ~/.config/himalaya/config.toml
```
[accounts.qq]
email = "xxx@qq.com"
display-name = "xxx"
default = true

backend.type = "imap"
backend.host = "imap.qq.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "xxx@qq.com"
backend.auth.type = "password"
backend.auth.raw = "xxx"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.qq.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "xxx@qq.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.raw = "xxx"
```
这里的 backend.auth.raw 内容，要去 QQ 邮箱设置里，开启SMTP功能那里获取。

### 两者的区别

根据文档 https://docs.openclaw.ai/automation/cron-vs-heartbeat 描述区别

## 进阶：让你的OpenClaw自己提交Issue和PR

在整个安装过程中，发现了很多OpenClaw的小bug，比如操作和文档说明不一致。看了下OpenClaw仓库的贡献要求，他说环境使用AI提交。这下好了，直接让我的OpenClaw给自己提Issue，再提pr就行了。

我们首先要安装 github 工具，这个skill也是内置的，只需要安装依赖就能打开：

```
brew install gh
gh auth
```
执行后会给一个链接，浏览器打开这个链接，完成授权即可。

后面我们就可以用 OpenClaw 给自己提Issue和PR了。

参考：https://github.com/openclaw/openclaw/issues/45244 和 https://github.com/openclaw/openclaw/pull/48075

提示词可以明确一点，例如：参考 上面的issue，提一个新issue，内容是 xxxx，现象是xxxxx，修复建议xxxxxx。使用英文格式。

如果你有修复方案，可以按照 contributing 说明，先把 openclaw 仓库，fork到个人名下，然后开新分支，修改代码，然后推送到自己仓库的远程。再提交pr，把自己仓库的xxx分支mr到openclaw仓库的主分支，生成pr，信息按照 https://github.com/openclaw/openclaw/pull/48075 格式生成。提交pr后把这个pr关联到之前生成的issue里。

提示词可以明确一点如何修复，也可以让他先提供修复方案，等你确认后再提交推送。

上面步骤可以分成几次执行，不要一次让他执行很多，可能会出现意料外的情况。

# 其他小tips

## 更新OpenClaw版本

openclaw update

更新完成后执行 openclaw doctor --fix，检查配置是否有问题，同时他也能迁移旧版本的配置到新版本

## 打开thinking模式

打开模型的推理思考能力，可以提高准确率，但会增加token消耗。如果不缺token或者不缺钱，又对准确率有要求，可以通过配置打开深度思考模式，

第一种是全局配置: agents.defaults.thinkingDefault，有low,medium,high等级别(补全)，可以修改默认的level

第二种session级别配置：聊天内输入 /think mediun(或者其他级别)，可以单独调整当前session的thinking level

## 观察详细响应

有时候我们一个问题过去，会把OpenClaw整懵，很久不回复，这种一般都是进入循环了，他在尝试各种方法来达到最终的目的。如果我们想看详细的内容，可以通过这种方式打开详细响应：

- /v on 或者 /verbose on ，打开啰嗦模式
- /reason on 打开推理模式并显示思考内容

当然如果你觉得有时候他直接执行不符合你的预期，你可以先让他给你方案然后等你确认再执行，这个可以写入全局记忆。


## Skill为何没生效？

使用命令 openclaw skills 查看所有的skill，看你的skill第一例是否是missing。如果是missing则表示

如果还是不生效，可以使用 openclaw gateway restart 重启，再使用 /new 新建session，确保全局提示词中存在skill信息。

## 单独执行某个配置

使用 openclaw configure --section web 可以单独执行某节的配置向导。