module ddr_capture (
    input logic clk, input logic reset,
    input logic [3:0] nibble_rise, input logic [3:0] nibble_fall,
    input logic valid,
    output logic [7:0] byte_data, output logic byte_valid, input logic byte_ready,
    output logic overflow
);
    logic have_rise;
    logic [3:0] rise_data;
    always_ff @(posedge clk) begin
        if (reset) begin
            have_rise <= 1'b0; rise_data <= '0; byte_data <= '0;
            byte_valid <= 1'b0; overflow <= 1'b0;
        end else begin
            if (byte_valid && byte_ready) byte_valid <= 1'b0;
            if (!overflow && valid && !have_rise) begin
                rise_data <= nibble_rise; have_rise <= 1'b1;
            end else if (!overflow && valid && have_rise) begin
                if (!byte_valid || byte_ready) begin
                    byte_data <= {nibble_fall, rise_data};
                    byte_valid <= 1'b1; have_rise <= 1'b0;
                end else begin
                    overflow <= 1'b1; have_rise <= 1'b0;
                end
            end
        end
    end
endmodule
