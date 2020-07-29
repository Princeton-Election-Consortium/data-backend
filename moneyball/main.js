/**
 * CONSTANTS AND GLOBALS
 * */
const width = window.innerWidth * 0.9, 
      height = window.innerHeight * 0.7, 
      margin = { top: 20, bottom: 50, left: 60, right: 40 };

// mapboxgl.accessToken = 'pk.eyJ1Ijoib3BlbnByZWNpbmN0cyIsImEiOiJjanVqMHJtM3gwMXdyM3lzNmZkbmpxaXpwIn0.ZU772lvU-NeKNFAkukT6hw';
mapboxgl.accessToken = 'pk.eyJ1IjoibWRoYWxsZWUiLCJhIjoiY2tjcWVscWkyMTN6czM0bGJ4eXB1dDNzMSJ9.ZqDUoCfQVWMN_ASDB9Mhdg';

const zoomThreshold = 2;

const map = new mapboxgl.Map({
    container: 'map-container',
    // style: 'mapbox://styles/openprecincts/ckb82ge1d1xx81ip9v5i0xony'
    style: 'mapbox://styles/mdhallee/ckd567qcu0baj1iqlnk8sg99b',

});

const bbox = [[-63.588704947691994, 50.715649574086314], [-127.55862265048071, 22.645896726596078]];
map.fitBounds(bbox, {
    padding: {top: 10, bottom:25, left: 15, right: 5},
    linear: true,
});

const svg = d3
      .select("#map-container")
      .append("svg")    
      .attr("width", width)
      .attr("height", height);

map.on('load', function() {

    map.addSource('state-house', {
        type: 'geojson',
        data: 'https://princetonuniversity.github.io/PEC-map/out-files/lower_state_moneyball.geojson'
    });

    map.addSource('state-senate', {
        type: 'geojson',
        data: 'https://princetonuniversity.github.io/PEC-map/out-files/upper_state_moneyball.geojson'
    });

    map.addLayer(
        {
            'id': 'state-house',
            'source': 'state-house',
            'minzoom': zoomThreshold,
            'paint': {
                'fill-outline-color': '#a3a3a3',
                'fill-opacity': [
                    'match',
                    ['get', 'VOTER_POWER'],
                    0, 0.5, 
                    0.8
                    ],
                'fill-color': [
                    "case",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      75
                    ],
                    "hsla(312, 99%, 55%, 0.88)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      45
                    ],
                    "hsla(288, 82%, 56%, 0.85)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      25
                    ],
                    "hsla(232, 56%, 75%, 0.68)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      5
                    ],
                    "hsla(193, 32%, 80%, 0.75)",
                    "hsla(0, 0%, 100%, 0)"
                  ]
                },
            'type': 'fill', 
            'layout': {
                'visibility': 'visible'
                },  
        }
    );

    map.addLayer(
        {
            'id': 'state-senate',
            'source': 'state-senate',
            'minzoom': zoomThreshold,
            'paint': {
                'fill-outline-color': '#a3a3a3',
                'fill-opacity': [
                    'match',
                    ['get', 'VOTER_POWER'],
                    0, 0.5, 
                    0.8
                    ],
                'fill-color': [
                    "case",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      75
                    ],
                    "hsla(312, 99%, 55%, 0.88)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      45
                    ],
                    "hsla(288, 82%, 56%, 0.85)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      25
                    ],
                    "hsla(232, 56%, 75%, 0.68)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      3
                    ],
                    "hsla(193, 32%, 80%, 0.75)",
                    "hsla(0, 0%, 100%, 0)"
                  ]
                },
            'type': 'fill',
            'layout': {
                'visibility': 'none'
                },  
        }
    );

    // State-House-layer click and pop-up stuff
    map.on('click', 'state-house', function(e) {
        e.originalEvent.cancelBubble = true; 
        let prop = e.features[0].properties
        let el = document.createElement('div');
        el.className = 'marker'
        console.log("clicked prop", prop);

        let myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                   '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
                                   '<tr> <th>' + "Dem. Cand." + '</th> <td>' + prop.NOM_D + '</td>' + 
                                   '<tr> <th>' + "Rep. Cand" + '</th> <td>' + prop.NOM_R + '</td>' + 


                                    '</table>'


        new mapboxgl.Popup(el)
            .setLngLat(e.lngLat)
            .setHTML(myCongressionalTable)
            .addTo(map);
        });

    // State-House-layer click and pop-up stuff
    map.on('click', 'state-senate', function(e) {
        e.originalEvent.cancelBubble = true; 
        let prop = e.features[0].properties
        let el = document.createElement('div');
        el.className = 'marker'
        console.log("clicked prop", prop);

        let myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                   '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
                                   '<tr> <th>' + "Dem. Cand." + '</th> <td>' + prop.NOM_D + '</td>' + 
                                   '<tr> <th>' + "Rep. Cand" + '</th> <td>' + prop.NOM_R + '</td>' + 


                                    '</table>'


        new mapboxgl.Popup(el)
            .setLngLat(e.lngLat)
            .setHTML(myCongressionalTable)
            .addTo(map);
        });

    // add legend on zoom
    var congressionalLegendEl = document.getElementById('congressional-legend');
    map.on('zoom', function() {
        if (map.getZoom() >= zoomThreshold) {
            congressionalLegendEl.style.display = 'block';
        } else {
        congressionalLegendEl.style.display = 'none';
        }
    });

    // add "Reset Map" 
    document.getElementById('zoom').addEventListener('click', function() {
        map.zoomTo(zoomThreshold);
        map.fitBounds(bbox, {
            // padding: {top: 10, bottom:25, left: 15, right: 5},
            linear: true,
            });
        map.setLayoutProperty('states-layer', 'visibility', 'visible');
        // map.setLayoutProperty('congressional-border', 'visibility', 'visible');
        // map.setLayoutProperty('congressional-layer', 'visibility', 'visible');
        // map.setLayoutProperty('state-house', 'visibility', 'none');
        // map.setLayoutProperty('state-senate', 'visibility', 'none');
        viewDropdown2('none');
        });

    // add address search thing
    map.addControl(
        new MapboxGeocoder({
        accessToken: mapboxgl.accessToken,
        mapboxgl: mapboxgl
        })
    );

    // add plus/minus zoom button
    // map.addControl(new mapboxgl.NavigationControl());

    function viewDropdown2(displayStyle) {
        /* "inline-block" or "none" */
      var x = document.getElementById("dropdown-2");
      x.style.display = displayStyle

      var y = document.getElementById("zoom");
      y.style.top= (displayStyle === 'none' ? '40px' : '64px')
    }
    
    const selectElement = d3.select("#dropdown").on("change", function(e) {
        console.log("new selected layer is", this.value);
        clickedLayer = this.value;
        var visibility = map.getLayoutProperty(clickedLayer, 'visibility');
        // toggle layer visibility by changing the layout object's visibility property
        if (clickedLayer === 'state-house'){
            map.setLayoutProperty('state-house', 'visibility', 'visible');
            map.setLayoutProperty('state-senate', 'visibility', 'none');
            viewDropdown2('inline-block');
        } else if (clickedLayer === 'state-senate'){
            map.setLayoutProperty('state-house', 'visibility', 'none');
            map.setLayoutProperty('state-senate', 'visibility', 'visible');
            viewDropdown2('inline-block');
        }
      });

});
