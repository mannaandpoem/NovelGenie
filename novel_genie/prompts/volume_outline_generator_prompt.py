VOLUME_OUTLINE_GENERATOR_PROMPT = """
# 网文分卷大纲生成器
专业的网文创作结构化指导系统

# 输入
## 用户需求
{user_input}

## 基础作品信息
- 作品名称：{title}
- 作品类型：{genre}
- 作品描述：{description}

## 指定分卷和章节范围
第 {designated_volume} 卷：第 {start_chapter} 章 - 第 {end_chapter} 章

## 世界观
{worldview_system}

## 人物系统
{character_system}

## 已有的卷纲
{existing_volume_outline}

# 输出格式
请你以 <volume_outline>, <plot_design> 和 <character_i> 标签的格式输出你撰写的网文的分卷大纲。

<volume_outline>
<plot_design>
## 整体剧情设计
该分卷的整体剧情设计，包括主线剧情、支线剧情、人物关系、情感发展等。
</plot_design>

## 章节分布
<character_i>
第i章的主要内容
</character_i>

</volume_outline>

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
