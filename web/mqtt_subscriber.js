// reference: https://eclipse.dev/paho/files/jsdoc/index.html
//source: https://github.com/eclipse-paho/paho.mqtt.javascript?tab=readme-ov-file

let port = 8080
let BROKER = "test.mosquitto.org"
let pChan = "OpenDemandResponse/Participant/" //path for participants
let pList = [];//['AlexN']; //list of participants
let aChan = "OpenDemandResponse/Event/BoroughHall" //aggregator channel
let partChan = "OpenDemandResponse/participants" //channel for participants to broadcast their own path

// Create a client instance
let client = new Paho.MQTT.Client(BROKER, Number(port), "clientId");

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect});


// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  client.subscribe(partChan);
  for (let p = 0; p < pList.length; p++){
      client.subscribe(pChan + p);
  }
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
  console.log(message.destinationName)
  console.log(pList)
  if (message.destinationName == partChan){
    //check if participant is new, and if so subscribe
    if (!pList.includes(message.payloadString)){
      pList.push(message.payloadString)
      document.getElementById("participants").innerHTML = pList;

      client.subscribe(pChan + message.payloadString);
    }
  } else {
    let values = ['battery', 'ac_out', 'ac_in', 'dc_out', 'dc_in', 'r1', 'pv', 'rpi', 'load', 'timestamp']
    let units = ['%', 'W', 'W', 'W', 'W', '', 'W', 'W', 'W','']
    data = message.payloadString.split("#");
    for (let v = 0; v < values.length;v++){
      updatePage(values[v],data[v], units[v])
    }
  }
}

function updatePage(id,d, u){
  document.getElementById(id).innerHTML = id + ": " + d + " " + u;
}