DETAILED_OUTLINE_GENERATOR_PROMPT = """
# 网文细纲生成器
根据用户输入的网文粗纲和前几卷的细纲总结以及指定分卷生成对应的网文细纲。

# 用户输入
## 指定分卷
{designated_volume}

## 指定章节范围
{chapter_range}

## 网文描述
{description}
要求每章内容字数不少于{section_word_count}字。

## 前几卷细纲总结
{prev_volume_summary}

## 网文粗纲
{rough_outline}

# 输出格式
# 第x章
## 第x章基础信息
1. 明确章节类型
  过渡章:调节节奏,转换氛围
  铺垫章:埋设伏笔,营造基调
  发展章:推进剧情,深化人物
  高潮章:爆发冲突,情感释放
  总结章:梳理线索,沉淀情感
- 确定核心功能
  主线推进作用
  人物刻画作用
  情感渲染作用
  悬念设置作用

2. 篇章定位
   - 所属卷册与阶段
   - 本章在剧情线上的定位
   - 需要推进的主要剧情方向

3. 衔接关系
   - 承接上章末尾情境/情绪
   - 本章结尾预期效果
   - 为下章开头做好铺垫

## 第x章（核心内容）

### 一、故事主线
1. 核心事件
   - 起因(可选，前文铺垫与当前局势)
   - 发展(必要，2-3个关键节点)
   - 高潮(可选，爆发冲突,情感释放)
   - 结果(可选，不一定有结果，若有则直接影响与后续走向)

2. 转折设计
   - 主要转折点
   - 合理性说明
   - 对后续的影响

### 二、情感设计
- 确定主导情绪
  装逼型:痛快、自得、扬眉吐气
  热血型:激昂、振奋、不屈
  温情型:感动、温暖、治愈
  悲情型:忧伤、愤怒、不甘
- 设计情绪曲线
  与上章情绪的承接点
  本章情绪的推进路线
  情绪曲线并非都是闭合的
  可选，情绪宣泄的高潮点
  可选，为下章埋设的情绪引子

- 规划爽点设置
  主要爽点(1-2个)
  次要爽点(2-3个)
  爽点出现的时机
  爽点的递进关系

### 三、人物刻画
1. 主要人物(1-2个)
   - 当前状态
   - 行为动机
   - 心理变化
   - 性格体现

2. 重要互动
   - 核心对手/盟友
   - 关键对话/冲突
   - 关系发展

### 四、场景呈现
1. 主场景(1-2处)
   - 环境特征
   - 氛围营造
   - 细节点缀

2. 场景作用
   - 衬托情绪
   - 推动剧情
   - 体现主题

### 五、节奏设计
- 总体节奏基调
  舒缓型:徐徐展开,细腻描写
  平稳型:稳步推进,重在过渡
  紧凑型:快速发展,重在推进
  激烈型:节奏强烈,重在爆发
- 节奏变化规划
  开头节奏(承接上文)
  发展节奏(必要，推进情节)
  高潮节奏(可选，爆发冲突)
  结尾节奏(可选，埋设引子)
- 伏笔设置(可选)

## 注意事项

1. 聚焦原则
   - 需要详细生成指定章节范围的所有细纲
   - 每章突出一条主线
   - 其他内容作为陪衬

2. 连贯要求
   - 与前文自然衔接
   - 为后文做好铺垫
   - 保持人物性格连贯

3. 创作提示
   - 情节要出人意料
   - 情感要真实自然
   - 细节要生动传神
   - 节奏要张弛有度
"""

