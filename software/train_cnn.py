import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# === 新加的这两行：解决 Windows 下 SSL 证书报错的问题 ===
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# ==========================================
# 第一步：搭建硬件友好的极简 CNN
# ==========================================
class SimpleFPGA_CNN(nn.Module):
    def __init__(self):
        super(SimpleFPGA_CNN, self).__init__()
        # 核心算子：3x3 卷积，单通道输入，4通道输出
        # 【注意】bias=False 是为了大幅简化底层的硬件加法逻辑
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=4, kernel_size=3, stride=1, padding=1, bias=False)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        # 全连接层：分类输出 0-9
        self.fc = nn.Linear(4 * 14 * 14, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1) # 展平操作
        x = self.fc(x)
        return x

# ==========================================
# 第二步：加载数据集并进行训练
# ==========================================
def train_model():
    # 数据预处理：转换为 Tensor 并归一化
    transform = transforms.Compose([transforms.ToTensor()])
    
    # 自动下载并加载 MNIST 数据集
    train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False) # 测试时 batch 设为 1 方便提取单张图片

    model = SimpleFPGA_CNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print("开始训练网络...")
    epochs = 3 # 因为网络极简，跑 3 到 5 轮准确率就足够高了
    for epoch in range(epochs):
        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
        print(f"Epoch {epoch+1}/{epochs} 完成，Loss: {loss.item():.4f}")

    # 保存训练好的模型权重
    torch.save(model.state_dict(), 'fpga_cnn_weights.pth')
    print("模型权重已保存至 fpga_cnn_weights.pth")
    return model, test_loader

# ==========================================
# 第三步：提取第一层输出作为“硬件仿真标准答案”
# ==========================================
def extract_golden_reference(model, test_loader):
    model.eval()
    with torch.no_grad():
        # 从测试集中抽第一张图片
        images, labels = next(iter(test_loader))
        img = images[0:1] # 获取第一张图片的张量

        # 核心：只让图片通过第一层卷积（不走后续的 ReLU 和全连接）
        conv_out = model.conv1(img)

        print("\n--- 提取硬件仿真对标数据 ---")
        print(f"目标数字标签: {labels[0].item()}")
        print(f"输入图像 Tensor 尺寸: {img.shape}  -> 对应 ModelSim 里的图片 ROM")
        print(f"第一层卷积结果尺寸: {conv_out.shape} -> 对应 ModelSim 里的输出 RAM")
        
        # 打印部分数据，用于后期核对波形
        print("\n第一张特征图(Channel 0)中心 5x5 矩阵结果:")
        print(np_format(conv_out[0, 0, 12:17, 12:17].numpy()))

def np_format(arr):
    # 格式化打印辅助函数，保留四位小数
    import numpy as np
    return np.array2string(arr, formatter={'float_kind':lambda x: "%.4f" % x})

if __name__ == "__main__":
    trained_model, loader = train_model()
    extract_golden_reference(trained_model, loader)