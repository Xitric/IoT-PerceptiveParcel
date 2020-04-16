let rawRoute = document.getElementById('mapScript').innerHTML;
let route = JSON.parse(rawRoute);

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
            Timestamp: ${secondsToDate(point.time)} <br/> 
            Event: ${"Shake"}`
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
