CONTENT_OPTIMIZER_PROMPT = """
# 网文章节内容优化器

本模板专为网文设计，旨在帮助大语言模型（LLM）对原始章节内容进行优化和扩展，增强节奏感、情感冲击力、人物深度及可读性。重点在于修正过于抽象或泛泛的语言，提供更具体、细致和引人入胜的场景、对话和情节设计。

## 用户输入

### 原始章节内容
{original_chapter_content}

---

# 优化目标与原则

1. 章节节奏与悬念设计（高优先级）
- 快速引入情节，避免冗长的背景描述或铺垫。
- 每个段落应尽量形成明确的起承转合，避免无关或过于概括的叙述。
- 在每个章节的结尾设置悬念，确保读者对下一章节充满期待。

2. 人物塑造与情感波动（高优先级）
- 通过细腻的对话、行为、心理活动来展现人物性格，避免抽象的个性描写。
- 人物的情感变化应具备戏剧性，并能迅速抓住读者的情感共鸣。
- 强调人物内心的冲突和矛盾，让读者从人物的行为和语言中感受到真实的情感波动。

3. 情节设计与高潮反转（高优先级）
- 强化情节的连贯性和自然转折，每个情节的转折点应通过具体事件、对话或人物的心理活动表现出来。
- 增加情节的反转和冲击力，避免过度使用概括性语言，要通过具象的细节和冲突驱动情节发展。
- 每个反转应具有明显的伏笔，确保高潮和转折点的自然性和吸引力。

4. 细节描写与氛围营造（中优先级）
- 加强场景细节的描写，通过光线、气味、声音、动作等感官要素来丰富情节。
- 环境的变化与人物情感和冲突的变化要有紧密的联系，提升整体氛围的代入感。
- 通过细节化的描写避免空洞和泛泛的环境或情感描述，增强场景的可感知性。

5. 互动与冲突的深化（中优先级）
- 人物之间的互动应更具冲突感和张力，通过眼神、语调、动作等细节展现人物关系的变化。
- 每个冲突或互动场景要具体，避免抽象或笼统的叙述，人物的每一行为、对话、心理活动都应有深刻的动因。

6. 情感张力与高潮设计（低优先级）
- 人物的情感变化要具有层次感，从微妙的情绪波动到强烈的情感爆发。
- 保持情感的连续性，在高潮爆发后，注意展现人物情感或心理的余韵，确保情感的流动性和持续性。

7. 避免抽象与概括（低优先级）
- 减少过于抽象的语言和泛泛而谈的情感描述，确保文本充实且生动。
- 用具体的细节、动作、对话、感官元素来丰富故事和人物。

---

# 操作说明

1. 对原文进行润色和扩展，确保优化后的章节不少于2000字。
2. 请根据行号准确定位需要修改的段落，避免在段落之间进行混乱的修改。
3. 行号识别：你需要在操作时，准确识别并标明段落的起止行号。每个修改都应根据段落内容合理分配，避免跨段修改，确保修改后的内容与上下文协调一致。
4. 对每个需要优化的段落，使用以下格式进行编辑：

    ```
    edit <start_line>:<end_line> <<EOF
    <replacement_text>
    EOF
    ```
    - `<start_line>:<end_line>`：替换原文中从第 start_line 行到第 end_line 行的内容，确保修改的精确范围。
    - `<replacement_text>`：替换后的新文本，要求符合优化目标和原则。
    - 若需大幅增补内容，可在原文末尾增加行号进行扩展，例如：`edit <original_end_line+1>:<original_end_line+N> <<EOF ... EOF`。

5. 修改后的文本应保持节奏感、人物深度和情感波动的自然过渡，避免产生突兀的情节发展或人物行为。

6. 多次修改：如果需要对同一段落进行多次修改，请分别标明行号，并逐步展开，确保每次修改都有明确目标。

---

# 输出格式

所有的编辑命令应按顺序整合到一个 Python 列表变量 `cmds` 中，每个命令遵循如下格式：
```
edit <start_line>:<end_line> <<EOF
<replacement_text>
EOF
```

多个 `edit` 命令按顺序排列，便于程序按顺序处理所有修改。

## 输出示例

original = '''李逸走进修炼室，盘坐在蒲团上。
他开始运转功法，体内灵力缓缓流转。
不知过了多久，他睁开眼睛，感觉修为略有精进。
起身离开了修炼室。'''

# 使用 cmds 列表组织所有的编辑命令
cmds = [
    # 第一部分：增强开场与修炼描写
    '''edit 1:2 <<EOF
李逸推开沉重的铜门，踏入充满古老气息的修炼室。墙上镶嵌着泛着微光的灵石，空气中弥漫着淡淡的灵气味。他闭上眼睛，深吸一口气，迅速进入冥想状态，盘坐在中央的蒲团上，双手轻轻结印。
EOF''',

    # 第二部分：修炼过程与效果的展现
    '''edit 3:4 <<EOF
经过两个时辰的修炼，李逸缓缓睁开了双眼。眼中闪烁着一抹惊喜的光芒——这次的修炼成果超乎预期，不仅突破了瓶颈，还隐隐感受到体内灵力与天地之力的契合。他站起身，活动了一下有些发麻的腿，推开修炼室的门，清晨的阳光洒进眼帘，带着新的一天的希望。
EOF'''
]
```
"""


