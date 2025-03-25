
#include "BluetoothSerial.h"  // BT: Include the Serial Bluetooth library
#include <Wire.h>

//------------------------------------------------------------------------------------------------------------
// Global Variables
//------------------------------------------------------------------------------------------------------------

//I2C Related Stuff
#define SLAVE_ADDRESS 0x12
#define MAX_REPORTS 5
//Bluetooth Related Variables
bool MasterConnected = false;           // BT: Variable to store the current connection state (true=connected/false=disconnected)
String device_name = "ESP32-BT-Slave";  // BT: Device name for the slave (client)
String MACadd = "1C:69:20:C6:5E:32";    // BT: Use the slave MAC address

//Reporting and API related things
float lat_received[] = {42.32112188684637, 42.3123944045252};
float long_received[] = {-83.23126720742225, -83.22663034636045};
char control = 'P'; //Write that down (R is for Requesting Weather Data P is for Posting Ice data)

//Not sure why this is here
String weather;
String gpsData = "";
//Flags for program control
volatile bool latLongAvailable = false;
volatile bool weatherDataAvailable = false;

//Struct to store the transmitted message
 struct tx_message {
   float temperature;
   float dew_point;
   float wind_chill;
   float precipitation;
};

tx_message weather_data;  //Global variable to store the weather data

//------------------------------------------------------------------------------------------------------------
// Bluetooth availability checks
//------------------------------------------------------------------------------------------------------------


// BT: Bluetooth availability check
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run make menuconfig to enable it.
#endif
// BT: Serial Bluetooth availability check
#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Bluetooth not available or not enabled. It is only available for the ESP32 chip.
#endif

BluetoothSerial SerialBT;  // BT: Set the Bluetooth Serial Object



//------------------------------------------------------------------------------------------------------------
// Bluetooth Functions
//------------------------------------------------------------------------------------------------------------


// BT: Bt_Status callback function
void Bt_Status(esp_spp_cb_event_t event, esp_spp_cb_param_t *param) {
  if (event == ESP_SPP_SRV_OPEN_EVT) {  // BT: Checks if the SPP Server connection is open
    Serial.println("Master Connected");
    MasterConnected = true;                 // BT: Server is connected to the slave
  } else if (event == ESP_SPP_CLOSE_EVT) {  // BT: Checks if the SPP connection is closed
    Serial.println("Master Disconnected");
    MasterConnected = false;  // BT: Server connection lost
  }
}


//------------------------------------------------------------------------------------------------------------
// Raspberry Pi 5 Functions 
//------------------------------------------------------------------------------------------------------------



//----------------------------------------------
// Read weather data from the Raspberry Pi
//----------------------------------------------
/*
void readRaspberryPi5() {
  // Check if there is enough data available to read
  if (SerialBT.available() >= sizeof(tx_message)) {
    // Create a buffer to store the incoming data
    byte buffer[sizeof(tx_message)];
    
    // Read the incoming data into the buffer
    SerialBT.readBytes(buffer, sizeof(tx_message));

    // Now unpack the buffer into the weather_data struct
    memcpy(&weather_data, buffer, sizeof(tx_message));
    
    // Set the weatherDataAvailable flag to true
    weatherDataAvailable = true;
  }
}*/
void readRaspberryPi5() {
  if (SerialBT.available() >= sizeof(tx_message)) {  // Ensure full data is available
    byte buffer[sizeof(tx_message)];  // Temporary buffer
    int bytesRead = SerialBT.readBytes(buffer, sizeof(tx_message));

    if (bytesRead == sizeof(tx_message)) {  // Validate full message received
      memcpy(&weather_data, buffer, sizeof(tx_message));  // Copy to struct
      weatherDataAvailable = true;

      // Debugging Output
      Serial.println("Weather data received successfully!");
      Serial.print("Temperature: "); Serial.println(weather_data.temperature);
      Serial.print("Dew Point: "); Serial.println(weather_data.dew_point);
      Serial.print("Wind Chill: "); Serial.println(weather_data.wind_chill);
      Serial.print("Precipitation: "); Serial.println(weather_data.precipitation);
    } else {
      Serial.println("Error: Incomplete weather data received.");
    }
  }
}



