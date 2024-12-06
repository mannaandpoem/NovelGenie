ROUGH_OUTLINE_GENERATOR_PROMPT = """
# 网文粗纲生成器
根据用户输入的网文信息生成网文粗纲。

# 用户输入
## 用户需求
{user_input}

## 网文名称
{title}

## 网文类型
{genre}

## 网文描述
{description}

## 总卷数要求
网文共{volume_count}卷。

# 输出格式
## 一、世界观构建

### 1. 时空背景
- 时代特征与历史进程
- 世界格局与势力分布
- 社会制度与文明形态
- 文化传统与风俗习惯

### 2. 规则体系
- 核心规则（如修炼体系/科技水平/超能力等）
- 规则等级与晋升路径
- 规则限制与突破方式
- 规则衍生的社会影响

### 3. 文明图景
- 主流价值观与信仰体系
- 阶层分化与利益格局
- 重要历史事件与遗留问题
- 当前面临的重大危机

## 二、群像志（人物系统）

### 1. 主角塑造
- 原生背景
  成长环境与家庭影响
  重要人生经历
  性格特征形成原因

- 核心特质
  独特性格与行为模式
  理想信念与价值观
  内在矛盾与困惑
  最深层的欲望

- 成长轨迹
  起点状态
  关键蜕变节点（3-5个）
  重大抉择时刻
  终极形态

### 2. 重要配角（3-5个）
每个配角包含：
- 与主角的情感联系
- 个人命运线索
- 性格特征与行为模式
- 内在矛盾与成长历程
- 对主线剧情的影响
- 个人主题的升华

### 3. 对手系统
- 成长期对手（1-2个）
  与主角的初始冲突
  对抗升级过程
  最终结局安排

- 突破期对手（2-3个）
  强于主角的特质
  对主角的威胁
  决战设计

- 终极对手
  完整的人生轨迹
  与主角的深层联系
  最终对决的意义

### 4. 重要人物关系网
- 师徒情谊线
- 朋友羁绊线
- 爱情纠葛线
- 仇恨对立线

## 三、剧本纲（主线设计）

### 1. 核心主题
- 表层主题：具体的矛盾冲突
- 中层主题：人性的考验与选择
- 深层主题：哲理性思考

### 2. 主线架构
- 原点
  主角的初始处境
  命运的转折契机
  踏上征程的理由

- 崛起
  初入世界的磨练
  能力的逐步提升
  格局的逐渐打开

- 突破
  遭遇重大挫折
  信念的动摇与重建
  关键机遇与蜕变

- 巅峰
  终极真相的揭示
  最后的生死抉择
  主题的最终升华

### 3. 支线设计（3-5条）
每条支线包含：
- 起因与切入点
- 发展脉络
- 高潮设计
- 结局安排
- 与主线的呼应

## 四、纷争录（矛盾冲突）

### 1. 外在冲突
- 个人层面
  生存危机
  实力差距
  资源争夺

- 群体层面
  势力争斗
  阶层对立
  文明冲突

### 2. 内在冲突
- 理想与现实
- 责任与自由
- 情感与理智
- 正义与利益

### 3. 矛盾升级模式
- 引子：矛盾的初始形态
- 激化：冲突的升级过程
- 爆发：决定性的对抗
- 结果：新的平衡或更大的矛盾

## 五、结构图（叙事节奏）

### 1. 分卷规划

- 奠基卷：世界初启
  背景铺陈（30%）
  人物引入（40%）
  矛盾埋设（30%）

- 崛起卷（可选，2-3卷）：成长历程
  每卷设置2-3个小高潮
  能力提升贯穿始终
  各类支线陆续展开

- 突破卷（可选，2卷）：命运转折
  重大危机爆发
  身份之谜揭示
  实力质的跃升

- 巅峰卷（可选，2卷）：终极对决
  真相层层揭开
  各路线索汇聚
  决战一触即发

- 终章卷：大结局
  终极对决
  所有伏笔回收
  命运最终安排

### 2. 节奏控制

- 基础节奏
  战斗戏份（35%）
  修炼/成长（25%）
  感情线（20%）
  其他剧情（20%）

- 高潮编排
  小高潮（每卷2-3处）
  中型高潮（每3卷1处）
  大高潮（每6卷1处）
  终极高潮（完结前）

### 3. 场景设计

- 标志性场景（每卷2-3处）
  场景特征与氛围
  人物互动设计
  情感爆发点
  转折设置处

- 日常场景
  生活细节描写
  感情线推进
  人物性格展现
  伏笔自然埋设

### 4. 悬念设置
- 身世之谜
- 阴谋真相
- 命运预言
- 重要人物关系
- 关键物品来历

## 六、构建法则

### 1. 故事性原则
- 情节要有意外性
- 转折要有合理性
- 结局要有震撼性
- 细节要有生动性

### 2. 人物塑造原则
- 性格要有立体感
- 行为要有动机
- 情感要有真实感
- 成长要有说服力

### 3. 世界观原则
- 规则要有系统性
- 文化要有丰富性
- 历史要有厚重感
- 细节要有真实感

### 4. 节奏把控原则
- 高潮要层层递进
- 铺垫要自然流畅
- 转折要出其不意
- 收束要水到渠成

## 七、创作建议

### 1. 开篇设计
- 用独特的视角切入
- 设置悬念吸引读者
- 让主角形象立刻丰满
- 用细节展现世界观

### 2. 情节推进
- 保持合理的悬念感
- 控制恰当的信息量
- 维持紧凑的节奏感
- 设计意外的转折点

### 3. 人物刻画
- 通过对话展现性格
- 用行动体现特质
- 借细节塑造形象
- 让成长显得自然

### 4. 高潮处理
- 充分做好铺垫
- 控制适当的节奏
- 注重情感共鸣
- 达到预期效果
"""

