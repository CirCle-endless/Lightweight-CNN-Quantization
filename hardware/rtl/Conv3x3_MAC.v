`timescale 1ns / 1ps

// =========================================================
// 模块名称: Conv3x3_MAC
// 功能描述: 纯组合逻辑的 3x3 卷积乘累加器 (面向 AI 边缘加速)
// 特性: 接收 9个 INT8 像素和 9个 INT8 权重，并行计算出一个特征点
// =========================================================
module Conv3x3_MAC (
    // 9个 8-bit 有符号像素输入 (对应 3x3 感受野)
    input signed [7:0] p0, p1, p2, 
    input signed [7:0] p3, p4, p5, 
    input signed [7:0] p6, p7, p8,
    
    // 9个 8-bit 有符号权重输入
    input signed [7:0] w0, w1, w2, 
    input signed [7:0] w3, w4, w5, 
    input signed [7:0] w6, w7, w8,
    
    // 卷积累加输出 
    // (8bit * 8bit = 16bit, 9个16bit相加，需要扩展到 20bit 防止溢出)
    output signed [19:0] conv_out 
);

    // 1. 定义 9 个 16-bit 乘积中间变量
    wire signed [15:0] mult_res0, mult_res1, mult_res2;
    wire signed [15:0] mult_res3, mult_res4, mult_res5;
    wire signed [15:0] mult_res6, mult_res7, mult_res8;

    // 2. 并行执行 9 次乘法 (在 FPGA 中会综合成专用的 DSP 模块)
    assign mult_res0 = p0 * w0;
    assign mult_res1 = p1 * w1;
    assign mult_res2 = p2 * w2;
    assign mult_res3 = p3 * w3;
    assign mult_res4 = p4 * w4;
    assign mult_res5 = p5 * w5;
    assign mult_res6 = p6 * w6;
    assign mult_res7 = p7 * w7;
    assign mult_res8 = p8 * w8;

    // 3. 加法树 (Adder Tree) 将所有乘积累加
    // 注意：这里为了代码简洁直接相加，真实高速设计中会插入寄存器做流水线(Pipeline)
    assign conv_out = mult_res0 + mult_res1 + mult_res2 + 
                      mult_res3 + mult_res4 + mult_res5 + 
                      mult_res6 + mult_res7 + mult_res8;

endmodule