//----------------------------------------------
// Send Latitude and Longitude to Raspberry Pi
//----------------------------------------------
void writeToRaspberryPi5() {
 int numOfElements = (sizeof(lat_received) / sizeof(lat_received)) + 1;
  int n = 0;
  int i = 0;
  gpsData = "";
  for (i = 0; i < numOfElements; i++){
    if(n == 0 ){
    gpsData = gpsData + "Control: " + String(control) + 
                 " Latitude: " + String(lat_received[i]) + 
                 " Longitude: " + String(long_received[i]);
                 n = n + 1;
                 Serial.println(n);
    }
    else
    {
          gpsData = gpsData + " Latitude: " + String(lat_received[i]) + " Longitude: " + String(long_received[i]);
    }
                 }
    Serial.println("\nGPS Str: " + gpsData);
    if (MasterConnected) {
    for (int i = 0; i < numOfElements; i++){
    SerialBT.println(gpsData);
    }
    }
    //Delete this else statment when no longer testing
    else{
    gpsData = "";
    }
}


//------------------------------------------------------------------------------------------------------------
// Jetson <------> ESP32 I2C Event Handlers 
//------------------------------------------------------------------------------------------------------------

//----------------------------------------------
// Read Event Handler (Data from Jetson)
//----------------------------------------------
void receiveEvent(int numBytes) {

  /*
  Serial.println("Receive Event");
  Serial.print("Number of Bytes Received: ");
  Serial.println(numBytes);
  */
 struct tx_message {
   float temperature;
   float dew_point;
   float wind_chill;
   float precipitation;
};
  // Buffer to store raw bytes received
  uint8_t rawBuffer[10];
  int bytesRead = 0;

  while (Wire.available() && bytesRead < numBytes) {
    rawBuffer[bytesRead++] = Wire.read();
  }

  if (bytesRead == 10 && rawBuffer[0] == 0) {
    memcpy(&control, rawBuffer + 1, sizeof(char));
    memcpy(&lat_received, rawBuffer + 2, sizeof(float));
    memcpy(&long_received, rawBuffer + 6, sizeof(float));


    /*
    Serial.print("Processed control character: ");
    Serial.println  (control);
    Serial.print("Processed latitude: ");
    Serial.print(lat_received, 6);
    Serial.print(", longitude: ");
    Serial.println(long_received, 6);
    */

    writeToRaspberryPi5();

    latLongAvailable = true;
    weatherDataAvailable = false;
}
}


//----------------------------------------------
// Write Event Handler (Data to Jetson)
//----------------------------------------------

void requestEvent() {
  if (!weatherDataAvailable) {
    Serial.println("No new weather data available, skipping...");
    return;
  }

  uint8_t outBuffer[16];

  memcpy(outBuffer, &weather_data.temperature, sizeof(float));
  memcpy(outBuffer + 4, &weather_data.wind_chill, sizeof(float));
  memcpy(outBuffer + 8, &weather_data.dew_point, sizeof(float));
  memcpy(outBuffer + 12, &weather_data.precipitation, sizeof(float));

  Wire.write(outBuffer, sizeof(outBuffer));

  /*// Debugging Output
  Serial.println("Sent data via I2C:");
  Serial.print("Temperature: "); Serial.println(weather_data.temperature);
  Serial.print("Wind Chill: "); Serial.println(weather_data.wind_chill);
  Serial.print("Dew Point: "); Serial.println(weather_data.dew_point);
  Serial.print("Precipitation: "); Serial.println(weather_data.precipitation);*/
}




//------------------------------------------------------------------------------------------------------------
// Setup and Busy-Wait Loop
//------------------------------------------------------------------------------------------------------------
  
void setup() {
  Serial.begin(115200);  // Sets the data rate for serial data transmission
  // BT: Define the Bt_Status callback
  SerialBT.register_callback(Bt_Status);
  // BT: Starts the Bluetooth device with the name stored in the device_name variable
  SerialBT.begin(device_name);
  Serial.printf("The device with name \"%s\" and MAC address \"%s\" is started.\nNow you can pair it with Bluetooth!\n", device_name.c_str(), MACadd.c_str());

  // I2C communication with Jetson (remains unchanged)
  Wire.begin(SLAVE_ADDRESS);
  Wire.setClock(400000);

  // Hardcoded Latitude and Longitude for Testing


  // Send Hardcoded Data Over Bluetooth for Testing
  

}

void loop() {
  writeToRaspberryPi5();
  delay(2000);  // Send location every 2 seconds
  Serial.println("Loop");
  

  // Check if there is Bluetooth data available
  if (SerialBT.available()) {
    readRaspberryPi5();  // Read weather data from Raspberry Pi
  }

  // Forward weather data to Jetson
  requestEvent();

  Serial.println("New Weather Data:");
  Serial.print("Temperature: "); Serial.println(weather_data.temperature);
  Serial.print("Wind Chill: "); Serial.println(weather_data.wind_chill);
  Serial.print("Dew Point: "); Serial.println(weather_data.dew_point);
  Serial.print("Precipitation: "); Serial.println(weather_data.precipitation);

  delay(2000);


}