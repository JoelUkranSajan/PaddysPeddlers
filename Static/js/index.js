const MAP_API = "AIzaSyAn8vI2bgALmlua9RQTTuvdv2NxEIFTrDY";
const MAP_ID = "84426611e9429eac";
const DUBLIN = { lat: 53.3449, lng: -6.2675 };
const ZOOM = 16;
const MAPID = "5a698d3eb10ed879";

let map;
let stationLocations = [];
let individualMarkers = []; // Array to hold all individual markers
let centerMarkers = [];
let currentZoom;
let selectedStation;
//****************************** Flask APi Layer - Start ***************************//

async function sendStationNumber(stationNo) {
  try {
    const response = await fetch("/getStationInfo", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ stationNumber: stationNo }),
    });

    if (!response.ok) {
      showErrorMessage("Network Error!", "Network response was not ok");
      return; // Stop the function if the response is not OK
    }

    const data = await response.json(); // Properly wait for and retrieve the JSON data

    console.log("Success:", data);
    await createDailyChart(data);
    await createStationChart(data);
    updateStationInfo(stationNo);
    // alert('Response from server: ' + JSON.stringify(data)); // Uncomment if needed
  } catch (error) {
    console.error("Error:", error);
    showErrorMessage("Fetch Error!", "An error occurred while fetching data");
  }
}

// A method to get the list of stations from the Flask stations api
async function getStations() {
  try {
    const response = await fetch("/stations");
    if (!response.ok) {
      showErrorMessage("Network Error!", "Network response was not ok");
      return; // Ensure we exit the function if the response is not OK
    }
    const data = await response.json(); // Properly wait for the JSON conversion
    setStations(data);
  } catch (error) {
    // It's good practice to handle possible exceptions from fetch or json parsing
    showErrorMessage("Network Error!", "An error occurred while fetching data");
    console.error("Fetch error:", error);
  }
}


// A method to get the weather from the Flask weather api
async function getWeather() {
  try {
    const response = await fetch("/weather");
    if (!response.ok) {
      showErrorMessage("Network Error!", "Network response was not ok");
      return; // Stop the function if the response is not OK
    }

    const data = await response.json(); // Correctly retrieve the JSON data

    setWeather(data); // Set the weather data
  } catch (error) {
    console.error("Error:", error);
    showErrorMessage("Fetch Error!", "An error occurred while fetching weather data");
  }
}


// A method to set the weather details to the box
function setWeather(data) {
  const locationId = document.getElementById("locationTextId");
  const weatherId = document.getElementById("weatherId");
  const tempId = document.getElementById("tempId");
  const pressureId = document.getElementById("pressureId");
  const humidityId = document.getElementById("humidityId");
  const windSpeedId = document.getElementById("windSpeedId");
  const weatherImageId = document.getElementById("weatherImageId");
  weatherImageId.setAttribute(
    "src",
    `http://openweathermap.org/img/w/${data.weather[0].icon}.png`
  );
  locationId.innerText = `Dublin,Ireland`;
  weatherId.innerText = `${data.weather[0].main}`;
  tempId.innerText = `${data.main.temp} °C`;
  pressureId.innerText = `${data.main.pressure} Pa`;
  humidityId.innerText = `${data.main.humidity} g.kg-1`;
  windSpeedId.innerText = `${data.wind.speed} km/h`;
}

// A method to set markers in the screen
function setStations(stations) {
  stationLocations = [];
  stations.forEach((station) => {
    stationLocations.push({
      stNo: station.number,
      stAddr: station.address,
      lat: station.positionlat,
      lng: station.positionlong,
      AvBk: station.available_bikes,
      AvSt: station.available_bike_stands,
      status: station.status,
    });
  });
}

async function getStationAndBikeInfo(data) {
  await fetch("/getBikeAndStandInfo", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok) {
        showErrorMessage("Network Error!", "Network response was not ok");
      }
      return response.json();
    })
    .then((responseData) => {
      console.log("Response:", responseData);
 // Update HTML elements with received data
 document.getElementById("availableBikesStart").textContent =
 responseData.availableBikesStart;
document.getElementById("availableStandsEnd").textContent =
 responseData.availableStandsEnd;    })
    .catch((error) => {
      console.error("There was a problem with your fetch operation:", error);
    });
}

//****************************** Flask APi Layer - End ***************************//

//****************************** Markers Layer - Start ***************************//

// A method that set the intensitiy of blinking on the screens
function getAnimationType(no_of_bikes_available) {
  switch (true) {
    case no_of_bikes_available >= 0 && no_of_bikes_available <= 10:
      return "smallGlow";
    case no_of_bikes_available > 10 && no_of_bikes_available <= 20:
      return "normalGlow";
    case no_of_bikes_available > 20:
      return "bigGlow";
    default:
      return "normalGlow";
  }
}

