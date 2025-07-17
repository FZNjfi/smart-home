#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "ESP_AP";
const char* password = "12345678";

WebServer server(80);

#define BAUD_RATE 9600 

void setup() {
  Serial.begin(BAUD_RATE); 


  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.println("AP IP address: " + IP.toString());

  server.on("/", handleRoot);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}

void handleRoot() {
  if (server.hasArg("cmd")) {
    String cmd = server.arg("cmd");

    Serial1.println(cmd);
    delay(100); 

    String response = "";
    unsigned long t0 = millis();
    while ((millis() - t0) < 2000) { 
      if (Serial1.available()) {
        response = Serial1.readStringUntil('\n');
        break;
      }
    }

    if (response.length() > 0)
      server.send(200, "text/plain", "Arduino: " + response);
    else
      server.send(200, "text/plain", "No response from Arduino.");
  } else {
    server.send(400, "text/plain", "Missing 'cmd' parameter.");
  }
}
