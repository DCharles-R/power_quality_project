#include <Arduino.h>
#include <WiFi.h>
#include <InfluxDbClient.h> // <-- La librería correcta de Tobias Schürg para v2
#include "config.h"
#include <time.h>

// --- Cliente InfluxDB ---
// Se configura con todos los parámetros de v2
InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN);

// --- Parámetros del Protocolo UART y Buffers (SIN CAMBIOS) ---
#define UART_HEADER_BYTE_1 0xAA
#define UART_HEADER_BYTE_2 0x55
#define TOTAL_CAPTURE_SAMPLES 5120
#define PAYLOAD_LENGTH (TOTAL_CAPTURE_SAMPLES * 2)
#define BATCH_SIZE 100 // Número de puntos a enviar en cada lote. Puedes ajustar este valor.

// Variables globales de tiempo
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = -21600; // CST es UTC-6
const int   daylightOffset_sec = 3600;

// Buffer para recibir los datos
uint16_t adc_samples[TOTAL_CAPTURE_SAMPLES];
uint8_t* payload_buffer = (uint8_t*)adc_samples;

// Estados para la máquina de recepción
enum RxState {
  WAITING_FOR_HEADER_1,
  WAITING_FOR_HEADER_2,
  READING_LENGTH_1,
  READING_LENGTH_2,
  READING_PAYLOAD,
  READING_CHECKSUM_1,
  READING_CHECKSUM_2
};

RxState currentState = WAITING_FOR_HEADER_1;
uint16_t payload_index = 0;
uint16_t received_length = 0;
uint16_t received_checksum = 0;

// --- Prototipos de Funciones ---
uint16_t calculate_checksum(const uint8_t* data, uint16_t length);
void sendToInfluxDB_v2(uint16_t* buffer, uint16_t num_samples);

// =================================================================
// FUNCIÓN SETUP
// =================================================================
void setup() {
  Serial.begin(115200);
  
  // Conexión Wi-Fi (sin cambios)
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando a Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado!");

  // SINCRONIZAR LA HORA
  Serial.println("Sincronizando hora con servidor NTP...");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.println("Esperando sincronización de hora...");
    delay(1000);
  }
  Serial.println("¡Hora sincronizada correctamente!");
  Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");

  // UART para comunicación con STM32 (sin cambios)
  Serial2.begin(115200, SERIAL_8N1, 26, 25);
  Serial2.setRxBufferSize(16384);

  // Verificamos la conexión con la base de datos
  if (client.validateConnection()) {
    Serial.print("Conexión a InfluxDB v2 exitosa. Bucket: ");
    Serial.println(client.getServerUrl());
  } else {
    Serial.print("Error de conexión con InfluxDB v2: ");
    Serial.println(client.getLastErrorMessage());
  }

  Serial.println("ESP32 Receptor listo (usando InfluxDB v2).");
}

// =================================================================
// FUNCIÓN LOOP (SIN CAMBIOS, EXCEPTO LA LLAMADA FINAL)
// =================================================================
void loop() {
  // Procesamos en un bucle 'while' para vaciar el buffer de hardware lo más rápido posible
  while (Serial2.available() > 0) {
    uint8_t incoming_byte = Serial2.read();

    switch (currentState) {
      case WAITING_FOR_HEADER_1:
        if (incoming_byte == UART_HEADER_BYTE_1) {
          currentState = WAITING_FOR_HEADER_2;
        }
        break;

      case WAITING_FOR_HEADER_2:
        if (incoming_byte == UART_HEADER_BYTE_2) {
          currentState = READING_LENGTH_1;
        } else {
          currentState = WAITING_FOR_HEADER_1;
        }
        break;

      case READING_LENGTH_1:
        received_length = incoming_byte;
        currentState = READING_LENGTH_2;
        break;
        
      case READING_LENGTH_2:
        received_length |= (incoming_byte << 8);
        if (received_length == PAYLOAD_LENGTH) {
            payload_index = 0;
            currentState = READING_PAYLOAD;
            // -- Mensaje de depuración eficiente --
            Serial.printf("Header y longitud OK. Leyendo %u bytes de payload...\n", received_length);
        } else {
            Serial.println("Error: Longitud de paquete incorrecta. Reiniciando...");
            currentState = WAITING_FOR_HEADER_1;
        }
        break;

      case READING_PAYLOAD:
        payload_buffer[payload_index++] = incoming_byte;
        if (payload_index >= received_length) {
          currentState = READING_CHECKSUM_1;
          // -- Mensaje de depuración eficiente --
          Serial.println("Lectura de payload completada. Verificando checksum...");
        }
        break;

      case READING_CHECKSUM_1:
        received_checksum = incoming_byte;
        currentState = READING_CHECKSUM_2;
        break;
        
      case READING_CHECKSUM_2:
        received_checksum |= (incoming_byte << 8);
        // --- AÑADE ESTE BLOQUE DE DEBUG ---
        Serial.print("Primeros 8 bytes del payload recibido: ");
        for(int i=0; i<8; i++) {
          Serial.printf("0x%02X ", payload_buffer[i]);
        }
        Serial.println();
        // --- FIN DEL BLOQUE DE DEBUG ---
        
        uint16_t calculated_checksum = calculate_checksum(payload_buffer, received_length);

        if (calculated_checksum == received_checksum) {
          Serial.println("¡Éxito! Checksum correcto. Enviando a InfluxDB...");
          sendToInfluxDB_v2(adc_samples, TOTAL_CAPTURE_SAMPLES);
        } else {
          Serial.printf("¡Fallo! Error de Checksum. Recibido: 0x%04X, Calculado: 0x%04X\n", received_checksum, calculated_checksum);
        }
        
        currentState = WAITING_FOR_HEADER_1;
        break;
    }
  }
}

