//TODO: access packid parameter
//let dataJson = document.getElementById('graph').innerHTML;
//let data = JSON.parse(dataJson);

let map = L.map('leaflet-map').setView([0, 0], 2);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1IjoieGl0cmljIiwiYSI6ImNrMTBuMnljNDAwM3Uzbm8wcjZpbWp1ZWEifQ.-1A8mRmzUpgHD4_Y4nCx0A'
}).addTo(map);

var marker = L.marker([51.5, -0.09]).addTo(map);
// create a red polyline from an array of LatLng points
var latlngs = [
    [45.51, -122.68],
    [37.77, -122.43],
    [34.04, -118.2]
];

var polyline = L.polyline(latlngs, { color: 'red' }).addTo(map);

//Runs over all lat, longs and creates a blue dot for every coordinates.
//Makes a mouseover for the values; coordinate, timestamp and package event.
var timestamp = "15:04:2020:13:20"
var event = "Shaked!"
var i;
for (i = 0; i < latlngs.length; i++) {
    var dotCoordinate = L.circleMarker(latlngs[i], { radius: 50, color: 'blue' }).addTo(map).bindTooltip(`
        Coordinate: ${latlngs[i]} <br/>
        Timestamp: ${timestamp} <br/> 
        Event: ${event}`);
}
// zoom the map to the polyline
map.fitBounds(polyline.getBounds());