// A method that set the marker box when you hover over the markers
function createMarkerContent(station) {
  return `<div id="marker_bubble">
            <div class="station_box">
                <div class="station_no">
                    <div class="station_text">Station No: ${station.stNo}</div>
                    <div class="station_text">${station.stAddr}</div>
                </div>
                <div class="open_box">
                ${station.status}
                </div>
            </div>
            <div class="justify_center">
                <div>Available Bikes:</div><div style="padding-left: 10px;">${station.AvBk}</div>
            </div>
            <div class="justify_center">
                <div>Available Stands:</div><div style="padding-left: 10px;">${station.AvSt}</div>
            </div>
          </div>`;
}

//****************************** Markers Layer - End ***************************//

//****************************** Search Layer - Start ***************************//

const searchClearer = setInterval(closeSearchOptions, 1);
const callApiForStationAndWeather = setInterval(fetchAndUpdate, 500000);

function handleKeyDown(event) {
  if (event.key === "Enter") {
    searchLocation();
  }
}

// Search method to search a specific input
function search(inputElement) {
  var input = inputElement.value.toLowerCase();
  var resultsContainer = inputElement.nextElementSibling; // Get the next sibling, which is the <ul> for search results
  resultsContainer.innerHTML = ""; // Clear previous search results
  resultsContainer.style.display = "block";
  var filteredStations = stationLocations.filter((station) => {
    return (
      station.stNo.toString().includes(input) ||
      station.stAddr.toLowerCase().includes(input)
    );
  });

  // Display filtered results
  filteredStations.forEach(function (station) {
    var li = document.createElement("li");
    li.textContent = station.stNo + " - " + station.stAddr;
    li.onclick = function () {
      inputElement.value = station.stAddr; // Populate the input with the station address
      resultsContainer.style.display = "none"; // Hide the search results
    };
    resultsContainer.appendChild(li);
  });
}

// The search results keeps poping up all the time, a check to remove it everytime
async function closeSearchOptions() {
  var input = document.getElementById("searchInput")?.value; // Convert input to lowercase for case-insensitive search
  if (input === "") {
    const searchOptContainer = document.getElementById("searchOptionContainer");
    searchOptContainer.style.display = "none";
  }

  inputField = document.querySelectorAll('.stationInput')[0]?.value;
  if(inputField === "")
{
  const resultsList = document.querySelectorAll('.searchResults')[0];
  resultsList.style.display = "none"
}
 inputField = document.querySelectorAll('.stationInput')[1]?.value;
  if(inputField === "")
{
  const resultsList = document.querySelectorAll('.searchResults')[1];
  resultsList.style.display = "none"
}
}

async function querySearch(query) {
  return new Promise((resolve, reject) => {
    var autoCompleteList = [];
    var request = {
      query: query,
      fields: ["name", "geometry"],
    };
    var service = new google.maps.places.PlacesService(map);

    if (service != null) {
      service.findPlaceFromQuery(request, (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
          for (var i = 0; i < results.length; i++) {
            var place = results[i];
            var station = {
              stNo: 0, // Assuming station number is not applicable or retrieved from elsewhere
              stAddr: place.name,
              Lat: place.geometry.location.lat(),
              lng: place.geometry.location.lng(),
              AvBk: 0,
              AvSt: 0,
              status: "",
            };
            autoCompleteList.push(station);
          }
          resolve(autoCompleteList); // Resolve the promise with the populated list
        } else {
          return []; // Reject the promise if the API call failed
        }
      });
    }
  });
}

// A method to add search options on the screen from the search input
async function addSearchOptionsOnScreen() {
  const searchOptContainer = document.getElementById("searchOptionContainer");
  // Filter stations based on input
  const input = document.getElementById("searchInput").value; // Convert input to lowercase for case-insensitive search

  var filteredStations = [];
  // Filter station Numbers
  filteredStations = stationLocations.filter((station) => {
    return (
      station.stNo.toString().includes(input) || // Convert station.stNo to string for partial match
      station.stAddr.toLowerCase().includes(input)
    );
  });
  let map_stations = [];
  await querySearch(input)
    .then((response) => {
      map_stations.push(response); // Now it should log the populated list
    })
    .catch((error) => {
      console.error(error); // Handle any errors
    });
  if (map_stations.length > 0) {
    // Adding googles autocompllete to my list
    filteredStations.push(...map_stations[0]);
  }
  if (filteredStations.length >= 1) {
    searchOptContainer.style.display = "block";
    const listContainer = document.getElementById("stationList");
    listContainer.innerHTML = ""; // Clear previous list
    filteredStations.forEach((station) => {
      const listItem = document.createElement("li");
      listItem.onclick = (event) => {
        const input = document.getElementById("searchInput");
        input.value = station.stAddr; // Use .value instead of .textContent for input elements
        searchOptContainer.style.display = "none";
        searchLocation(station.lat, station.lng);
      };
      listItem.textContent = `${station.stNo ? station.stNo + "." : ""} ${
        station.stAddr
      }`;
      listContainer.appendChild(listItem);
    });
  } else {
    searchOptContainer.style.display = "none";
  }
}

