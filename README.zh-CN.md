# AutoTA

[English](README.md) | **简体中文**

AutoTA 是一套可移植、以实际验收证据为依据的技术美术流程。它将美术需求
（设计文档中的视觉／音频需求）转化为经过许可核查或生成的资产，记录交付与验收结果，
再将引擎集成交给目标项目自身的工作流。它位于游戏制作流程的**中游**：上游设计文档
说明需要什么；AutoTA 负责寻找、生成、调整和检查资产；目标项目（例如 CCGS／Codex
游戏工作室配置）负责将资产集成到引擎并验证。

包含五项可移植的 Agent Skill：

- `search-game-art`：建立需求矩阵、覆盖不同来源的资源搜索、逐项许可核查和下载验收；
  支持从统一许可来源通过程序获取 CC0 资源，例如 Poly Haven API。
- `create-2d-game-art`：确定性的二维图像制作，包括像素化、序列处理、打包和检查，
  并输出具有严格字段约束的交付记录。
- `auto-ta`：Blender 端的三维技术美术，包括建模、调整、隔离检查、导出再导入验证及后续优化。
- `generate-hosted-game-art`：使用用户提供的 Meshy／腾讯混元凭据进行托管生成，
  包括免费能力探测、经预算授权的批量任务和生成记录。Tripo AI 通过独立的
  [Tripo 适配器](scripts/tripo-adapter.md)支持。
- `character-rig-animation-alignment`：将人形角色与外部动画对齐，进行重定向和引擎交付验收。

此外还包含共享交付／验收记录规范 `workflows/handoff-contract.md`、两个带命名空间的
Codex agent（`autota_technical_artist`、`autota_art_scout`），以及一个默认不启用的项目配置。

## 在制作流程中的位置

1. **上游（设计）**：游戏项目的设计文档说明视觉／音频需求，作为 AutoTA 的输入。
   用户也可直接通过文字描述或图像指定需要的资产。
2. **中游（AutoTA）**：寻找或生成资产，在 Blender 中调整、检查，并输出交付记录。
   必要验收项通过前，交付保持 `prototype`；记录本身不会将 `not_tested` 变成通过。
3. **下游（引擎）**：目标项目使用自己的工具导入资产、配置场景并进行引擎内验证。
   AutoTA 不会在未经授权时修改游戏项目的场景。

## 资产制作与资源获取

开始前与用户确定制作路线；如果用户已经指定，或授权自主决策，则无需重复询问。
综合比较预期效果、平台积分、agent token 消耗以及可能的返工成本。

| 路线 | 适合的情况 | 交接方式 |
| --- | --- | --- |
| 已有授权资源 | 有合适资产，调整成本低于重新制作 | 通过 `search-game-art` 核查风格、技术内容及许可后获取 |
| 直接在 Blender 中建模 | 简单几何组合、需要合理拆件和可编辑 UV，或包含精确文字与数字 | 本地制作后检查、导出 |
| Meshy／腾讯混元 | 根据需求选择托管生成 | 使用 `generate-hosted-game-art`，确认凭据与预算授权 |
| Tripo API | 需要 API 生成及任务追踪 | 使用 [Tripo 适配器](scripts/tripo-adapter.md)，再进行本地检查与集成 |
| Tripo Studio 网页版 | 使用 Studio 账户进行交互式生成 | 用户手动下载，或通过 Send to Blender／Studio Bridge 传输；本地收到后继续流程 |

寻找三维资源时，优先选择具有可用 PBR 材质信息、而非只有 Base Color 的资产。
核实实际贴图，并计入补齐缺失通道的成本。简化几何应符合项目风格；不要仅因资源免费
或面数低，就将卡通／几何风格资产用于不同的美术方向。

Tripo 默认使用 **P2 系列**，以当前可用型号及用户明确指定为准。网页版默认
**文字生成、Smart Mesh、四边形拓扑和 2K 贴图**。提交前核实实际控件与积分费用。
网页与 API 是两条独立路线：不擅自切换，也不假定积分通用。详见
[运行路线](skills/auto-ta/references/runtime-routing.md)。

API 适配器已实现余额检查、显式提交和任务查询；下载、解压及 Blender／Unity 的串联
由当前资产任务完成。平台的四边形、面数或 UV 参数不保证实际输出达标；API 的
`export_uv` 不等于已支持 Smart UV。网页版包含人工传输步骤，不是无人值守的端到端流程。

## 游戏资产规范与调整

