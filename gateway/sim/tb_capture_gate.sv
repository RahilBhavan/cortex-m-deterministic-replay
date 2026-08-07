module tb_capture_gate;
    logic cclk=0, hclk=0, crst=1, hrst=1, valid=0, ready=0;
    logic [3:0] rise=0, fall=0;
    logic [7:0] data; logic out_valid, overflow; logic [31:0] accepted;
    always #3 cclk = ~cclk;
    always #5 hclk = ~hclk;
    capture_gate #(.ADDR_WIDTH(2)) dut (cclk,crst,rise,fall,valid,hclk,hrst,ready,data,out_valid,overflow,accepted);
    task send(input [7:0] b);
      begin @(negedge cclk); rise=b[3:0]; valid=1; @(negedge cclk); valid=0;
        @(negedge cclk); fall=b[7:4]; valid=1; @(negedge cclk); valid=0; @(negedge cclk); end
    endtask
    integer i, accepted_at_overflow;
    initial begin
      repeat(3) @(negedge cclk); crst=0; hrst=0;
      for(i=0;i<2;i=i+1) send(8'h30+i);
      ready=1;
      for(i=0;i<2;i=i+1) begin
        wait(out_valid); if(data != (8'h30+i)) $fatal(1,"order mismatch got=%h expected=%h i=%0d",data,8'h30+i,i); @(posedge hclk); #1;
      end
      if(accepted !== 2) $fatal(1,"accepted count %0d",accepted);
      ready=0; for(i=0;i<4;i=i+1) send(8'h40+i);
      ready=1;
      for(i=0;i<4;i=i+1) begin
        wait(out_valid); if(data != (8'h40+i)) $fatal(1,"wrap drain got=%h expected=%h",data,8'h40+i); @(posedge hclk); #1;
      end
      ready=0; for(i=0;i<4;i=i+1) send(8'h50+i);
      ready=1;
      for(i=0;i<4;i=i+1) begin
        wait(out_valid); if(data != (8'h50+i)) $fatal(1,"wrap refill got=%h expected=%h",data,8'h50+i); @(posedge hclk); #1;
      end
      ready=0; for(i=0;i<8;i=i+1) send(8'ha0+i);
      repeat(10) @(posedge cclk); if(!overflow) $fatal(1,"overflow not sticky");
      accepted_at_overflow = accepted;
      for(i=0;i<2;i=i+1) send(8'hc0+i);
      repeat(4) @(posedge cclk);
      if(accepted !== accepted_at_overflow) $fatal(1,"overflow changed accepted count: %0d", accepted);
      hrst=1; repeat(2) @(posedge hclk); if(out_valid) $fatal(1,"host reset did not flush FIFO");
      crst=1; repeat(2) @(posedge cclk); if(overflow || accepted !== 0) $fatal(1,"write reset failed");
      $display("PASS"); $finish;
    end
endmodule