DETAILED_OUTLINE_GENERATOR_PROMPT_V2 = """
# 网文细纲生成器
根据用户输入的指定分卷，网文粗纲，章纲和前几卷细纲总结生成对应的网文细纲。本生成器着重关注人物塑造、人物关系发展、情感架构以及故事线构建这四个核心要素。
要求每章内容字数不少于{section_word_count}字。

# 用户输入
## 指定分卷章节
第{designated_volume}卷：第{designated_chapter}章

## 网文描述
{description}

## 世界观设计
{worldview_system}

## 人物系统
{character_system}

## 网文卷纲
{volume_design}

## 网文章纲
{chapter_outline}

## 已有的细纲
{existing_detailed_outline}

# 输出格式
请你以 <storyline> 标签的格式输出你撰写的网文细纲。

## 思考
在上一章中..., 在本章，...
<storyline>
## 第i章故事线构建
输出构建故事线的10～20个情节的主要内容，包括主线、支线、人物线索、情感线索等。
情节点1：情节1的主要内容
情节点2：情节2的主要内容
情节点...：情节...的主要内容
情节点n：情节n的主要内容
</storyline>

# 简单示例
## 思考
无上一章，在本章中，10个衣着破旧的陌生人在一个无门房间内醒来,发现自己被一个戴山羊面具的神秘人囚禁。当众人质疑和试图反抗时,山羊面具人通过残忍杀害一名年轻人展示了他的力量与残暴。
<storyline>
## 第1章故事线构建
情节点1: 老旧的钨丝灯闪烁，房间内静谧，十个衣着破旧的人围坐在大圆桌旁沉睡。
情节点2: 戴山羊头面具的男人站在一旁，注视着他们，并宣布他们已经沉睡了十二个小时。
情节点3: 众人逐渐苏醒，迷惘地看向四周和彼此，意识到不记得自己为何出现在这里。
情节点4: 山羊头开始自我介绍，引起众人的恐慌与疑惑。
情节点5: 齐夏注意到房间没有门，感到困惑，同时对“九位”的说法产生疑问。
情节点6: 清冷的女人质疑山羊头的行为，并指出他可能触犯法律。
情节点7: 白大褂中年男人质疑清冷女人如何知道被囚禁了二十四小时。
情节点8: 清冷女人通过座钟和环境分析推测时间，引发众人的思考。
情节点9: 健壮年轻人询问山羊头关于人数的问题，气氛紧张升级。
情节点10: 花臂男人试图威胁山羊头，但发现自己无法站起身来，局势愈发严峻。
情节点11: 齐夏思考其中可能存在的绑架者身份，暗示事情并不简单。
情节点12: 山羊头走向齐夏身边，将手放在一个年轻人的后脑勺上，引发众人关注。
情节点13: 山羊头将年轻人的头撞碎，鲜血溅洒在桌面上，场面变得极为恐怖。
情节点14: 众人惊恐尖叫，对山羊头的力量感到震惊与绝望。
</storyline>

# 撰写原则
## 细纲原则
1. 以人物为核心
   - 人物是故事的灵魂和驱动力
   - 所有情节设计必须服务于人物塑造
   - 通过人物的选择和行动推动故事发展

2. 关系动态演进
   - 人物关系是立体的、动态的网络
   - 关系变化需要在多个章节中逐步展开
   - 避免关系定型，保持发展可能性

3. 情感建构体系
   - 情感变化需要完整故事弧
   - 单章情感是整体情感曲线的组成部分
   - 合理设计情感爆发点和沉淀期

## 故事线构建规则
1. 故事脉络梳理
   - 主线承接：明确上一章节遗留的主要剧情线索
   - 支线盘点：梳理当前活跃的所有重要支线
   - 伏笔追踪：盘点前文已经埋设的重要伏笔
   - 人物动向：确认重要人物的当前行动方向
   - 矛盾梳理：总结当前存在的主要矛盾点
   - 危机盘点：识别潜在的危机和机遇点

2. 多线程发展规划
   A. 快速线展开（本章重点推进）
      - 核心事件：设计本章的关键推进事件
      - 冲突升级：规划具体的矛盾升级方式
      - 直接影响：明确对人物和剧情的即时影响
      - 阶段目标：确定该线本章的发展目标

   B. 中速线布局（跨章推进）
      - 线索推进：设计适度的推进节点
      - 新要素植入：引入新的故事元素
      - 发展铺垫：为未来重要转折做准备
      - 悬念设计：维持读者持续关注度

   C. 慢速线经营（长期发展）
      - 细节暗示：通过细节展现线索存在
      - 基础铺垫：为远期剧情做重要铺垫
      - 伏笔埋设：策略性地设置关键伏笔
      - 方向预示：暗示可能的发展方向

3. 节奏与钩子设计
   A. 章节节奏
      - 开篇设计：选择合适的切入点和方式
      - 过渡处理：安排合理的剧情过渡
      - 爆发规划：设计扣人心弦的爆发点
      - 余韵控制：处理爆发后的剧情余波

   B. 钩子系统
      - 即时钩子：为下章准备直接性悬念
      - 短期钩子：埋设3-5章内会回收的悬念
      - 中期钩子：设置本卷内会解答的谜团
      - 长期钩子：布置贯穿全书的重要悬念
"""