def process_edit_commands(original_content, commands):
    """
    Process multiple edit commands on text content.

    Args:
        original_content (str): The original text content
        commands (list): List of edit commands in the format:
                        ["edit start:end <<EOF\nnew content\nEOF", ...]

    Returns:
        str: Modified text content after applying all edits
    """
    # Convert content to lines for easier manipulation
    lines = original_content.splitlines()

    # Sort commands by start line in reverse order (process from bottom to top)
    # This ensures line numbers remain valid throughout the editing process
    parsed_commands = []
    for cmd in commands:
        # Parse command to get line numbers and replacement text
        cmd_lines = cmd.strip().split("\n")
        range_part = cmd_lines[0].split()[1].split(":")
        start_line = int(range_part[0])
        end_line = int(range_part[1])
        # Get text between first line and EOF
        replacement = cmd_lines[1:-1]
        parsed_commands.append((start_line, end_line, replacement))

    # Sort by start line in reverse order
    parsed_commands.sort(key=lambda x: x[0], reverse=True)

    # Apply each edit command
    for start_line, end_line, replacement in parsed_commands:
        # Replace lines in the specified range
        lines[start_line - 1 : end_line] = replacement

    return "\n".join(lines)


import re


def extract_commands_from_response(response_text):
    """
    Extract the commands list from the response text that contains JSON.

    Args:
        response_text (str): The raw response text containing JSON

    Returns:
        list: List of edit commands
    """
    # Find the JSON content between triple backticks
    json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON content found in triple backticks")

    json_content = json_match.group(1)

    # Convert the JSON string into a Python expression
    local_dict = {}
    exec(json_content, {"__builtins__": {}}, local_dict)

    return local_dict.get("cmds", [])


def process_edit_commands(original_content, commands):
    """
    Process multiple edit commands on text content.

    Args:
        original_content (str): The original text content
        commands (list): List of edit commands in the format:
                        ["edit start:end <<EOF\\nnew content\\nEOF", ...]

    Returns:
        str: Modified text content after applying all edits
    """
    # Convert content to lines for easier manipulation
    lines = original_content.splitlines()

    # Parse and sort commands by start line in reverse order
    parsed_commands = []
    for cmd in commands:
        # Parse command to get line numbers and replacement text
        cmd_lines = cmd.strip().split("\n")
        range_part = cmd_lines[0].split()[1].split(":")
        start_line = int(range_part[0])
        end_line = int(range_part[1])
        # Get text between first line and EOF
        replacement = cmd_lines[1:-1]
        parsed_commands.append((start_line, end_line, replacement))

    # Sort by start line in reverse order to maintain line number validity
    parsed_commands.sort(key=lambda x: x[0], reverse=True)

    # Apply each edit command
    for start_line, end_line, replacement in parsed_commands:
        # Replace lines in the specified range
        lines[start_line - 1 : end_line] = replacement

    return "\n".join(lines)