// A method to search location
function searchLocation(lat, lng) {
  const geocoder = new google.maps.Geocoder();

  if (isNaN(lat) || isNaN(lng)) {
    const input = document.getElementById("searchInput").value;
    geocoder.geocode({ address: input }, (results, status) => {
      if (status === "OK") {
        getTopStations(results);
      } else {
        showErrorMessage(
          "Search Failed!",
          "Sorry, " + input + ", is out of coverage scope!"
        );
      }
    });
  } else {
    var latlng = { lat: parseFloat(lat), lng: parseFloat(lng) };
    geocoder.geocode({ location: latlng }, (results, status) => {
      if (status === "OK") {
        getTopStations(results);
      } else {
        showErrorMessage(
          "Search Failed!",
          "Sorry, " + input + ", is out of coverage scope!"
        );
      }
    });
  }
}

// A method to get top 5 stations
function getTopStations(results) {
  const targetLocation = results[0].geometry.location;
  map.setCenter(targetLocation);
  map.setZoom(16); // Adjust zoom level as needed

  // Find nearby stations
  console.log(stationLocations);
  const radius = 1000; // Specify the radius in meters
  var nearbyStations = stationLocations.filter((station) => {
    const stationLocations = new google.maps.LatLng(station.lat, station.lng);
    const distance = google.maps.geometry.spherical.computeDistanceBetween(
      targetLocation,
      stationLocations
    );
    return distance <= radius;
  });

  // Sort nearby stations by distance
  nearbyStations.sort((a, b) => {
    const locationA = new google.maps.LatLng(a.lat, a.lng);
    const locationB = new google.maps.LatLng(b.lat, b.lng);
    const distanceA = google.maps.geometry.spherical.computeDistanceBetween(
      targetLocation,
      locationA
    );
    const distanceB = google.maps.geometry.spherical.computeDistanceBetween(
      targetLocation,
      locationB
    );
    return distanceA - distanceB;
  });

  // Select the top 5 stations
  const top5Stations = nearbyStations.slice(0, 5);

  //display top 5 stations
  if (top5Stations.length > 1) {
    displayStations(top5Stations);
  }
}

//****************************** Search Layer - End ***************************//

//****************************** Popup Layer - Start ***************************//

async function handleInput() {
  await closeAllPopups();
  // Display matching stations
  addSearchOptionsOnScreen();
}

// A method to close all the popups
async function closeAllPopups() {
  const searchOptContainer = document.getElementById("searchOptionContainer");
  searchOptContainer.style.display = "none";
  // Close station result if opened
  const searchResultCont = document.getElementById("searchResultContainer");
  searchResultCont.classList.remove("slideIn");
  searchResultCont.classList.add("slideOut");
  await delay(200);
  searchResultCont.style.display = "none";

  const stationInfo = document.getElementById("stationInfoContainer");
  stationInfo.classList.remove("slideIn");
  stationInfo.classList.add("slideOut");
  await delay(200);
  stationInfo.style.display = "none";

  const ridePlannerPopup = document.getElementById("ridePlannerPopup");
  ridePlannerPopup.classList.remove("slideIn");
  ridePlannerPopup.classList.add("slideOut");
  await delay(200);
  ridePlannerPopup.style.display = "none";
}

// A method to remove all the popus from the screen when X is pressed
async function onClosePressed(button) {
  var parentDivId = button.parentNode.id;
  parent = document.getElementById(parentDivId);
  parent.classList.remove("slideIn");
  parent.classList.add("slideOut");
  if (parentDivId == "ridePlannerPopup") {
    await delay(500);
    parent.style.display = "none";
  }
}

// A method to toggle popup from the screen
async function toggleRidePlannerPopup() {
  const searchResultCont = document.getElementById("stationInfoContainer");
  searchResultCont.classList.remove("slideIn");
  searchResultCont.classList.add("slideOut");
  await delay(500);
  searchResultCont.style.display = "none";

  var popup = document.getElementById("ridePlannerPopup");
  if (popup.style.display === "block") {
    popup.classList.remove("slideIn");
    popup.classList.add("slideOut");
    popup.style.display = "none";
  } else {
    popup.classList.add("slideIn");
    popup.classList.remove("slideOut");
    popup.style.display = "block";

    // Get current date
    var currentDate = new Date();
    var currentDateString = currentDate.toISOString().slice(0, 10); // Format: "YYYY-MM-DD"
    // Set the minimum date for all elements with the class "startDate" to today's date
    var startDateInputs = document.querySelectorAll(".startDate");
    startDateInputs.forEach(function (input) {
      input.setAttribute("min", currentDateString);
    });
    var stationInputs = document.querySelectorAll(".stationInput");
    // Loop through each stationInput element and set its display property to "none" if value is empty
    stationInputs.forEach(function (input) {
      if (input.value === "") {
        // Hide the corresponding search results element
        var searchResults = input.nextElementSibling;
        searchResults.style.display = "none";
      }
    });
  }
  resetPopup();
}

