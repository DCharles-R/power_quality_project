#ifndef INC_ESP32_PAQUET_H_
#define INC_ESP32_PAQUET_H_

#include "main.h" // Necesario para acceder a tipos como HAL_StatusTypeDef y UART_HandleTypeDef

// --- Prototipo de la Función ---
// Esta es la "declaración" que otros archivos necesitan conocer.
HAL_StatusTypeDef send_buffer_to_esp32(UART_HandleTypeDef *huart, uint16_t* buffer, uint16_t num_samples);

// Aquí también puedes declarar la función del checksum si la quieres usar en otro lado
uint16_t calculate_checksum(const uint8_t* data, uint16_t length);

#endif /* INC_ESP32_PAQUET_H_ */
