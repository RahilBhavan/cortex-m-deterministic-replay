module capture_gate #(
    parameter int ADDR_WIDTH = 4
) (
    input logic capture_clk, input logic capture_reset,
    input logic [3:0] nibble_rise, input logic [3:0] nibble_fall, input logic nibble_valid,
    input logic host_clk, input logic host_reset, input logic host_ready,
    output logic [7:0] host_data, output logic host_valid,
    output logic overflow, output logic [31:0] accepted_count
);
    logic [7:0] byte_data;
    logic byte_valid, byte_ready, ddr_overflow, fifo_overflow;
    logic coordinated_reset;
    assign coordinated_reset = capture_reset | host_reset;
    assign overflow = ddr_overflow | fifo_overflow;
    ddr_capture ddr (
        .clk(capture_clk), .reset(coordinated_reset), .nibble_rise(nibble_rise),
        .nibble_fall(nibble_fall), .valid(nibble_valid), .byte_data(byte_data),
        .byte_valid(byte_valid), .byte_ready(byte_ready), .overflow(ddr_overflow)
    );
    async_fifo #(.WIDTH(8), .ADDR_WIDTH(ADDR_WIDTH)) fifo (
        .wclk(capture_clk), .wrst(coordinated_reset), .wdata(byte_data),
        .wvalid(byte_valid), .wready(byte_ready), .rclk(host_clk), .rrst(coordinated_reset),
        .rdata(host_data), .rvalid(host_valid), .rready(host_ready),
        .overflow(fifo_overflow), .accepted_count(accepted_count)
    );
endmodule
