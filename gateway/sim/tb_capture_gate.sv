module tb_capture_gate;
    parameter MAX_BYTES = 65536;
    parameter ADDR_WIDTH = 1;
    logic cclk = 0, hclk = 0, crst = 1, hrst = 1, valid = 0, ready = 0;
    logic [3:0] rise = 0, fall = 0;
    logic [7:0] data;
    logic out_valid, overflow;
    logic [31:0] accepted;
    logic [7:0] input_bytes [0:MAX_BYTES-1];
    integer input_count, input_fd, bytes_read, output_index, accepted_at_overflow;
    reg [1023:0] input_path;
    logic checking = 0;

    always #3 cclk = ~cclk;
    always #2 hclk = ~hclk;

    capture_gate #(.ADDR_WIDTH(ADDR_WIDTH)) dut (
        cclk, crst, rise, fall, valid, hclk, hrst, ready,
        data, out_valid, overflow, accepted
    );

    always @(posedge hclk) begin
        if (checking && out_valid && ready) begin
            if (data !== input_bytes[output_index])
                $fatal(1, "golden order mismatch got=%h expected=%h index=%0d",
                       data, input_bytes[output_index], output_index);
            output_index = output_index + 1;
        end
    end

    task automatic send(input logic [7:0] value);
        begin
            @(negedge cclk); rise = value[3:0]; valid = 1;
            @(negedge cclk); valid = 0;
            @(negedge cclk); fall = value[7:4]; valid = 1;
            @(negedge cclk); valid = 0;
            @(negedge cclk);
        end
    endtask

    task automatic release_resets;
        begin
            @(negedge cclk); crst = 0; hrst = 0;
            repeat (4) @(negedge cclk);
            repeat (4) @(negedge hclk);
        end
    endtask

    integer i;
    initial begin
        if (!$value$plusargs("INFILE=%s", input_path) ||
            !$value$plusargs("COUNT=%d", input_count))
            $fatal(1, "INFILE and COUNT are required");
        if (input_count <= 0 || input_count > MAX_BYTES)
            $fatal(1, "COUNT must be between 1 and MAX_BYTES");
        input_fd = $fopen(input_path, "rb");
        if (input_fd == 0)
            $fatal(1, "cannot open INFILE");
        bytes_read = $fread(input_bytes, input_fd);
        $fclose(input_fd);
        if (bytes_read < input_count)
            $fatal(1, "INFILE shorter than COUNT");

        release_resets();
        output_index = 0;
        checking = 1;
        ready = 1;
        for (i = 0; i < input_count; i = i + 1)
            send(input_bytes[i]);
        wait (output_index == input_count);
        repeat (2) @(posedge cclk);
        if (overflow || accepted !== input_count)
            $fatal(1, "golden capture status mismatch accepted=%0d", accepted);

        checking = 0;
        ready = 0;
        hrst = 1;
        repeat (3) @(posedge cclk);
        repeat (3) @(posedge hclk);
        if (overflow || accepted !== 0 || out_valid)
            $fatal(1, "coordinated reset did not flush state");
        release_resets();

        for (i = 0; i < 8; i = i + 1)
            send(input_bytes[i % input_count]);
        repeat (6) @(posedge cclk);
        if (!overflow)
            $fatal(1, "overflow not sticky");
        accepted_at_overflow = accepted;
        send(input_bytes[0]);
        send(input_bytes[1 % input_count]);
        repeat (4) @(posedge cclk);
        if (accepted !== accepted_at_overflow)
            $fatal(1, "overflow changed accepted count");

        crst = 1;
        repeat (3) @(posedge cclk);
        crst = 0;
        repeat (4) @(posedge cclk);
        repeat (4) @(posedge hclk);
        if (overflow || accepted !== 0 || out_valid)
            $fatal(1, "reset recovery failed");

        rise = input_bytes[0][3:0];
        valid = 1;
        @(negedge cclk);
        valid = 0;
        crst = 1;
        @(negedge cclk);
        crst = 0;
        repeat (4) @(negedge cclk);
        repeat (4) @(negedge hclk);
        output_index = 0;
        checking = 1;
        ready = 1;
        send(input_bytes[0]);
        wait (output_index == 1);
        if (accepted !== 1)
            $fatal(1, "half-byte reset produced a phantom byte");

        $display("PASS");
        $finish;
    end
endmodule
