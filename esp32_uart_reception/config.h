#ifndef CONFIG_H
#define CONFIG_H

// --- Configuración Wi-Fi ---
#define WIFI_SSID "HUAWEI-106Z30"
#define WIFI_PASSWORD "DanRam0412?"

// --- Configuración InfluxDB ---
#define INFLUXDB_URL "http://192.168.3.14:8086" // ¡Importante! Usa la IP de tu PC, no localhost.
// #define INFLUXDB_TOKEN "l4Pc6bk84nlZOaqRuZzJm7w9JHd7Qq9_k5k7ZTKubg1RU1CZVJGHs1fjdCKH02El248GYB0ILFVLjYrROz6Vow=="
#define INFLUXDB_TOKEN "GCat09CuQtF7tMcAZuiSXV8LxU9EncYOsAfi79TRVLtBz2naqBIe0htbIEwqKjuSNKEHx4wFlsLwNglrtvgSHg=="
#define INFLUXDB_ORG "ITM_PCIE"          // La organización que creaste
#define INFLUXDB_BUCKET "senales_adc" // El bucket que creaste

// --- Configuración del Dispositivo (Tags) ---
#define DEVICE_ID "STM32H7_FV_System_01"
#define LOCATION "Laboratorio_A"

#endif