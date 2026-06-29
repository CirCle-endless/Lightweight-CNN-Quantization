`timescale 1ns / 1ps

module tb_Conv3x3_MAC();

    // 1. 定义测试信号 (连接到 MAC 的输入输出)
    reg signed [7:0] img_window [0:8];
    reg signed [7:0] weights [0:8];
    wire signed [19:0] conv_out;

    // 2. 例化刚才写的 MAC 核心算子 (Unit Under Test)
    Conv3x3_MAC uut (
        .p0(img_window[0]), .p1(img_window[1]), .p2(img_window[2]),
        .p3(img_window[3]), .p4(img_window[4]), .p5(img_window[5]),
        .p6(img_window[6]), .p7(img_window[7]), .p8(img_window[8]),
        .w0(weights[0]),    .w1(weights[1]),    .w2(weights[2]),
        .w3(weights[3]),    .w4(weights[4]),    .w5(weights[5]),
        .w6(weights[6]),    .w7(weights[7]),    .w8(weights[8]),
        .conv_out(conv_out)
    );

    // 3. 定义大容量 ROM，用于存放 Python 导出的十六进制数据
    reg [7:0] image_rom [0:783];
    reg [7:0] weight_rom [0:35]; 

    integer i;

    initial begin
        // 4. 将 .hex 文件读入 ROM
        // 【极度重要】仿真前，必须把这两个文件复制到 Quartus 工程根目录下！
        $readmemh("image_data.hex", image_rom);
        $readmemh("weight_data.hex", weight_rom);

        // 5. 初始化所有引脚为 0
        for (i = 0; i < 9; i = i + 1) begin
            img_window[i] = 8'd0;
            weights[i] = 8'd0;
        end

        #100; // 等待 100ns 系统稳定

        // 6. 载入卷积核权重 (读取前 9 个权重)
        for (i = 0; i < 9; i = i + 1) begin
            weights[i] = weight_rom[i];
        end

        // 7. 模拟喂入图像正中心的一个 3x3 窗口 (提取有数据区域)
        // MNIST 中心点大致在第 14 行，第 14 列 (一维索引 = 行*28 + 列)
        img_window[0] = image_rom[13*28 + 13];
        img_window[1] = image_rom[13*28 + 14];
        img_window[2] = image_rom[13*28 + 15];
        img_window[3] = image_rom[14*28 + 13];
        img_window[4] = image_rom[14*28 + 14];
        img_window[5] = image_rom[14*28 + 15];
        img_window[6] = image_rom[15*28 + 13];
        img_window[7] = image_rom[15*28 + 14];
        img_window[8] = image_rom[15*28 + 15];

        #50; // 等待 50ns，观察组合逻辑的计算结果

        // 8. 模拟滑窗移动，喂入旁边的一组新窗口
        img_window[0] = image_rom[15*28 + 15];
        img_window[1] = image_rom[15*28 + 16];
        img_window[2] = image_rom[15*28 + 17];
        img_window[3] = image_rom[16*28 + 15];
        img_window[4] = image_rom[16*28 + 16];
        img_window[5] = image_rom[16*28 + 17];
        img_window[6] = image_rom[17*28 + 15];
        img_window[7] = image_rom[17*28 + 16];
        img_window[8] = image_rom[17*28 + 17];

        #50;
        $stop; // 结束仿真
    end
endmodule