async function toggleChartPopup() {
  const searchResultCont = document.getElementById("stationInfoContainer");
  searchResultCont.classList.remove("slideIn");
  searchResultCont.classList.add("slideOut");
  await delay(500);
  searchResultCont.style.display = "none";

  var popup = document.getElementById("stationChartPopup");
  popup.classList.add("slideIn");
  popup.classList.remove("slideOut");
  popup.style.display = "block";
}

//****************************** Popup Layer - End ***************************//

//****************************** Station Informstion - Start ***************************//

// A method to display station details popup
async function displayStationDetails(station) {
  // Close station result if opened

  selectedStation = station;
  const searchResultCont = document.getElementById("searchResultContainer");
  searchResultCont.classList.remove("slideIn");
  searchResultCont.classList.add("slideOut");
  await delay(250);
  searchResultCont.style.display = "none";

  // Display station info box
  const stationDetails = document.getElementById("stationInfoContainer");
  stationDetails.style.display = "block";
  stationDetails.classList.remove("slideOut");
  stationDetails.classList.add("slideIn");

  const stNum = document.getElementById("stationNumberId");
  const stAdd = document.getElementById("stationAddressId");
  const stBikAv = document.getElementById("stationBikesId");
  const stSaAv = document.getElementById("stationStandsId");
  const stSt = document.getElementById("stationStatusId");

  stNum.innerText = station.stNo;
  stAdd.innerText = station.stAddr;
  stBikAv.innerText = station.AvBk;
  stSaAv.innerText = station.AvSt;
  stSt.innerText = station.status;

  map.setZoom(16);
  var centerLatLng = new google.maps.LatLng(station.lat, station.lng);
  map.setCenter(centerLatLng);
  if (selectedStation.stNo) {
    await sendStationNumber(selectedStation.stNo);
  }
}

