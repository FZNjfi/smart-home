#include <WiFi.h>

const char* ssid = "ORANGE";
const char* password = "09125941742";

WiFiServer server(80); 

#define BAUD_RATE 9600

void setup() {
  Serial.begin(BAUD_RATE); 
  //Serial.print("connecting to ");
  //Serial.print(ssid);

 WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    //Serial.print(".");
  }
  //Serial.println("");
  //Serial.println("WiFi connected");

  //Serial.print(WiFi.localIP());
  //Serial.println(" connect");

  server.begin();
  //Serial.println("Server started");
}

void loop() {
  WiFiClient client = server.available();  

  if (client) 
  {
    //Serial.println("New client connected");

    String request = "";
    while (client.connected()) 
    {
      if (client.available()) {
        char c = client.read();
        request += c;

        if (request.endsWith("\r\n\r\n")) break;
      }
    }

    String cmd = parseCommand(request);

    String response = "3";
    if (cmd.length() > 0) 
    {
      Serial.println(cmd);
      delay(100);

      unsigned long t0 = millis();
      while ((millis() - t0) < 2000) {
        if (Serial.available()) {
          response = Serial.readStringUntil('\n');
          break;
        }
      }
    } else {
      response = "1";
    }

    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println("Connection: close");
    client.println();
    client.println(response);

    delay(5);
    client.stop();
    //Serial.println("Client disconnected");
  }
}

String parseCommand(String req) {
  int idx = req.indexOf("GET /?cmd=");
  if (idx == -1) return "";

  int start = idx + 10;
  int end = req.indexOf(' ', start);
  if (end == -1) return "";

  String cmd = req.substring(start, end);
  cmd.replace("%20", " "); 
  return cmd;
}
