# 其他小tips

## 常用命令

### 更新OpenClaw版本

openclaw update

更新完成后执行 openclaw doctor --fix，检查配置是否有问题，同时他也能迁移旧版本的配置到新版本

### 打开thinking模式

打开模型的推理思考能力，可以提高准确率，但会增加token消耗。如果不缺token或者不缺钱，又对准确率有要求，可以通过配置打开深度思考模式，

第一种是全局配置: agents.defaults.thinkingDefault，有low,medium,high等级别(补全)，可以修改默认的level

第二种session级别配置：聊天内输入 /think mediun(或者其他级别)，可以单独调整当前session的thinking level

### 观察详细响应

有时候我们一个问题过去，会把OpenClaw整懵，很久不回复，这种一般都是进入循环了，他在尝试各种方法来达到最终的目的。如果我们想看详细的内容，可以通过这种方式打开详细响应：

- /v on 或者 /verbose on ，打开啰嗦模式
- /reason on 打开推理模式并显示思考内容

当然如果你觉得有时候他直接执行不符合你的预期，你可以先让他给你方案然后等你确认再执行，这个可以写入全局记忆。

### 单独执行某个配置

使用 openclaw configure --section web 可以单独执行某节的配置向导。

## 常见问题

### Skill为何没生效？

使用命令 openclaw skills 查看所有的skill，看你的skill第一例是否是missing。如果是missing则表示

如果还是不生效，可以使用 openclaw gateway restart 重启，再使用 /new 新建session，确保全局提示词中存在skill信息。
