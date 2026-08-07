module async_fifo #(
    parameter int WIDTH = 8,
    parameter int ADDR_WIDTH = 4
) (
    input logic wclk, input logic wrst,
    input logic [WIDTH-1:0] wdata, input logic wvalid, output logic wready,
    input logic rclk, input logic rrst,
    output logic [WIDTH-1:0] rdata, output logic rvalid, input logic rready,
    output logic overflow, output logic [31:0] accepted_count
);
    localparam int DEPTH = 1 << ADDR_WIDTH;
    logic [WIDTH-1:0] mem [0:DEPTH-1];
    logic [ADDR_WIDTH:0] wbin, wgray, rbin, rgray;
    logic [ADDR_WIDTH:0] rgray_w1, rgray_w2, wgray_r1, wgray_r2;
    logic wfull;
    logic wpush, rpop;

    function automatic [ADDR_WIDTH:0] bin2gray(input [ADDR_WIDTH:0] b);
        bin2gray = (b >> 1) ^ b;
    endfunction
    function automatic [ADDR_WIDTH:0] next_bin(input [ADDR_WIDTH:0] b);
        next_bin = b + 1'b1;
    endfunction
    assign wpush = wvalid && wready;
    assign wready = !wfull;
    assign rvalid = (rgray != wgray_r2);
    assign rdata = mem[rbin[ADDR_WIDTH-1:0]];
    assign rpop = rvalid && rready;

    always_ff @(posedge wclk) begin
        if (wrst) begin
            wbin <= '0; wgray <= '0; rgray_w1 <= '0; rgray_w2 <= '0;
            wfull <= 1'b0; overflow <= 1'b0; accepted_count <= 32'd0;
        end else begin
            rgray_w1 <= rgray; rgray_w2 <= rgray_w1;
            if (wvalid && !wready) overflow <= 1'b1;
            if (wpush) begin
                mem[wbin[ADDR_WIDTH-1:0]] <= wdata;
                wbin <= next_bin(wbin); wgray <= bin2gray(next_bin(wbin));
                accepted_count <= accepted_count + 1'b1;
            end
            wfull <= (bin2gray(next_bin(wbin)) == {~rgray_w2[ADDR_WIDTH:ADDR_WIDTH-1], rgray_w2[ADDR_WIDTH-2:0]});
        end
    end

    always_ff @(posedge rclk) begin
        if (rrst) begin
            rbin <= '0; rgray <= '0; wgray_r1 <= '0; wgray_r2 <= '0;
        end else begin
            wgray_r1 <= wgray; wgray_r2 <= wgray_r1;
            if (rpop) begin
                rbin <= next_bin(rbin); rgray <= bin2gray(next_bin(rbin));
            end
        end
    end
endmodule
