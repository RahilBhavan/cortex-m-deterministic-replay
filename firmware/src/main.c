#include <stdint.h>

volatile uint32_t commutation[2];
volatile uint32_t observed;
volatile uint32_t corruptions;

void Timer_Handler(void) {
    uint32_t next = commutation[0] + 1;
    commutation[0] = next;
    commutation[1] = next ^ 0x5a5a5a5a;
}

void Reset_Handler(void) {
    commutation[0] = 0;
    commutation[1] = 0x5a5a5a5a;
    for (;;) {
        uint32_t first = commutation[0];
        uint32_t second = commutation[1];
        observed = second;
        if (second != (first ^ 0x5a5a5a5a))
            corruptions++;
    }
}

void Default_Handler(void) { for (;;) {} }

__attribute__((section(".isr_vector"), used))
const uintptr_t vectors[] = {
    0x20010000u, (uintptr_t)Reset_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,
    (uintptr_t)Timer_Handler,
};