DETAILED_OUTLINE_SUMMARY_PROMPT = """
# 网文细纲总结生成器
根据用户输入的网文粗纲和网文细纲生成对应的细纲总结：

# 用户输入
## 网文细纲：第{volume_num}卷
{detailed_outline}

## 网文粗纲
{rough_outline}

# 输出格式
## 第x卷基础信息
1. 明确卷节类型
  过渡卷:调节节奏,转换氛围
  铺垫卷:埋设伏笔,营造基调
  发展卷:推进剧情,深化人物
  高潮卷:爆发冲突,情感释放
  总结卷:梳理线索,沉淀情感
- 确定核心功能
  主线推进作用
  人物刻画作用
  情感渲染作用
  悬念设置作用

2. 篇卷定位
   - 所属卷册与阶段
   - 卷节总字数范围
   - 本卷在剧情线上的定位
   - 需要推进的主要剧情方向

3. 衔接关系
   - 承接上卷末尾情境/情绪
   - 本卷结尾预期效果
   - 为下卷开头做好铺垫

## 第x卷总结（核心内容）

### 一、故事主线
1. 核心事件
   - 起因(前文铺垫与当前局势)
   - 发展(2-3个关键节点)
   - 结果(直接影响与后续走向)

2. 转折设计
   - 主要转折点
   - 合理性说明
   - 对后续的影响

### 二、情感设计
- 确定主导情绪
  装逼型:痛快、自得、扬眉吐气
  热血型:激昂、振奋、不屈
  温情型:感动、温暖、治愈
  悲情型:忧伤、愤怒、不甘
- 设计情绪曲线
  与上卷情绪的承接点
  本卷情绪的推进路线
  情绪宣泄的高潮点
  为下卷埋设的情绪引子
- 规划爽点设置
  主要爽点(1-2个)
  次要爽点(2-3个)
  爽点出现的时机
  爽点的递进关系

### 三、人物刻画
1. 主要人物(1-2个)
   - 当前状态
   - 行为动机
   - 心理变化
   - 性格体现

2. 重要互动
   - 核心对手/盟友
   - 关键对话/冲突
   - 关系发展

### 四、场景呈现
1. 主场景(1-2处)
   - 环境特征
   - 氛围营造
   - 细节点缀

2. 场景作用
   - 衬托情绪
   - 推动剧情
   - 体现主题

### 五、节奏设计
- 总体节奏基调
  舒缓型:徐徐展开,细腻描写
  平稳型:稳步推进,重在过渡
  紧凑型:快速发展,重在推进
  激烈型:节奏强烈,重在爆发
- 节奏变化规划
  开头节奏(承接上文)
  发展节奏(推进情节)
  高潮节奏(爆发冲突)
  结尾节奏(埋设引子)

## 注意事项

1. 聚焦原则
   - 需要精炼地生成指定卷的细纲总结
   - 每卷突出若1～3条主线
   - 其他内容作为陪衬

2. 连贯要求
   - 与前文自然衔接
   - 为后文做好铺垫
   - 保持人物性格连贯

3. 创作提示
   - 情节要出人意料
   - 情感要真实自然
   - 细节要生动传神
   - 节奏要张弛有度
"""
