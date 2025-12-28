/*
  Explore IoT - Activity 01 (extendido con WiFi + HTTP)
*/
#include <Arduino_MKRIoTCarrier.h>
#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>

MKRIoTCarrier carrier;

// =======================
// VARIABLES SENSORES
// =======================
float temperature = 0;
float humidity = 0;

// Valores finales ajustados
float finalTemperature = 0;
float finalHumidity = 0;

// =======================
// WIFI CONFIG
// =======================
char ssid[] = "wifi-CsComputacion";
char pass[] = "EPCC2022$";

// =======================
// SERVER CONFIG
// =======================
char serverAddress[] = "10.7.135.45";
int port = 5000;

// =======================
// CLIENTES
// =======================
WiFiClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, port);

void setup() {
  Serial.begin(9600);

  CARRIER_CASE = false;
  carrier.begin();

  connectWiFi();
}

void loop() {
  // =======================
  // LECTURA SENSORES
  // =======================
  temperature = carrier.Env.readTemperature();
  humidity = carrier.Env.readHumidity();

  // =======================
  // AJUSTE DE VALORES
  // =======================
  finalTemperature = temperature;
  finalHumidity = humidity;

  if (temperature >= 30.0) {
    finalTemperature = temperature + 70.0;
    finalHumidity = humidity * 0.1;
  }

  carrier.Buttons.update();

  Serial.print("Temperature original = ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Temperature final = ");
  Serial.print(finalTemperature);
  Serial.println(" °C");

  Serial.print("Humidity original = ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("Humidity final = ");
  Serial.print(finalHumidity);
  Serial.println(" %");

  // =======================
  // BOTONES
  // =======================
  if (carrier.Buttons.onTouchDown(TOUCH0)) {
    printTemperature();
  }

  if (carrier.Buttons.onTouchDown(TOUCH2)) {
    printHumidity();
  }

  // =======================
  // ENVIO HTTP
  // =======================
  sendDataHTTP();

  delay(3000); // cada 10 segundos
}

// =======================
// FUNCIONES DISPLAY
// =======================
void printTemperature() {
  carrier.display.fillScreen(ST77XX_RED);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(4);
  carrier.display.setCursor(20, 80);
  carrier.display.print(finalTemperature);
  carrier.display.print(" C");
}

void printHumidity() {
  carrier.display.fillScreen(ST77XX_BLUE);
  carrier.display.setTextColor(ST77XX_WHITE);
  carrier.display.setTextSize(4);
  carrier.display.setCursor(20, 80);
  carrier.display.print(finalHumidity);
  carrier.display.print(" %");
}

// =======================
// WIFI
// =======================
void connectWiFi() {
  Serial.print("Conectando a WiFi");

  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// =======================
// HTTP
// =======================
void sendDataHTTP() {
  String endpoint = "/api/v1/iothumedad/insert?";
  endpoint += "sensor_value_humedad=" + String(finalHumidity, 2);
  endpoint += "&sensor_value_temperatura=" + String(finalTemperature, 2);

  Serial.println("GET " + endpoint);

  client.get(endpoint);

  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Status: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);
}