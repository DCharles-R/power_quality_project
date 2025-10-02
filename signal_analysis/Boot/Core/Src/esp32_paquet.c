// --- Coloca esto en la sección USER CODE BEGIN 0 o en un archivo .c separado ---

#include <string.h> // Necesitarás esto para memcpy
#include "signal_config.h"
#include "esp32_paquet.h"

// Crea un buffer estático para el paquete. 'static' evita que se cree en el stack.
static uint8_t tx_packet_buffer[PACKET_LEN];

/**
  * @brief Calcula un checksum simple de 16 bits (Fletcher-16 modificado).
  * @param data Puntero a los datos.
  * @param length Número de bytes de los datos.
  * @retval El checksum de 16 bits calculado.
  */
uint16_t calculate_checksum(const uint8_t* data, uint16_t length)
{
    uint16_t sum1 = 0;
    uint16_t sum2 = 0;
    for (uint16_t i = 0; i < length; ++i) {
        sum1 = (sum1 + data[i]) % 255;
        sum2 = (sum2 + sum1) % 255;
    }
    return (sum2 << 8) | sum1;
}

//uint16_t calculate_checksum(const uint8_t* data, uint16_t length) {
//    uint16_t checksum = 0;
//    for (uint16_t i = 0; i < length; i++) {
//        checksum += data[i];
//    }
//    return checksum;
//}

/**
  * @brief Construye y envía un paquete de datos al ESP32 por UART.
  * @param huart Puntero a la estructura del UART.
  * @param buffer Puntero al buffer de datos (ej. processing_buffer).
  * @param num_samples El número de muestras en el buffer (ej. ADC_BUFFER_LEN).
  */
HAL_StatusTypeDef send_buffer_to_esp32(UART_HandleTypeDef *huart, uint16_t* buffer, uint16_t num_samples)
{
    uint16_t payload_length = num_samples * sizeof(uint16_t); // 5120 * 2 = 10240 bytes
    uint16_t checksum = calculate_checksum((const uint8_t*)buffer, payload_length);
    uint16_t current_pos = 0;

    // --- 1. Ensamblar el paquete completo en un solo buffer ---

    // Header (2 bytes)
    tx_packet_buffer[current_pos++] = UART_HEADER_BYTE_1;
    tx_packet_buffer[current_pos++] = UART_HEADER_BYTE_2;

    // Length (2 bytes) - little-endian
    tx_packet_buffer[current_pos++] = (uint8_t)(payload_length & 0xFF);
    tx_packet_buffer[current_pos++] = (uint8_t)(payload_length >> 8);

    // Payload (10240 bytes) - Usamos memcpy para máxima velocidad
    memcpy(&tx_packet_buffer[current_pos], buffer, payload_length);
    current_pos += payload_length;

    // Checksum (2 bytes) - little-endian
    tx_packet_buffer[current_pos++] = (uint8_t)(checksum & 0xFF);
    tx_packet_buffer[current_pos++] = (uint8_t)(checksum >> 8);

    // --- 2. Enviar el paquete completo con UN SOLO llamado al DMA ---
    return HAL_UART_Transmit_DMA(huart, tx_packet_buffer, PACKET_LEN);
}