部署后的第一次资产对话会询问用户规范；已经提供或保存的无需重复询问。
之后复用已接受的偏好，单个资产的明确要求优先。

以下均为可调整的默认值：

| 项目 | 默认规范 |
| --- | --- |
| 可编辑拓扑 | 仅三角面与四边面，不保留多于四边的面。需要形变的有机物优先四边形与适合形变的布线；刚性道具可合理混用，在有利于后期编辑的位置保留四边形 |
| 面数预算 | 小道具通常 300–1000 面，大道具约 2000 面；根据复杂度和画面重要性选择目标，容差 ±20%。另行报告引擎三角面数 |
| 贴图 | 默认 2048 × 2048，提供适当的 PBR 通道，并正确区分颜色与数据贴图 |
| UV 与扩色 | 排布便于理解，重叠符合用途，间距充足。将 UV 岛边缘像素向空白区域延伸，保留有效像素，并检查接缝和 mip 表现 |
| 修复投入 | 合格资产直接保留，小问题局部修复；重要、细节明显或缺陷严重且局部修复不经济时，考虑重构 |

四边形本身不保证形变良好，少量三角面也不构成重新拓扑的理由。
物理尺寸不是判断重要性的唯一依据。详见[资产规范](skills/auto-ta/references/asset-standards.md)。

可选的[重构脚本](skills/auto-ta/references/mesh-reconstruction.md)通过体素重构、QuadriFlow、
UV 展开和 PBR 重新烘焙，生成新的静态网格候选版本。它根据明确的 UV 覆盖遮罩，对四张
烘焙贴图的空白区域进行扩色。输入文件保持不变，重试次数受限；不适用于骨架、形态键
或透明源材质。重构结果仍需通过视觉、几何、UV、导出和引擎检查。

## Unity 交付

仅集成到用户授权的项目，并遵循该项目的渲染管线。优先复用明确用于存放模型的目录，
例如合适的 Art／Arts；只有符合项目既有约定时才使用 Resources。
否则使用 `Assets/AutoTA_Models`。

物件目录、模型和预制体使用 `category_Features` 命名，例如 `sofa_RedThreeSeat` 或
`clock_RedAlarm`。在 `Assets` 外保留一份共享批量导入脚本及各物件配置；如果 Unity
需要编译 Editor 脚本，则临时放入项目，确认结果已保存且验证通过后移除。
这是执行规范，并非仓库已经提供了通用 Unity 导入器。

默认不为每个模型保存专用验收场景。用户可以将资产拖入自己的场景；agent 可以使用
已授权的现有场景、Prefab Mode 或临时不保存的预览场景。未完成的视觉检查保持
`not_tested`。详见[Unity 资产组织规范](skills/auto-ta/references/unity-asset-layout.md)。

## 将工作目录链接到 Codex

链接脚本让 Codex 直接使用此仓库。修改 Skill 或自定义 agent 后，新启动的 Codex
任务会加载这些修改；安装过程不复制另一份文件。

所有平台均需要 Python 3.11+ 和 `uv`。`uv` 根据锁定的内联依赖运行 Skill；缺少它时，
doctor 会报错并停止。macOS 使用 iTerm2 作为终端模拟器，并在 `zsh` 或 `bash` 中运行
POSIX 脚本；iTerm2 本身不是 shell，macOS 不需要 PowerShell。Linux 使用相同 POSIX
流程。Windows 脚本需要 PowerShell 7+（`pwsh`），不支持 Windows PowerShell 5.1；
旧版本执行入口会在修改前退出。

macOS：在 iTerm2 中打开仓库，以 `zsh` 或 `bash` 执行：

~~~sh
./scripts/link.sh
./scripts/doctor.sh
~~~

Linux：在 POSIX shell 中执行相同命令：

~~~sh
./scripts/link.sh
./scripts/doctor.sh
~~~

Windows：在 PowerShell 7 中执行：

~~~powershell
pwsh -NoProfile -File .\scripts\link.ps1
pwsh -NoProfile -File .\scripts\doctor.ps1
~~~

可设置 `CODEX_HOME`，或将明确的 home 路径作为第一个参数。已有真实文件或目录不会被覆盖。
`-Force`（PowerShell）或 `--force`（POSIX）仅用于替换冲突的符号链接，仍不会替换非链接对象。

首次写入 `CODEX_HOME` 前，脚本会检查清单及准确的 Skill、agent、工作流和项目配置数量。
随后链接五项 Skill、两个带命名空间的 agent，以及完整产品根目录
`${CODEX_HOME}/workflow-products/autota`。Skill 从链接位置解析脚本及交付规范，因此可在
其他游戏项目的工作目录中使用。

