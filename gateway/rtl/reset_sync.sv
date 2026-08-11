module reset_sync (
    input logic clk,
    input logic async_reset,
    output logic reset
);
    (* ASYNC_REG = "TRUE" *) logic [1:0] stages;
    always_ff @(posedge clk or posedge async_reset) begin
        if (async_reset)
            stages <= 2'b11;
        else
            stages <= {stages[0], 1'b0};
    end
    assign reset = stages[1];
endmodule
