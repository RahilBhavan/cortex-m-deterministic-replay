module tb_capture_fifo;
    logic clk = 1'b0;
    logic reset = 1'b1;
    logic [7:0] in_data = 8'd0;
    logic in_valid = 1'b0;
    logic in_ready;
    logic [7:0] out_data;
    logic out_valid;
    logic out_ready = 1'b0;
    logic overflow;
    logic [31:0] accepted_sequence;
    logic [7:0] golden [0:4];
    integer golden_fd, bytes_read;
    reg [1023:0] input_path;

    always #5 clk = ~clk;

    capture_fifo #(.DEPTH(2)) dut (
        .clk(clk),
        .reset(reset),
        .in_data(in_data),
        .in_valid(in_valid),
        .in_ready(in_ready),
        .out_data(out_data),
        .out_valid(out_valid),
        .out_ready(out_ready),
        .overflow(overflow),
        .accepted_sequence(accepted_sequence)
    );

    task automatic drive_input(input logic [7:0] data);
        begin
            @(negedge clk);
            in_data = data;
            in_valid = 1'b1;
            if (!in_ready)
                $fatal(1, "input was not accepted: %h", data);
            @(negedge clk);
            in_valid = 1'b0;
        end
    endtask

    task automatic check_output(input logic [7:0] expected);
        begin
            @(negedge clk);
            if (!out_valid || out_data !== expected)
                $fatal(1, "expected output %h, got valid=%b data=%h", expected,
                       out_valid, out_data);
            out_ready = 1'b1;
            @(negedge clk);
            out_ready = 1'b0;
        end
    endtask

    initial begin
        if (!$value$plusargs("INFILE=%s", input_path))
            $fatal(1, "INFILE is required");
        golden_fd = $fopen(input_path, "rb");
        if (golden_fd == 0)
            $fatal(1, "cannot open INFILE");
        bytes_read = $fread(golden, golden_fd);
        $fclose(golden_fd);
        if (bytes_read < 5)
            $fatal(1, "INFILE must contain at least five bytes");

        repeat (2) @(negedge clk);
        reset = 1'b0;

        drive_input(golden[0]);
        drive_input(golden[1]);
        if (accepted_sequence !== 32'd2)
            $fatal(1, "sequence count mismatch after accepted inputs");

        @(negedge clk);
        in_data = golden[2];
        in_valid = 1'b1;
        if (in_ready)
            $fatal(1, "full FIFO did not apply backpressure");
        @(negedge clk);
        in_valid = 1'b0;
        if (!overflow)
            $fatal(1, "overflow did not become sticky after rejection");
        if (accepted_sequence !== 32'd2)
            $fatal(1, "rejected input changed sequence count");

        check_output(golden[0]);
        check_output(golden[1]);

        if (in_ready)
            $fatal(1, "overflowed FIFO accepted input before reset");
        @(negedge clk);
        reset = 1'b1;
        @(negedge clk);
        reset = 1'b0;

        drive_input(golden[3]);
        @(negedge clk);
        out_ready = 1'b1;
        in_data = golden[4];
        in_valid = 1'b1;
        if (!in_ready)
            $fatal(1, "simultaneous pop did not permit push");
        @(negedge clk);
        in_valid = 1'b0;
        out_ready = 1'b0;
        if (accepted_sequence !== 32'd2)
            $fatal(1, "sequence count mismatch after simultaneous pop/push");
        check_output(golden[4]);

        @(negedge clk);
        reset = 1'b1;
        @(negedge clk);
        reset = 1'b0;
        if (overflow || accepted_sequence !== 32'd0 || out_valid)
            $fatal(1, "reset did not deterministically clear FIFO state");

        $display("PASS");
        $finish;
    end
endmodule