脚本会将每个受管理目标、规范化源路径、类型及实际链接类型原子写入
`${CODEX_HOME}/state/autota/install-receipt.json`。记录绑定此仓库与 AutoTA 命名空间。
清单重命名或删除条目后，重新链接会清理记录所属的旧符号链接／junction；解除链接依照
记录执行，而非只看当前目录。损坏、属于其他仓库／命名空间或真实文件的目标会保留并报错。
`CODEX_HOME` 与此仓库不能相等，也不能互为父子目录，以免产品根目录链接递归。

解除链接仅删除能够证明仍指向此仓库、且属于安装记录的条目。macOS 在 iTerm2 的
`zsh`／`bash` 中执行，Linux 使用相同命令：

~~~sh
./scripts/unlink.sh
~~~

Windows 使用 PowerShell 7：

~~~powershell
pwsh -NoProfile -File .\scripts\unlink.ps1
~~~

修改链接的 Skill 或自定义 agent 配置后，请重启 Codex。Windows 的 Skill 目录使用 junction；
agent 文件优先使用符号链接，不具备权限时回退为同卷硬链接。Git 操作可能替换硬链接源文件，
因此切换或更新仓库后应运行 doctor。如果原文件标识已丢失，仅凭路径无法证明失效硬链接
的归属；doctor／link／unlink 会停止并保留文件以供人工检查，不保证自动清理这种回退链接。
需要重命名／删除后仍能自动清理时，请启用 Windows 开发者模式以使用 agent 符号链接。

Claude Code 仅集成 Skill：`scripts/link-claude-skills.sh`（POSIX／WSL）或
`scripts/link-claude-skills.ps1`（原生 Windows）将各 Skill 链接到 Claude Code 用户 Skill 目录。
Skill 可从任一运行环境的 home 解析随附脚本。

## 项目配置须明确选择

可移植核心不会自动选择项目配置。必须由目标仓库或用户明确指定：

- `dreamweaver`：项目工作区信息和历史重定向案例证据。

项目配置可以收窄路径和交付适配方式，但不能扩大用户授权，或降低验证、许可和工作区边界要求。

## 验证

可选重构脚本包含真实 Blender 测试，不调用生成平台：设置 `AUTOTA_TEST_BLENDER` 为
已安装的 Blender 可执行文件路径，然后运行
`python -m unittest discover -s tests -p 'test_reconstruction*.py' -v`。
不设置时会跳过 DCC 集成测试，但仍运行策略测试。

macOS 在 iTerm2 的 `zsh`／`bash` 中运行完整 POSIX 验证；Linux 使用相同命令：

~~~sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts -p test_tripo_client.py -v
python3 -m compileall -q skills scripts tests
sh -n scripts/link.sh scripts/unlink.sh scripts/doctor.sh
./scripts/doctor.sh --skip-link-check

codex_home="${CODEX_HOME:-$HOME/.codex}"
validator="$codex_home/skills/.system/skill-creator/scripts/quick_validate.py"
for skill_dir in skills/*; do
    [ -d "$skill_dir" ] || continue
    uv run --with pyyaml python "$validator" "$skill_dir"
done

git diff --check
~~~

以上 macOS 流程不调用也不需要 `pwsh`。Windows 在 PowerShell 7 中运行：

~~~powershell
$env:PYTHONUTF8 = '1'
python -m unittest discover -s tests -v
python -m unittest discover -s scripts -p test_tripo_client.py -v
python -m compileall -q skills scripts tests
pwsh -NoProfile -File .\scripts\doctor.ps1 -SkipLinkCheck
$codexHome = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    Join-Path $env:USERPROFILE '.codex'
} else {
    [System.IO.Path]::GetFullPath($env:CODEX_HOME)
}
$validator = Join-Path $codexHome 'skills\.system\skill-creator\scripts\quick_validate.py'
Get-ChildItem .\skills -Directory | ForEach-Object {
    uv run --with pyyaml python $validator $_.FullName
}
git diff --check
~~~

测试使用临时 Codex home，不会修改用户正在使用的 Codex 安装。

## 许可状态

原始检出内容、公开仓库元数据及最初的空远程仓库未能确定许可。
在所有者选定条款前，本仓库有意不提供 `LICENSE` 文件。
不要仅凭仓库公开可见就推断允许复制、再分发或发布。
