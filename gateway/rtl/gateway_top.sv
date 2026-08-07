module gateway_top (
    input  logic clk,
    input  logic reset,
    input  logic [3:0] nibble_rise,
    input  logic [3:0] nibble_fall,
    input  logic nibble_valid,
    input  logic host_ready,
    output logic [7:0] host_data,
    output logic host_valid,
    output logic overflow,
    output logic [31:0] accepted_count
);
    capture_gate gate (
        .capture_clk(clk), .capture_reset(reset),
        .nibble_rise(nibble_rise), .nibble_fall(nibble_fall),
        .nibble_valid(nibble_valid), .host_clk(clk), .host_reset(reset),
        .host_ready(host_ready), .host_data(host_data), .host_valid(host_valid),
        .overflow(overflow), .accepted_count(accepted_count)
    );
endmodule
