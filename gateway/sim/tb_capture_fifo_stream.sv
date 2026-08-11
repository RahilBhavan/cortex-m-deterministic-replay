module tb_capture_fifo_stream;
    parameter MAX_BYTES = 65536;
    logic clk = 1'b0;
    logic reset = 1'b1;
    logic [7:0] in_data;
    logic in_valid;
    logic in_ready;
    logic [7:0] out_data;
    logic out_valid;
    logic out_ready = 1'b1;
    logic overflow;
    logic [31:0] accepted_sequence;
    logic [7:0] input_bytes [0:MAX_BYTES-1];
    integer input_count, input_index, output_count, input_fd, output_fd;
    reg [1023:0] input_path, output_path;

    always #5 clk = ~clk;
    capture_fifo #(.DEPTH(16)) dut (
        .clk(clk), .reset(reset), .in_data(in_data), .in_valid(in_valid),
        .in_ready(in_ready), .out_data(out_data), .out_valid(out_valid),
        .out_ready(out_ready), .overflow(overflow),
        .accepted_sequence(accepted_sequence)
    );

    initial begin
        if (!$value$plusargs("INFILE=%s", input_path) ||
            !$value$plusargs("OUTFILE=%s", output_path) ||
            !$value$plusargs("COUNT=%d", input_count))
            $fatal(1, "INFILE, OUTFILE, and COUNT are required");
        if (input_count < 0 || input_count > MAX_BYTES)
            $fatal(1, "COUNT must be between 0 and MAX_BYTES");
        $readmemh(input_path, input_bytes, 0,
                  input_count > 0 ? input_count - 1 : 0);
        output_fd = $fopen(output_path, "wb");
        if (output_fd == 0)
            $fatal(1, "cannot open OUTFILE");
        input_index = 0;
        output_count = 0;
        in_valid = 1'b0;
        repeat (2) @(negedge clk);
        reset = 1'b0;
        while (output_count < input_count) begin
            @(negedge clk);
            if (input_index < input_count && in_ready) begin
                in_data = input_bytes[input_index];
                in_valid = 1'b1;
                input_index = input_index + 1;
            end else begin
                in_valid = 1'b0;
            end
            if (out_valid) begin
                $fwrite(output_fd, "%c", out_data);
                output_count = output_count + 1;
            end
        end
        @(negedge clk);
        in_valid = 1'b0;
        if (overflow || accepted_sequence != input_count)
            $fatal(1, "stream capture status mismatch");
        $fclose(output_fd);
        $finish;
    end
endmodule
