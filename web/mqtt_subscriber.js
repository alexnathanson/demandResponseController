// reference: https://eclipse.dev/paho/files/jsdoc/index.html
//source: https://github.com/eclipse-paho/paho.mqtt.javascript?tab=readme-ov-file

let port = 8080
let BROKER = "test.mosquitto.org"
let pChan = "OpenDemandResponse/Participant/AlexN"
let aChan = "OpenDemandResponse/Event/BoroughHall"
let participants = "OpenDemandResponse/participants"
// Create a client instance
var client = new Paho.MQTT.Client(BROKER, Number(port), "clientId");

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect});


// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  client.subscribe(participants);
  client.subscribe(pChan);
  // message = new Paho.MQTT.Message("Hello");
  // message.destinationName = "World";
  // client.send(message);
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
  }
}

// called when a message arrives
function onMessageArrived(message) {
  console.log("onMessageArrived:"+message.payloadString);
}