// A method to impart delay
async function delay(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

// A method to display station near a location on the search bar
async function displayStations(stations) {
  // Close station details if opened
  const stationDetails = document.getElementById("stationInfoContainer");
  stationDetails.classList.remove("slideIn");
  stationDetails.classList.add("slideOut");
  await delay(250);

  stationDetails.style.display = "none";

  // Display search result box
  const searchResultCont = document.getElementById("searchResultContainer");
  searchResultCont.style.display = "block";
  searchResultCont.classList.remove("slideOut");
  searchResultCont.classList.add("slideIn");

  const listContainer = document.getElementById("stationsList");
  // Clear previous list items
  listContainer.innerHTML = "";
  stations.forEach((station) => {
    const listItem = document.createElement("div");
    listItem.classList.add("station");
    listItem.innerHTML = `
      <div>${station.stNo}</div>
      <div>${station.stAddr}</div>
      <div>${station.AvBk}</div>
      <div>${station.AvSt}</div>
    `;
    listContainer.appendChild(listItem);
  });
}

//****************************** Station Informstion - End ***************************//

//*****************************Distance - Start***************************************//
async function calculateAndDisplayRoute(
  originLatLng,
  destLatLng,
  data=null
) {
  const directionsService = new google.maps.DirectionsService();
  directionsRenderer.setMap(map);

  // Clear previous directions from the map
  if (directionsRenderer) {
    directionsRenderer.setMap(null);
  }

  // Initialize or reset the directionsRenderer
  directionsRenderer = new google.maps.DirectionsRenderer({
    suppressMarkers: true, // This prevents the default markers from being displayed

    polylineOptions: {
      strokeColor: "purple",
    },
    map: map, // Ensure the renderer is bound to the current map instance
  });

  directionsService.route(
    {
      origin: originLatLng,
      destination: destLatLng,
      travelMode: google.maps.TravelMode.WALKING,
    },
    async function (response, status) {
      if (status === "OK") {
        directionsRenderer.setDirections(response);
        const route = response.routes[0].legs[0];

        // Create a new marker for the clicked location
        const { AdvancedMarkerElement } = await google.maps.importLibrary(
          "marker"
        );  
        closeAllPopups();
        if (data) {
          setPathMarkers(route, AdvancedMarkerElement);
          await getStationAndBikeInfo(data);
        } else {
          const ridePlannerPopup = document.getElementById("ridePlannerPopup");
          if(ridePlannerPopup.style.display == "block")
          {
            return
          }
          setRouteMarkers(route, AdvancedMarkerElement);
        }
        // Show an info box with distance and time
        // showInfoBox(route.distance.text, route.duration.text, currentMarker);
      } else {
        showErrorMessage(
          "Distance Calcualtion Failed",
          "Directions request failed due to " + status
        );
      }
    }
  );


  function setPathMarkers(route, AdvancedMarkerElement) {
    const container = document.createElement("div");
    container.style.padding = "10px";
    container.style.height = "100px";
    container.style.width = "190px";
    container.style.borderRadius = "20px";
    container.style.backgroundColor = "#5e1675";
    container.style.color = "white";

    // Create the inner content div
    const contentDiv = document.createElement("div");
    contentDiv.style.fontSize = "14px";

    // Add HTML content to the inner div
    contentDiv.innerHTML = `
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
        <strong>Distance:</strong> <span>${route.distance.text}</span>
    </div>
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
        <strong>Duration:</strong> <span>${route.duration.text}</span>
    </div>
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
        <strong>Aprox Av Bikes:</strong> <div id="availableBikesStart" style="flex: 1; text-align: center;"></div>
    </div>
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
        <strong>Aprox Stands:</strong> <div id="availableStandsEnd" style="flex: 1; text-align: center;"></div>
    </div>`;

    // Append the content div to the container
    container.appendChild(contentDiv);

    const startMarker = new AdvancedMarkerElement({
      map: map,
      position: { lat: originLatLng.lat, lng: originLatLng.lng },
      content: container,
    });
    const endMarker = new AdvancedMarkerElement({
      map: map,
      position: { lat: destLatLng.lat, lng: destLatLng.lng },
      content: container,
    });
    setTimeout(function () {
      // Assuming AdvancedMarkerElement has a method to remove itself from the map
      if (startMarker) {
        startMarker.setMap(null);
      }
      if (endMarker) {
        endMarker.setMap(null);
      }
      if (directionsRenderer) {
        directionsRenderer.setMap(null);
      }
    }, 10000);
  }

  function setRouteMarkers(route, AdvancedMarkerElement) {
    const container = document.createElement("div");
    container.style.padding = "10px";
    container.style.height = "50px";
    container.style.width = "150px";
    container.style.borderRadius = "20px";
    container.style.backgroundColor = "#5e1675";
    container.style.color = "white";

    // Create the inner content div
    const contentDiv = document.createElement("div");
    contentDiv.style.fontSize = "14px";

    // Add HTML content to the inner div
    contentDiv.innerHTML = `<strong>Distance:</strong> ${route.distance.text}<br><strong>Duration:</strong> ${route.duration.text}`;

    // Append the content div to the container
    container.appendChild(contentDiv);

    const currentMarker = new AdvancedMarkerElement({
      map: map,
      position: { lat: originLatLng.lat, lng: originLatLng.lng },
      content: container,
    });
    setTimeout(function () {
      // Assuming AdvancedMarkerElement has a method to remove itself from the map
      if (currentMarker) {
        currentMarker.setMap(null);
      }
      if (directionsRenderer) {
        directionsRenderer.setMap(null);
      }
    }, 5000);
  }
}

function showInfoBox(distance, duration, marker) {
  const contentString = `<div style="padding:10px;height: 50px;width: 110px;border-radius:20px; background-color:white;"><div style="font-size: 14px;">
    <strong>Distance:</strong> ${distance}<br>
    <strong>Duration:</strong> ${duration}
  </div></div>`;

  const infoWindow = new google.maps.InfoWindow({
    content: contentString,
  });

  infoWindow.open(map, marker);
  google.maps.event.addListener(infoWindow, "closeclick", function () {
    marker.setMap(null);
  });
}

//*****************************Distance - End***************************************//

//****************************Error - Start****************************************//
function showErrorMessage(title, message) {
  // Get the container for the error messages
  let container = document.getElementById("errorMessageContainer");
  let messageBox = document.getElementById("errorMessageBox");

  // Update the title and message if the box already exists
  document.getElementById("errorTitleMessage").innerHTML = title;
  document.getElementById("errorMessage").innerHTML = message;

  // Make the container visible
  container.style.display = "block";
  messageBox.style.display = "block";

  // Add slide-in animation
  messageBox.classList.remove("fadeOut");
  messageBox.classList.add("fadeIn");

  // Optionally, you can add a function to hide the message after some time or on click
  setTimeout(function () {
    messageBox.classList.remove("fadeIn");
    messageBox.classList.add("fadeOut");
    // After the animation ends, hide the container
    delay(500);
    container.style.display = "none";
  }, 3000); // Adjust timing as needed
}

//****************************Error - End******************************************//

//****************************** MAP - Start ***************************//

async function fetchAndUpdate() {
  await getStations();
  await getWeather();
}

let directionsRenderer = new google.maps.DirectionsRenderer();

//Function for creating the map layout and plotting the set of initial set of locations
async function initMap() {
  await fetchAndUpdate();
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
  const { Map, InfoWindow, MarkerClusterer } = await google.maps.importLibrary(
    "maps"
  );

  const map_content = {
    center: DUBLIN,
    zoom: ZOOM,
    mapId: MAPID,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    mapTypeControl: false,
    streetViewControl: false,
  };
  map = new Map(document.getElementById("mapContainer"), map_content);
  map.addListener("zoom_changed", function () {
    // Your code to handle zoom change goes here
    var zoomLevel = map.getZoom();
  });
  stationLocations.forEach((station, index) => {
    const label = station.stNo;
    const address = station.address;
    const circle = document.createElement("div");

    circle.setAttribute("class", "marker_dot");
    circle.setAttribute("id", getAnimationType(station.AvBk));
    circle.textContent = label;
    let advanced_marker = new AdvancedMarkerElement({
      map: map,
      position: { lat: station.lat, lng: station.lng },
      content: circle,
    });
    // markers.push(advanced_marker);
    const infowindow = new InfoWindow({
      content: createMarkerContent(station),
    });

    map.addListener("click", async function (e) {
      const lat = e.latLng.lat();
      const lng = e.latLng.lng();
      let nearestStation = null;
      let minDistance = Number.MAX_VALUE;

      stationLocations.forEach((station) => {
        const distance = google.maps.geometry.spherical.computeDistanceBetween(
          new google.maps.LatLng(lat, lng),
          new google.maps.LatLng(station.lat, station.lng)
        );
        if (distance < minDistance) {
          nearestStation = station;
          minDistance = distance;
        }
      });

      await calculateAndDisplayRoute(
        { lat, lng },
        { lat: nearestStation.lat, lng: nearestStation.lng }
      );
    });

    advanced_marker.content.addEventListener("mouseenter", () => {
      advanced_marker.style.zIndex = "10";
      infowindow.open({
        anchor: advanced_marker,
        map: map,
      });
    });
    advanced_marker.content.addEventListener("mouseleave", () => {
      advanced_marker.style.zIndex = "1";
      infowindow.close();
    });

    advanced_marker.addListener("gmp-click", () => {
      displayStationDetails(station);
    });
    individualMarkers.push(advanced_marker);
  });

  // Listen for zoom changes
  map.addListener("zoom_changed", async () => {
    await handleZoomChange();
  });
}

async function handleZoomChange() {
  const newZoom = map.getZoom();
  if (newZoom <= 13) {
    if (currentZoom > 13) {
      // We are zooming out to below zoom level 8
      await aggregateMarkers();
    }
  } else {
    if (currentZoom <= 13) {
      // We are zooming in past zoom level 8
      await disperseMarkers();
    }
  }
  currentZoom = newZoom;
  console.log(currentZoom);
  console.log(newZoom);
}

async function aggregateMarkers() {
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  // Calculate the center of all markers
  console.log("Aggregate method 8");
  let lat = 0;
  let lng = 0;
  console.log(individualMarkers);
  individualMarkers.forEach((marker) => {
    lat += marker.position.lat;
    lng += marker.position.lng;
    marker.map = null; // Hide individual markers
  });
  lat /= individualMarkers.length;
  lng /= individualMarkers.length;
  const distinctMarkers = findDistinctMarkers(individualMarkers);

  distinctMarkers.forEach((marker) => {
    const circle = document.createElement("div");
    circle.classList.add("marker_dot");
    circle.classList.add("big_marker");
    circle.setAttribute("id", "bigGlow");
    circle.textContent = "";

    const centerMarker = new AdvancedMarkerElement({
      map: map,
      position: { lat: marker.position.lat, lng: marker.position.lng },
      content: circle,
    });

    centerMarker.addListener("click", function () {
      var centerLatLng = new google.maps.LatLng(
        centerMarker.position.lat,
        centerMarker.position.lng
      );

      map.setCenter(centerLatLng); // Center the map on the marker
      map.setZoom(16); // Set the zoom level to 16
    });
    centerMarkers.push(centerMarker);
  });
}

function findDistinctMarkers(markers) {
  if (markers.length < 5) {
    return markers; // Return all markers if there are fewer than 5
  }

  let north = markers[0];
  let south = markers[0];
  let east = markers[0];
  let west = markers[0];
  let center = markers[0];
  let minLat = markers[0].position.lat;
  let maxLat = markers[0].position.lat;
  let minLng = markers[0].position.lng;
  let maxLng = markers[0].position.lng;

  // Calculate sum for the average (central point)
  let latSum = 0;
  let lngSum = 0;

  markers.forEach((marker) => {
    if (marker.position.lat > north.position.lat) north = marker;
    if (marker.position.lat < south.position.lat) south = marker;
    if (marker.position.lng > east.position.lng) east = marker;
    if (marker.position.lng < west.position.lng) west = marker;

    latSum += marker.position.lat;
    lngSum += marker.position.lng;

    minLat = Math.min(minLat, marker.position.lat);
    maxLat = Math.max(maxLat, marker.position.lat);
    minLng = Math.min(minLng, marker.position.lng);
    maxLng = Math.max(maxLng, marker.position.lng);
  });

  // Determine the central marker by finding the closest to the average
  let averageLat = latSum / markers.length;
  let averageLng = lngSum / markers.length;
  let smallestDistance = Number.MAX_VALUE;

  markers.forEach((marker) => {
    let distance = Math.sqrt(
      Math.pow(marker.position.lat - averageLat, 2) +
        Math.pow(marker.position.lng - averageLng, 2)
    );
    if (distance < smallestDistance) {
      smallestDistance = distance;
      center = marker;
    }
  });

  // Hide all markers and then only show the distinct ones
  markers.forEach((marker) => {
    marker.map = null; // Hide marker
  });

  // Return the five distinct markers
  return [north, south, east, west, center];
}

function disperseMarkers() {
  individualMarkers.forEach((marker) => {
    marker.map = map; // Hide individual markers
  });
  centerMarkers.forEach((centerMarker) => {
    centerMarker.map = null; // Hide the center marker
  });
}

//****************************** MAP - End ***************************//

// Function for sending data for a planned trip to Flask.
async function planDataToFlask() {
  const startDateValue = document.querySelector(".startDate").value;
  const startTimeValue = document.getElementById("startTime").value;
  const startStationAddr = document.querySelectorAll(".stationInput")[0].value;

  const endDateValue = document.querySelector(".startDate").value;
  const endTimeValue = document.getElementById("endTime").value;
  const endStationAddr = document.querySelectorAll(".stationInput")[1].value;
  const inputs = document.querySelectorAll(
    '#ridePlannerPopup input[type="text"], #ridePlannerPopup input[type="date"], #ridePlannerPopup input[type="time"]'
  );
  let allFilled = true;

  inputs.forEach((input) => {
    if (input.value === "") {
      allFilled = false;
    }
  });

  if (!allFilled) {
    showErrorMessage(
      "Fields Missing",
      "Please fill out all fields before confirming."
    );
    return;
  }

  if (endTimeValue < startTimeValue) {
    showErrorMessage("Time Error", "You have filled the wrong reaching time");
    return;
  } else if (endTimeValue === startTimeValue) {
    showErrorMessage("Time Error", "Start and end time cannot be same");
    return;
  }

  const startDate = new Date(startDateValue);
  const endDate = new Date(endDateValue);

  const startMonth = startDate.getMonth() + 1;
  const startHour = parseInt(startTimeValue.split(":")[0], 10);
  const startMinute = parseInt(startTimeValue.split(":")[1], 10);
  const startSecond = startDate.getSeconds();
  const startDayOfWeek = startDate.getDay();

  const endMonth = endDate.getMonth() + 1;
  const endHour = parseInt(endTimeValue.split(":")[0], 10);
  const endMinute = parseInt(endTimeValue.split(":")[1], 10);
  const endSecond = endDate.getSeconds();
  const endDayOfWeek = endDate.getDay();

  const startStation = stationLocations.find(
    (station) => station.stAddr === startStationAddr
  );
  const startStationNumber = startStation ? startStation.stNo : null;
  const endStation = stationLocations.find(
    (station) => station.stAddr === endStationAddr
  );
  const endStationNumber = endStation ? endStation.stNo : null;

  const startLocation = { lat: startStation.lat, lng: startStation.lng };
  const endLocation = { lat: endStation.lat, lng: endStation.lng };

  const startUnixTimestamp = Math.floor(startDate.getTime() / 1000);
  const endUnixTimestamp = Math.floor(endDate.getTime() / 1000);

  // Data object to send
  const data = {
    startMonth: startMonth,
    startHour: startHour,
    startMinute: startMinute,
    startSecond: startSecond,
    startDayOfWeek: startDayOfWeek,
    startDate: startDateValue,
    startTime: startTimeValue,
    startStation: startStationAddr,
    startStationNumber: startStationNumber,
    startUnixTimestamp: startUnixTimestamp,

    endMonth: endMonth,
    endHour: endHour,
    endMinute: endMinute,
    endSecond: endSecond,
    endDayOfWeek: endDayOfWeek,
    endDate: endDateValue,
    endTime: endTimeValue,
    endStation: endStationAddr,
    endStationNumber: endStationNumber,
    endUnixTimestamp: endUnixTimestamp, // End Unix timestamp
  };

  // Fetch request
  await calculateAndDisplayRoute(startLocation, endLocation, data);
}

// Function to reset the popup once closed.
function resetPopup() {
  const startDateInput = document.querySelector(".startDate");
  const startTimeInput = document.getElementById("startTime");
  const startStationInput = document.querySelectorAll(".stationInput")[0];
  const endDateInput = document.querySelector(".startDate");
  const endTimeInput = document.getElementById("endTime");
  const endStationInput = document.querySelectorAll(".stationInput")[1];

  startDateInput.value = "";
  startTimeInput.value = "";
  startStationInput.value = "";
  endDateInput.value = "";
  endTimeInput.value = "";
  endStationInput.value = "";

  // document.getElementById("availableBikesStart").textContent = "";
  // document.getElementById("availableStandsEnd").textContent = "";
}

//**********************Charts - Start*******************************//

let globalAvBkChart = null; // Declare a global variable to hold the chart instance
let globalDayChart = null;

function updateStationInfo(stationNumber) {
  // Update the station number
  document.getElementById("stationNoId").textContent = stationNumber;

  // Update the day of the week
  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  const today = new Date();
  const dayOfWeek = days[today.getDay()];
  document.getElementById("dayId").textContent = dayOfWeek;
}

async function createStationChart(data) {
  // First calculate daily averages from the availability data
  const dailyBikeAverages = await calculateDailyAverages(data.bikes[1]);
  const dailyStationAverages = await calculateDailyAverages(data.stands[1]);
  // Generating labels for each day using today's date
  const today = new Date();
  const labels = Array.from({ length: 5 }, (_, i) => {
    const nextDay = new Date(today);
    nextDay.setDate(today.getDate() + i);
    return formatDate(nextDay);
  });
  const cti = document.getElementById("nextFiveDayChart").getContext("2d");
  if (globalAvBkChart) {
    globalAvBkChart.destroy();
  }
  globalAvBkChart = new Chart(cti, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Approx Bikes per Day",
          data: dailyBikeAverages,
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
          tension: 0.4,
        },
        {
          label: "Approx Stands per Day",
          data: dailyStationAverages,
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
          tension: 0.4,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Bikes Available",
          },
          grid: {
            display: true,
            color: "rgba(0, 0, 0, 0.1)",
            borderColor: "black", // Adds border on Y-axis
            borderWidth: 2,
          },
        },
        x: {
          title: {
            display: true,
            text: "Days",
          },
          grid: {
            display: true,
            color: "rgba(0, 0, 0, 0.1)",
            borderColor: "black", // Adds border on X-axis
            borderWidth: 2,
          },
        },
      },
    },
  });
}

