import torch
import numpy as np
from train_cnn import SimpleFPGA_CNN, train_model

def float_to_hex8(val, scale):
    """将浮点数量化为 8位 有符号整数 (INT8) 并转为 16进制补码格式"""
    q_val = int(np.round(val * scale))
    q_val = max(-128, min(127, q_val)) # 截断防止溢出
    return f"{q_val & 0xFF:02X}" # 0xFF 掩码处理负数补码

def export_to_hex_file(tensor_data, filename, scale):
    """将张量导出为 Verilog 可读文件"""
    flat_data = tensor_data.detach().cpu().numpy().flatten()
    with open(filename, 'w') as f:
        for val in flat_data:
            f.write(f"{float_to_hex8(val, scale)}\n")
    print(f"成功生成文件: {filename} (共 {len(flat_data)} 个数据)")

# 1. 重新加载刚才训练好的模型
model = SimpleFPGA_CNN()
model.load_state_dict(torch.load('fpga_cnn_weights.pth'))
model.eval()

# 2. 拿到测试集的第一张图片
_, test_loader = train_model() # 借用之前的函数加载数据
images, _ = next(iter(test_loader))
img_tensor = images[0]

# 3. 提取权重和图片进行量化导出
# 图片归一化前是 0-1，映射到 0-127
export_to_hex_file(img_tensor, "image_data.hex", scale=127.0)

# 权重最大绝对值映射到 127
weights = model.conv1.weight
max_w = torch.max(torch.abs(weights)).item()
scale_w = 127.0 / max_w
export_to_hex_file(weights, "weight_data.hex", scale=scale_w)
print(f"当前模型的权重缩放因子 scale_w 为: {scale_w}")
print("\n--- 软硬协同数据导出完成！ ---")