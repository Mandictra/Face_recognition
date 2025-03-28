#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "TROPICAL";
const char* password = "letatropical";
const int doorPin = 5;  // Change this to the GPIO pin connected to your door lock

WebServer server(80);

void handleControl() {
    if (server.hasArg("action")) {
        String action = server.arg("action");

        if (action == "open_door") {
            digitalWrite(doorPin, HIGH);  // Unlock the door
            delay(3000);  // Keep it open for 3 seconds
            digitalWrite(doorPin, LOW);   // Lock it again
            server.send(200, "text/plain", "Door Opened");
            Serial.println("✅ Door opened via web request.");
        } else {
            server.send(400, "text/plain", "Invalid Action");
        }
    } else {
        server.send(400, "text/plain", "No action provided");
    }
}

void handleRoot() {
    server.send(200, "text/html", "<h1>ESP32 Face Recognition Door Lock</h1>");
}

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    
    pinMode(doorPin, OUTPUT);
    digitalWrite(doorPin, LOW);  // Ensure door is locked at startup

    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());

    server.on("/", handleRoot);
    server.on("/control", handleControl);
    
    server.begin();
    Serial.println("🌍 ESP32 Web Server Started");
}

void loop() {
    server.handleClient();
}