// =================================================================
// NUEVA FUNCIÓN DE ENVÍO PARA INFLUXDB v2
// =================================================================
void sendToInfluxDB_v2(uint16_t* buffer, uint16_t num_samples) {
  //String event_id = String(millis());
  const uint64_t sampling_period_ns = 32552;
  // Para la API antigua, no podemos obtener el tiempo del cliente, así que lo calculamos nosotros.
  // ¡OJO! Esto requiere que el reloj del ESP32 esté sincronizado (ej. con NTP) para ser preciso.
  // Por ahora, para la prueba, usamos un valor de inicio ficticio.
  struct timeval tv;
  gettimeofday(&tv, NULL);
  uint64_t current_timestamp_ns = (uint64_t)tv.tv_sec * 1000000000L + (uint64_t)tv.tv_usec * 1000;
  String event_id = String(current_timestamp_ns);

  Serial.println("Iniciando envío por lotes a InfluxDB v2 (Modo de compatibilidad)...");

  String line_protocol_batch; // String para acumular los puntos del lote
  int points_in_batch = 0;    // Contador para el lote

  for (int i = 0; i < num_samples; i++) {
    // Construimos manualmente cada línea del protocolo InfluxDB
    // Formato: measurement,tag=value field=value timestamp
    line_protocol_batch += "voltage_waveform";
    line_protocol_batch += ",device_id=" + String(DEVICE_ID);
    line_protocol_batch += ",location=" + String(LOCATION);
    line_protocol_batch += ",trigger_type=manual_button";
    line_protocol_batch += ",event_id=" + event_id;
    line_protocol_batch += " value=" + String(buffer[i]);
    line_protocol_batch += " " + String(current_timestamp_ns + (i * sampling_period_ns));
    line_protocol_batch += "\n"; // Cada punto termina con un salto de línea

    points_in_batch++;

    // Si el lote está lleno, lo enviamos
    if (points_in_batch >= BATCH_SIZE) {
      Serial.printf("Enviando lote de %d puntos...\n", points_in_batch);
      // Serial.println(line_protocol_batch);
      // Las versiones antiguas usan writeRecord para enviar el string del protocolo de línea
      if (!client.writeRecord(line_protocol_batch)) {
        Serial.print("Error al escribir lote en InfluxDB: ");
        Serial.println(client.getLastErrorMessage());
      }
      // Reseteamos el string y el contador
      line_protocol_batch = "";
      points_in_batch = 0;
    }
  }

  // Enviar los puntos restantes que no completaron un lote
  if (points_in_batch > 0) {
    Serial.printf("Enviando último lote de %d puntos...\n", points_in_batch);
    if (!client.writeRecord(line_protocol_batch)) {
      Serial.print("Error al escribir el último lote en InfluxDB: ");
      Serial.println(client.getLastErrorMessage());
    }
  }

  Serial.println("Envío de la captura completa a InfluxDB finalizado.");
}

// =================================================================
// FUNCIÓN DE CHECKSUM
// =================================================================
uint16_t calculate_checksum(const uint8_t* data, uint16_t length) {
    uint16_t sum1 = 0;
    uint16_t sum2 = 0;
    for (uint16_t i = 0; i < length; ++i) {
        sum1 = (sum1 + data[i]) % 255;
        sum2 = (sum2 + sum1) % 255;
    }
    return (sum2 << 8) | sum1;
}

// uint16_t calculate_checksum(const uint8_t* data, uint16_t length) {
//     uint16_t checksum = 0;
//     for (uint16_t i = 0; i < length; i++) {
//         checksum += data[i];
//     }
//     return checksum;
// }