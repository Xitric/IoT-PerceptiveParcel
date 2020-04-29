let packageJSON = document.getElementById('mapScript').innerHTML;

let packageData = JSON.parse(packageJSON)
// let route = JSON.get(route)
// humidity = JSON.get(humidity)
// temperature = JSON.get(temperature)

let route = packageData.route
let humidities = packageData.humidities

// Initialize leaflet
let map = L.map('leaflet-map').setView([0, 0], 2);
L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoieGl0cmljIiwiYSI6ImNrMTBuMnljNDAwM3Uzbm8wcjZpbWp1ZWEifQ.-1A8mRmzUpgHD4_Y4nCx0A'
}).addTo(map);

// Create a red polyline from an array of LatLng points
let latlngs = route.map(toCoordinate)
var polyline = L.polyline(latlngs, { color: 'red' }).addTo(map);

// Runs over all lat, longs and creates a blue dot for every coordinates.
// Makes a mouseover for the values; coordinate, timestamp and package event.
// TODO: Events
for (point of route) {
    console.log(point)
    L.circleMarker(
        toCoordinate(point), {
            radius: 5,
            color: 'blue'
        }).addTo(map);
    L.circleMarker(
        toCoordinate(point), {
            radius: 30,
            color: 'transparent'
        }).addTo(map).bindTooltip(
            `Coordinate: ${toCoordinate(point)} <br/>
            Timestamp: ${secondsToDate(point.time)} <br/>`
        );
}

for (humidity of humidities) {
    console.log(humidity)
    L.circleMarker(
        toCoordinate(humidity), {
            radius: 10,
            color: 'black'
        }).addTo(map);
    L.circleMarker(
        toCoordinate(humidity), {
            radius: 30,
            color: 'transparent'
        }).addTo(map).bindTooltip(
            `Coordinate: ${toCoordinate(humidity)} <br/>
            Timestamp: ${secondsToDate(humidity.time)} <br/>
             Event: ${humidity}`
        );
}

// Fit the map to the polyline
map.fitBounds(polyline.getBounds());

function toCoordinate(point) {
    return [point.latitude, point.longitude]
}

function secondsToDate(seconds) {
    let date = new Date(seconds * 1000)
    return `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`
}
