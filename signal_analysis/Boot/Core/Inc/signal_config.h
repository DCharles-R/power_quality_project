#ifndef INC_CONFIG_H_
#define INC_CONFIG_H_

#include <stdint.h>

// --- Configuración de Captura ---
#define HISTORY_BUFFER_CYCLES   12  // Tamaño del buffer de historial continuo (2 ciclos de margen)
#define TOTAL_CAPTURE_CYCLES    10  // Total de ciclos a enviar (2 pre + 8 post)
#define PRE_TRIGGER_CYCLES      2
#define POST_TRIGGER_CYCLES     (TOTAL_CAPTURE_CYCLES - PRE_TRIGGER_CYCLES) // = 8

#define SAMPLES_PER_CYCLE       512

// --- Tamaños de Buffer Derivados ---
// Tamaño del buffer de historial donde el DMA escribe en modo circular
#define ADC_BUFFER_LEN          (HISTORY_BUFFER_CYCLES * SAMPLES_PER_CYCLE) // 12 * 512 = 6144
// Tamaño del buffer de procesamiento y del payload final que se enviará
#define PROCESSING_BUFFER_LEN   (TOTAL_CAPTURE_CYCLES * SAMPLES_PER_CYCLE)  // 10 * 512 = 5120

// --- Constantes del Protocolo de Comunicación ---
#define PAYLOAD_LEN         (PROCESSING_BUFFER_LEN * sizeof(uint16_t)) // 5120 * 2 = 10240 bytes
#define PACKET_LEN          (2 + 2 + PAYLOAD_LEN + 2) // Header + Length + Payload + Checksum

#define UART_HEADER_BYTE_1 0xAA
#define UART_HEADER_BYTE_2 0x55

#endif /* INC_CONFIG_H_ */
