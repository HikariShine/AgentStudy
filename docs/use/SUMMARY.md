# 综合应用

## 自动发布公众号

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

同时这里为了能够查阅邮件，我使用了两个内置的skill，参考后面内容。

配置好skill之后，就可以让OpenClaw帮你添加心跳内容：新增心跳内容，心跳时使用gog和himalaya检测我的google邮箱以及qq邮箱是否有未读邮件，如果有未读则提醒我，格式要求规范。

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