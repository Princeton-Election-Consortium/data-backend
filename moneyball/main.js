var siteWidth = 1280;
var scale = screen.width /siteWidth

//document.querySelector('meta[name="viewport"]').setAttribute('content', 'width='+siteWidth+', initial-scale='+scale+'');

var redist_data 

d3.csv("redistricting summaries.csv").then(function(data) {
    redist_data = data
  });

/**
 * CONSTANTS AND GLOBALS
 * */
const width = window.innerWidth * 0.9, 
      height = window.innerHeight * 0.7, 
      margin = { top: 20, bottom: 50, left: 60, right: 40 };

// mapboxgl.accessToken = 'pk.eyJ1Ijoib3BlbnByZWNpbmN0cyIsImEiOiJjanVqMHJtM3gwMXdyM3lzNmZkbmpxaXpwIn0.ZU772lvU-NeKNFAkukT6hw';
mapboxgl.accessToken = 'pk.eyJ1IjoibWRoYWxsZWUiLCJhIjoiY2tjcWVscWkyMTN6czM0bGJ4eXB1dDNzMSJ9.ZqDUoCfQVWMN_ASDB9Mhdg';

const zoomThreshold = 2;
const zoomState = 5.2;

const map = new mapboxgl.Map({
    container: 'map-container',
    // style: 'mapbox://styles/openprecincts/ckb82ge1d1xx81ip9v5i0xony'
    style: 'mapbox://styles/mdhallee/ckd9fgs5405tt1iphjqsl6zwk',

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
                'fill-outline-color': '#c4c4c4',
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
                    "hsla(288, 88%, 56%, 0.85)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      30
                    ],
                    "hsla(232, 82%, 69%, 0.75)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      20
                    ],
                    "hsla(193, 82%, 74%, 0.75)",
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
                        "hsla(288, 88%, 56%, 0.85)",
                        [
                          ">=",
                          ["get", "VOTER_POWER"],
                          30
                        ],
                        "hsla(232, 82%, 69%, 0.75)",
                        [
                          ">=",
                          ["get", "VOTER_POWER"],
                          20
                        ],
                        "hsla(193, 82%, 74%, 0.75)",
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

        // can change to .POSTAL now ***********************
        var state = prop.DISTRICT.substring(0,2)

        $('#sstates').val(state)
        $('#allstcheckbx').prop( "checked", false );
        $("#submit").click();

        updateStateInfoSidebar(state)

        let myCongressionalTable = buildDistrictHoverTable(prop)

        new mapboxgl.Popup(el)
            .setLngLat(e.lngLat)
            .setHTML(myCongressionalTable)
            .addTo(map);
        });

    // State-Senate-layer click and pop-up stuff
    map.on('click', 'state-senate', function(e) {
        e.originalEvent.cancelBubble = true; 
        let prop = e.features[0].properties
        let el = document.createElement('div');
        el.className = 'marker'
        console.log("clicked prop", prop);

        // can change to .POSTAL now ***********************
        var state = prop.DISTRICT.substring(0,2)

        $('#sstates').val(state)
        $('#allstcheckbx').prop( "checked", false );
        $("#submit").click();

        updateStateInfoSidebar(state)

        let myCongressionalTable = buildDistrictHoverTable(prop)

        new mapboxgl.Popup(el)
            .setLngLat(e.lngLat)
            .setHTML(myCongressionalTable)
            .addTo(map);
        });

    // add "Reset Map" 
    document.getElementById('zoom').addEventListener('click', function() {
        map.zoomTo(zoomThreshold);
        map.fitBounds(bbox, {
            // padding: {top: 10, bottom:25, left: 15, right: 5},
            linear: true,
            });
        map.setLayoutProperty('state-house', 'visibility', 'visible');
        map.setLayoutProperty('state-senate', 'visibility', 'none');
        });

    // add address search thing
    map.addControl(
        new MapboxGeocoder({
        accessToken: mapboxgl.accessToken,
        mapboxgl: mapboxgl
        })
    );
    map.addControl(new mapboxgl.NavigationControl());

    // add plus/minus zoom button
    // map.addControl(new mapboxgl.NavigationControl());

    const selectElement = d3.select("#dropdown").on("change", function(e) {
        console.log("new selected layer is", this.value);
        clickedLayer = this.value;
        var visibility = map.getLayoutProperty(clickedLayer, 'visibility');
        // toggle layer visibility by changing the layout object's visibility property
        if (clickedLayer === 'state-house'){
            map.setLayoutProperty('state-house', 'visibility', 'visible');
            map.setLayoutProperty('state-senate', 'visibility', 'none');
        } else if (clickedLayer === 'state-senate'){
            map.setLayoutProperty('state-house', 'visibility', 'none');
            map.setLayoutProperty('state-senate', 'visibility', 'visible');
        }
      });

    function updateStateInfoSidebar(state) {
        /* find state data in csv data */
        var redist_data_row 
        for (const item of redist_data) {
            if (item.state_po === state) {
            redist_data_row = item
            }
        }

        let clickedStateBox = document.getElementById('clicked-info') 
        let clickedStateInfo = document.getElementById('state-info')
        clickedStateInfo.innerHTML = ""

        clickedStateBox.appendChild(clickedStateInfo)

        /* Add state name title */
        let title = clickedStateInfo.appendChild(document.createElement('div'));
        title.className = 'title';
        title.innerHTML = redist_data_row['state'];

        let impactLevel = redist_data_row['Voter Impact on 2021 Congressional Redisticting:']
        let bipartisonProb = redist_data_row['Bipartisan Control Probability']
        let redistProcess = redist_data_row['Redistricting process']
        let playingField = redist_data_row['2020 election playing field']

        /* Add details to the individual state info -- if they exist */
        let details = clickedStateInfo.appendChild(document.createElement('div'));
        if (impactLevel != 'null') {
            details.innerHTML += 'Voter Impact on 2021 Congressional Redisticting: '.bold() + impactLevel + "<br />";}
        if (bipartisonProb != 'null' && bipartisonProb != '') {
            details.innerHTML += 'Bipartisan Control Probability: '.bold() + bipartisonProb + "<br />";}
        if (redistProcess != 'null') {
            details.innerHTML += 'Redistricting process: '.bold() + redistProcess + "<br />";}
        if (playingField != 'null' && playingField != '') {
            details.innerHTML += '2020 election playing field: '.bold() + playingField + "<br />";}
    }

    function buildDistrictHoverTable(prop) {
        let districtTable = ''
    
        if (prop.VOTER_POWER >= 1 & prop.INCUMBENT == 'R'){
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
            '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.NOM_D + '</td>' + 
            '<tr> <th>' + "R Candidate (Incumbent)" + '</th> <th style="text-decoration: underline">' + prop.NOM_R + '</th>' + 
            '</table>'
    
        }
        else if (prop.VOTER_POWER >= 1 & prop.INCUMBENT == 'D'){
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
            '<tr> <th>' + "D Candidate (Incumbent)" + '</th> <th style="text-decoration: underline">' + prop.NOM_D +'</th>' + 
            '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.NOM_R +  '</td>' + 
            '</table>'
        }
        else if (prop.VOTER_POWER >= 1){
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                        '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
                                    '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
                                    '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.NOM_D + '</td>' + 
                                    '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.NOM_R + '</td>' + 
                                        '</table>'
        }
        else {
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                    '<tr> <th colspan="2"> Not an important district for redistricting</th> </tr>' +
                                    '<tr> <th colspan="2"> *See state redistricing information in sidebar*</th> </tr>' +
                                        '</table>'
        }
    
        return districtTable
    }

    $("#tx-link").click(function() {
        $('#dropdown').val("state-house")
        document.querySelector("#dropdown").dispatchEvent(new Event("change"));
        map.flyTo({
            center: [-97.5, 31.5], 
            zoom: 6,
            speed: 0.4,
            curve: 1
        })
        $('#sstates').val('TX')
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();
    });
    $("#mn-link").click(function() {
        $('#dropdown').val("state-senate")
        document.querySelector("#dropdown").dispatchEvent(new Event("change"));
        map.flyTo({
            center: [-93.7, 45.5], 
            zoom: 6,
            speed: 0.4,
            curve: 1
        })
        $('#sstates').val('MN')
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();
    });
    $("#ks-link").click(function() {
        $('#dropdown').val("state-house")
        document.querySelector("#dropdown").dispatchEvent(new Event("change"));
        map.flyTo({
            center: [-96.31, 38.6], 
            zoom: 6.4,
            speed: 0.4,
            curve: 1
        })
        $('#sstates').val('KS')
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();
    });
    $("#fl-link").click(function() {
        $('#dropdown').val("state-house")
        document.querySelector("#dropdown").dispatchEvent(new Event("change"));
        map.flyTo({
            center: [-81.5, 27.6], 
            zoom: 6.1,
            speed: 0.4,
            curve: 1
        })
        $('#sstates').val('FL')
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();
    });
    $("#ct-link").click(function() {
        $('#dropdown').val("state-house")
        document.querySelector("#dropdown").dispatchEvent(new Event("change"));
        map.flyTo({
            center: [-72.7, 41.6], 
            zoom: 7.8,
            speed: 0.4,
            curve: 1
        })
        $('#sstates').val('CT')
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();
    });
    $("#nc-link").click(function() {
        $('#dropdown').val("state-house")
        document.querySelector("#dropdown").dispatchEvent(new Event("change"));
        map.flyTo({
            center: [-79.5, 35.7], 
            zoom: 6.2,
            speed: 0.4,
            curve: 1
        })
        $('#sstates').val('NC')
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();
    });

    // map.on('mousemove', function(e) {
    //     document.getElementById('info').innerHTML =
    //     // e.point is the x, y coordinates of the mousemove event relative
    //     // to the top-left corner of the map
    //     JSON.stringify(e.point) +
    //     '<br />' +
    //     // e.lngLat is the longitude, latitude geographical position of the event
    //     JSON.stringify(e.lngLat.wrap());
    //     });
});
