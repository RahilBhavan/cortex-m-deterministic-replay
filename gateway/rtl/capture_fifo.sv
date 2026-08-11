module capture_fifo #(
    parameter int DEPTH = 16
) (
    input  logic        clk,
    input  logic        reset,
    input  logic [7:0]  in_data,
    input  logic        in_valid,
    output logic        in_ready,
    output logic [7:0]  out_data,
    output logic        out_valid,
    input  logic        out_ready,
    output logic        overflow,
    output logic [31:0] accepted_sequence
);
    logic [7:0] mem [0:DEPTH-1];
    integer write_ptr;
    integer read_ptr;
    integer count;
    logic push;
    logic pop;

    assign out_valid = (count != 0);
    assign out_data = mem[read_ptr];
    assign pop = out_valid && out_ready;
    assign in_ready = ((count < DEPTH) || pop) && !overflow;
    assign push = in_valid && in_ready;

    always_ff @(posedge clk) begin
        if (reset) begin
            write_ptr <= 0;
            read_ptr <= 0;
            count <= 0;
            overflow <= 1'b0;
            accepted_sequence <= 32'd0;
        end else begin
            if (in_valid && !in_ready)
                overflow <= 1'b1;

            if (push) begin
                mem[write_ptr] <= in_data;
                if (write_ptr == DEPTH - 1)
                    write_ptr <= 0;
                else
                    write_ptr <= write_ptr + 1;
                accepted_sequence <= accepted_sequence + 1'b1;
            end

            if (pop) begin
                if (read_ptr == DEPTH - 1)
                    read_ptr <= 0;
                else
                    read_ptr <= read_ptr + 1;
            end

            case ({push, pop})
                2'b10: count <= count + 1;
                2'b01: count <= count - 1;
                default: count <= count;
            endcase
        end
    end
endmodule
