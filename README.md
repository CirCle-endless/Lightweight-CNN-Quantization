# Lightweight-CNN-Quantization
基于 PyTorch 与 Verilog 的轻量级 CNN 前向传播与 INT8 有符号量化算法复现与算子级仿真验证。

# 轻量级CNN前向传播与INT8量化算法复现 (Lightweight-CNN-Quantization)

本仓库是《人工智能》课程期末专业核心课设的配套开源项目。项目完整复现了经典的卷积神经网络（CNN）前向传播算法与 INT8 对称线性量化算法，并通过 Verilog 硬件描述语言实现了底层的算子级仿真验证，实现了“软硬协同”的逻辑闭环。

## 📁 目录结构与规范

项目严格遵循工业界开源硬件与算法仓库的目录规范，剥离了 EDA 工具生成的本地临时文件，仅保留核心源码与指令流数据：

```text
Lightweight-CNN-Quantization/
│
├── README.md                      # 项目说明文档
│
├── software/                      # 软件算法端（Python/PyTorch）
│   ├── train_cnn.py                   # CNN 模型训练、前向传播与特征矩阵可视化脚本
│   ├── export_hex.py              # INT8 对称最大值量化与 Hex 指令流导出脚本
│   └── fpga_cnn_weights.pth       # 训练收敛后导出的浮点模型权重文件
│
├── hardware/                      # 硬件验证端（Verilog RTL）
│   ├── rtl/
│   │   └── Conv3x3_MAC.v          # 核心硬件算子：9路并行有符号乘法器与加法树组合逻辑
│   └── tb/
│       └── tb_Conv3x3_MAC.v       # 仿真激励文件：负责读取外部Hex数据流并驱动时钟
│
└── data/                          # 软硬协同测试数据集（纯十六进制补码格式）
    ├── image_data.hex             # 由 Python 量化导出并重排的输入图像定点特征流
    └── weight_data.hex            # 由 Python 量化导出并重排的 3x3 卷积核定点权重流
```

## 🚀 快速复现指南

### 1. 软件端模型训练与数据量化
* **环境依赖**：`Python 3.9+`, `PyTorch`, `NumPy`
* **执行命令**：
  打开终端，依次运行以下脚本完成模型收敛并刷新底层数据集：
  ```bash
  python software/train_cnn.py
  python software/export_hex.py
  ```
* **软硬件对标基准**：
  脚本运行后，会在终端打印出当前权重的最大绝对值量化缩放因子 `scale_w`（本组实验真实运行值为 `99.4555`）。结合图像量化因子 `127.0`，可推导系统定点化后的总乘加放大系数约为 `12630.85`。同时，脚本会打印出图像中心区域（`12:17`）的浮点特征作为软件端黄金参考（Golden Reference）。

### 2. 硬件端算子级仿真验证
* **验证环境**：`ModelSim` / `Intel Quartus Prime`
* **复现步骤**：
  1. 在仿真软件中新建工程，导入 `hardware/rtl/Conv3x3_MAC.v` 和 `hardware/tb/tb_Conv3x3_MAC.v`。
  2. 将 `data/` 目录下重新生成的 `image_data.hex` 与 `weight_data.hex` 复制到仿真软件的工作根目录下（确保 Testbench 能够通过 `$readmemh` 相对路径正确加载）。
  3. 编译并运行仿真（执行 `run -all` 或仿真至 `150ns` 以上）。
* **算子完备性检查**：
  在仿真轴推进至 `150ns` 时，利用波形探测抓取乘法阵列内部的有符号中间变量（`mult_res0` 至 `mult_res8`）。可以观测到硬件完美支持了有符号补码运算，例如正负相乘（`127 × -34 = -4318`）与正正相乘（`102 × 63 = 6426`）。加法树执行级联累加后，输出端口 `conv_out` 精确吐出十进制有符号整数 `11634`。经总放大系数去量化反推，硬件幅值趋势与软件高度自洽，算子内部的数学逻辑与边界条件得到完备性验证。

## 📝 开发与技术声明
1. **工具链管理规范**：本仓库依据集成电路版本控制规范，垃圾文件（如 Quartus 的 `.db`、`.incremental_db` 以及 ModelSim 的 `work` 缓存）已列入 `.gitignore`，确保交付源码的纯净度。
2. **开发路径**：本项目软硬件协同框架统筹、Verilog 硬件算子编写、数据接口定义以及最终 ModelSim 流水线时序的 Debug 验证工作均由作者独立实践推进。

---
*本项目仅作为高校课程期末教学设计及开源学术交流使用，严禁用于任何商业目的。*