async function calculateHourlyAverages(data) {
  if (data.length < 96) {
    console.error("Incomplete data for today");
    return [];
  }

  let hourlyAverages = [];
  // Loop through each hour, there are 4 quarters per hour (15 min intervals)
  for (let i = 0; i < data.length; i += 4) {
    let sum = 0;
    // Sum up the data points for each hour
    for (let j = i; j < i + 4; j++) {
      sum += data[j];
    }
    // Calculate average and add to the hourly averages array
    hourlyAverages.push(sum / 4);
  }
  return hourlyAverages;
}

async function createDailyChart(data) {
  // Calculate hourly averages from the availability data
  const hourlyData = await calculateHourlyAverages(data.bikes[1]);

  const ctx = document.getElementById("stationInfoChart").getContext("2d");
  if (globalDayChart) {
    globalDayChart.destroy();
  }
  const labels = Array.from({ length: 24 }, (_, i) => {
    const time = new Date();
    time.setHours(i, 0, 0, 0); // Set time from 00:00 increasing by 1 hour
    return `${time.getHours()}:00`; // Display hour only
  });
  globalDayChart = new Chart(ctx, {
    type: "line", // Line chart to show the trend over the hours of today
    data: {
      labels: labels,
      datasets: [
        {
          label: `Bikes Available on ${formatDate(new Date())}`,
          data: hourlyData,
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          borderColor: "rgba(255, 99, 132, 1)",
          borderWidth: 1,
          tension: 0.7,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Bikes Available",
          },
          grid: {
            display: true,
            color: "rgba(0, 0, 0, 0.1)",
            borderColor: "black", // Adds border on Y-axis
            borderWidth: 2,
          },
        },
        x: {
          title: {
            display: true,
            text: "Time (every hour)",
          },
          grid: {
            display: true,
            color: "rgba(0, 0, 0, 0.1)",
            borderColor: "black", // Adds border on X-axis
            borderWidth: 2,
          },
        },
      },
    },
  });
}

async function calculateDailyAverages(data, intervalsPerDay = 88) {
  let dailyAverages = [];
  for (let i = 0; i < data.length; i += intervalsPerDay) {
    let dayData = data.slice(i, i + intervalsPerDay);
    let dailyAverage =
      dayData.reduce((sum, current) => sum + current, 0) / dayData.length;
    dailyAverages.push(dailyAverage);
  }
  return dailyAverages;
}

function formatDate(date) {
  return `${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}`;
}

async function calculateTodayAverages(data) {
  if (data.length < 96) {
    console.error("Incomplete data for today");
    return [];
  }
  return data.slice(0, 96);
}

//**********************Charts - End*******************************//