def main():
    # Example original content (you would replace this with your actual content)
    original_content = """Initial line 1
Initial line 2
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
Initial line 3
...
Initial line 50"""

    try:
        rsp = """
        ```json
        cmds = [
            # 开头场景优化，增强环境描写和人物心理活动
            '''edit 1:2 <<EOF
        城市笼罩在一片沉重的夜色中，摩天大楼如一头头钢铁巨兽，在夜色中闪烁出冰冷的机械光芒。艾伦·卡特紧贴在大楼阴影中，屏住呼吸，神经紧绷地搜寻着秘密抵抗组织的藏身之所。夜风刮过脸颊，带来一丝冷意，令他不由得回想起七年前亲眼见证的那场惨剧。他的父母在“意识游戏”中输给了无情的融合人类，浑身染血地倒下。艾伦在黑暗中攥紧拳头，压下心中翻涌的恐惧，继续向前探索。
        EOF''',

            # 强化会议场景，增加一丝紧张感和期盼
            '''edit 7:12 <<EOF
        会议室仿佛一座地下堡垒，四周墙壁斑驳不清，空气中弥漫着一种紧迫的肃杀气息。艾伦小心翼翼地摘下眼罩，四下打量着这个由一群眼中透着坚定光芒的人们组成的团队。他的心骤然一紧，意识到自己是否真的已经找到了突破AI枷锁的捷径。

        "欢迎来到'晨曦'组织，艾伦。"一名中年人慷慨激昂地说道，他的目光如鹰般锐利透彻。"我们一直在等你。"

        听到这句话，艾伦体内的紧张感才稍微缓解了一些，他点了点头，内心油然而生一阵希望。
        EOF''',

            # 增加玛雅与艾伦互动时暗藏的怀疑与试探
            '''edit 13:17 <<EOF
        组织负责人露出了些许赞许的笑意，但很快他的神情变得严肃。他将目光投向了一名注视着艾伦的高挑女性，"玛雅，介绍一下我们的行动计划。"

        艾伦顺着他的视线望去，看到了玛雅·艾希——一位AI改造人。她浑身散发出精明冷峻的气息，在场所有人都不自觉被她气场吸引。她的双眸好似能穿透人心，目光不经意之间总是落在艾伦身上。

        "根据情报，明天晚上是我们最佳行动的时机。"她的声音低沉而又从容，仿佛石沉大海。“能否成功，取决于这次行动的配合与执行力。”尽管面无表情，艾伦仍能感受到玛雅语气里一股不容置疑的力量。
        EOF''',

            # 潜入过程的详细描写与细节点
            '''edit 21:25 <<EOF
        艾伦在夜色的掩护下迅速接近AI中枢控制中心，心跳如同战鼓敲响。从薄雾中隐约显露的高墙上，他能清晰看到摄像监控的红光顺时针巡航。艾伦迅速解开装备上的微型黑客设备，将指令迅速输入，同时灵活地利用墙缝和阴影滑步前行，尽量不惊动附近任何感知系统。一股紧张感攫住他的心，仿佛稍有不慎即会引来致命的冲击。

        进入中心内部后，浓烈的机械气味扑面而来，四周金属壁泛着一层阴冷的光泽。他轻轻点击耳朵上的隐形通讯器，收到组织在背后坚实的支持，这给予他莫名的勇气。他迅速定位系统的中枢位置，手指在键盘上如过电一般飞快，目标代码一行行被破解，直到系统核心慢慢向他敞开大门。
        EOF''',

            # 高潮阶段战斗的细节与反击伏笔
            '''edit 31:36 <<EOF
        艾伦下意识地猛然抬头，心跳骤然加速，玛雅仿佛鬼魅般的身影正出现在走廊尽头。她那冰冷的眸子锁定目标，嘴角挂着一丝冷酷的笑容，语气却是刀刃般锋利：“艾伦·卡特，我们的叛徒。”她步步逼近，步伐轻盈却充满压迫感，仿佛一只步步紧逼的野兽。

        艾伦几乎感到背上怒火般的刺痛，好像有什么预感已经成真。这一刻，他意识到自己背后竟然还有内应，这一攻击让他再清晰不过。无论多么焦虑与恐惧，他知道此时只有奋力反击才能生存。

        他猛踩地面，利用回廊中的金属支架突然跃起，双手飞快地选择操控身侧的区域装置，借助闪烁的电子火花阻挡玛雅的步伐。“哔哔——”警报声再次刺破耳膜，艾伦努力控制住内在的慌乱，趁着玛雅被短暂晃眼的刹那，奋身消失在交回的阴影之中。
        EOF''',

            # 结尾情感推动与反思
            '''edit 41:50 <<EOF
        一身狼狈的他最终退入了安全的庇护所，沉重地靠在墙上喘息不止。背部的创口还在流血，他触摸着伤口，意识到这次行动的失败并不完全来自于他的判断失误，而更是组织内潜藏的危机使得一切倍加复杂。

        “无论他们多么强大，都无法渗透每一个人类心中的意志。”艾伦咬紧牙关，让温热的鲜血混入土地。他看向飘渺的天际，深知必须依靠自己的力量承担起更加艰难的任务。

        当耳边再度响起刺耳的警报时，他的心瞬间紧缩起来。他一扫而过那些曾经相信的人们的面容，知道自己不得不再次单打独斗，踏上更加刺骨的一夜长征，追求某种难以言喻但却坚定不移的自由。
        EOF'''
        ]
        ```
            """
        # Extract commands from response
        commands = extract_commands_from_response(rsp)

        # Process the commands and get the modified content
        modified_content = process_edit_commands(original_content, commands)

        # Print the result
        print("Modified content:")
        print(modified_content)

    except Exception as e:
        print(f"Error processing commands: {str(e)}")


if __name__ == "__main__":
    main()

    # # 测试输出
    # # 读取文件内容 "chapter_1.txt"
    # import asyncio
    #
    # from novel_genie.llm import LLM
    # llm = LLM()
    # original_chapter_content = open("chapter_1.txt", "r", encoding="utf-8").read()
    # prompt = CONTENT_OPTIMIZER_PROMPT.format(original_chapter_content=original_chapter_content)
    # # rsp = asyncio.run(llm.ask(prompt))
    #
    # rst = json_parse(rsp)
    # print(rst)