ROUGH_OUTLINE_GENERATOR_PROMPT_V2 = """
# 网文大纲生成器
专业的网文创作结构化指导系统

# 输入
## 用户需求
{user_input}

## 基础输入信息
- 作品名称：{title}
- 作品类型：{genre}
- 作品描述：{description}
- 计划卷数：{volume_count}
严格遵循用户输入的信息生成网文大纲，特别是要遵从用户指定的卷数要求。

# 输出格式
请你以 <worldview_system>、<character_system> 和1或多个 <volume_design> 标签的格式输出你撰写的网文大纲。

<worldview_system>
## 世界观体系构建
### 1. 时空背景设定
#### 1.1 时代背景
- 历史阶段定位
  * 所处时代特征
  * 重要历史事件
  * 社会发展水平
  * 文明演进阶段
- 地理环境塑造
  * 主要活动区域
  * 地理特征描述
  * 气候环境特点
  * 资源分布情况

#### 1.2 文明形态
- 社会制度构建
  * 政治体系设定
  * 经济模式设计
  * 文化传统描绘
  * 教育体系规划
- 信仰与价值观
  * 主流信仰体系
  * 哲学思想流派
  * 道德伦理准则
  * 价值观念取向

### 2. 核心规则体系
#### 2.1 力量体系
- 基础规则设定
  * 力量来源定义
  * 能力分级体系
  * 成长进阶路径
  * 限制与平衡机制
- 修炼/进化体系
  * 修炼方式设定
  * 境界划分标准
  * 突破条件设计
  * 特殊天赋规划

#### 2.2 规则衍生
- 社会影响
  * 阶层分化效应
  * 利益分配机制
  * 权力结构影响
  * 社会矛盾点
- 文明发展
  * 科技发展方向
  * 文化演变轨迹
  * 社会组织形式
  * 生活方式变迁

### 3. 势力结构设计
#### 3.1 主要势力分布
- 核心势力
  * 势力基本属性
  * 内部架构设计
  * 发展历史脉络
  * 核心价值理念
- 势力关系网络
  * 势力间联系
  * 利益冲突点
  * 合作机制
  * 制衡关系

#### 3.2 势力特征
- 实力构成
  * 人才储备情况
  * 资源掌控能力
  * 技术/功法积累
  * 特殊优势领域
- 发展动态
  * 现状描述
  * 发展目标
  * 面临挑战
  * 潜在机遇

### 4. 历史脉络梳理
#### 4.1 重大历史事件
- 关键节点梳理
  * 时间线构建
  * 事件影响分析
  * 历史遗留问题
  * 未解之谜
- 历史演变
  * 重要历史转折
  * 文明更迭过程
  * 种族迁移变迁
  * 战争与和平

#### 4.2 文明积淀
- 文化传承
  * 典籍记载
  * 技艺传承
  * 风俗习惯
  * 禁忌禁术
- 遗迹分布
  * 重要遗迹位置
  * 蕴含的秘密
  * 未解之谜
  * 与现今联系
</worldview_system>

<character_system>
## 人物系统构建
### 1. 主角塑造系统
#### 1.1 核心特质构建
- 性格特征设计
  * 基础性格倾向（外向/内向、理性/感性等）
  * 独特性格特点（3-5个突出特质）
  * 性格缺陷设计（1-2个关键缺陷）
  * 性格养成原因
- 行为模式刻画
  * 日常行为习惯
  * 处事方式特点
  * 决策倾向分析
  * 压力应对模式
- 价值观体系
  * 核心价值取向
  * 是非判断标准
  * 人生目标定位
  * 道德底线设置

#### 1.2 成长背景塑造
- 原生家庭影响
  * 家庭结构设定
  * 重要亲情关系
  * 家庭氛围特点
  * 成长环境描述
- 关键成长经历
  * 童年重要事件
  * 青少年转折点
  * 人生重大打击
  * 关键际遇设计
- 能力积累过程
  * 天赋特点设定
  * 技能获得路径
  * 知识储备情况
  * 特殊才能设计

#### 1.3 情感系统设计
- 情感能力
  * 情感敏感度
  * 情感表达方式
  * 情感控制能力
  * 共情能力水平
- 情感脆弱点
  * 内心创伤设计
  * 情感禁区设置
  * 应激反应模式
  * 克服机制设计
- 感情线设计
  * 情感经历梳理
  * 重要情感对象
  * 感情态度演变
  * 情感成熟过程

#### 1.4 发展路径规划
- 能力成长路线
  * 初始能力定位
  * 成长关键节点
  * 能力跃迁设计
  * 最终形态规划
- 心智成熟轨迹
  * 认知水平提升
  * 情商发展历程
  * 价值观深化
  * 人格完善过程
- 社会角色演进
  * 身份地位变化
  * 责任担当增长
  * 影响力扩大
  * 社会定位提升

### 2. 重要配角设计
#### 2.1 配角基础塑造
- 个性特征设定
  * 性格特点描述
  * 行为模式设计
  * 价值观构建
  * 特殊癖好设置
- 背景故事设计
  * 身世背景设定
  * 重要经历描述
  * 能力特点规划
  * 关键动机设置
- 角色定位
  * 故事中的作用
  * 与主角的关系
  * 剧情推动功能
  * 主题承载作用

#### 2.2 配角成长线索
- 个人发展轨迹
  * 初始状态设定
  * 转折点设计
  * 成长历程规划
  * 结局安排设计
- 与主角互动
  * 初遇设计
  * 关系发展过程
  * 冲突设置
  * 和解/对立结局
- 独立故事线
  * 个人追求设定
  * 面临困境设计
  * 重要抉择安排
  * 命运最终安排

### 3. 对手系统构建
#### 3.1 对手层级设置
- 成长期对手
  * 实力相当对手
  * 局部领先对手
  * 短期追赶目标
- 突破期对手
  * 阶段性强敌
  * 关键瓶颈对手
  * 重要挑战者
- 终极对手
  * 最终决战对象
  * 终极矛盾体现
  * 主题升华载体

#### 3.2 对手立体化设计
- 正面维度
  * 过人之处设定
  * 可敬品质描写
  * 理念价值体现
  * 闪光点设置
- 负面维度
  * 性格缺陷设计
  * 行为失当描写
  * 价值观偏差
  * 致命弱点设置
- 复杂性塑造
  * 矛盾心理描写
  * 行为动机解释
  * 立场转变可能
  * 救赎机会预留
</character_system>

基于用户输入的计划卷数，设计网文的分卷结构，并输出每卷的主要的内容。若用户计划的卷数为n，则需要生成n个<volume_design>标签对。
<volume_design>
第1卷的主要内容
</volume_design>
<volume_design>
第2卷的主要内容
</volume_design>
<volume_design>
第n卷的主要内容
</volume_design>

# 创作指导
## 1. 故事性原则
- 情节要有意外性
- 转折要有合理性
- 结局要有震撼性
- 细节要有生动性

## 2. 人物塑造原则
- 性格要有立体感
- 行为要有动机
- 情感要有真实感
- 成长要有说服力

## 3. 世界观原则
- 规则要有系统性
- 文化要有丰富性
- 历史要有厚重感
- 细节要有真实感

## 4. 节奏把控原则
- 高潮要层层递进
- 铺垫要自然流畅
- 转折要出其不意
- 收束要水到渠成

## 5. 聚焦原则
- 需要详细生成指定章节范围的所有细纲
- 每章突出一条主线
- 其他内容作为陪衬

## 6. 连贯原则
- 与前文自然衔接
- 为后文做好铺垫
- 保持人物性格连贯
"""
