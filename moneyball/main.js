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
    

    //'#e6ebf5'


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
                    "hsla(232, 82%, 75%, 0.75)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      20
                    ],
                    "hsla(193, 82%, 80%, 0.75)",
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
                      30
                    ],
                    "hsla(232, 56%, 75%, 0.68)",
                    [
                      ">=",
                      ["get", "VOTER_POWER"],
                      20
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

        var state = prop.DISTRICT
        state = state.substring(0,2)

        $('#sstates').val(state)
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();

        console.log("state", state);

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

        /* Add state name. */
        let title = clickedStateInfo.appendChild(document.createElement('div'));
        title.className = 'title';
        title.innerHTML = redist_data_row['state'];
        
        /* Add details to the individual state info. */
        let details = clickedStateInfo.appendChild(document.createElement('div'));
        if (redist_data_row['Voter Impact on 2021 Congressional Redisticting:'] != 'null') {
            details.innerHTML += 'Voter Impact on 2021 Congressional Redisticting: '.bold() + redist_data_row['Voter Impact on 2021 Congressional Redisticting:']+ "<br />";
        }
        if (redist_data_row['Bipartisan Control Probability'] != 'null') {
            details.innerHTML += 'Bipartisan Control Probability: '.bold() + redist_data_row['Bipartisan Control Probability']+ "<br />";
        }

        if (redist_data_row['Redistricting process'] != 'null') {
            details.innerHTML += 'Redistricting process: '.bold() + redist_data_row['Redistricting process']+ "<br />";
        }

        if (redist_data_row['2020 election playing field'] != 'null') {
            details.innerHTML += '2020 election playing field: '.bold() + redist_data_row['2020 election playing field']+ "<br />";
        }

        let myCongressionalTable = ''

        if (prop.VOTER_POWER >= 1 & prop.INCUMBENT == 'R'){
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
            '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.NOM_D + '</td>' + 
            '<tr> <th>' + "R Candidate" + '</th> <th>' + prop.NOM_R + ' *' + '</th>' + 
            '<tr> <th colspan="2"> * denotes incumbent </th> </tr>' +
            '</table>'

        }
        else if (prop.VOTER_POWER >= 1 & prop.INCUMBENT == 'D'){
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
            '<tr> <th>' + "D Candidate" + '</th> <th>' + prop.NOM_D + ' *' +'</th>' + 
            '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.NOM_R +  '</td>' + 
            '<tr> <th colspan="2"> * denotes incumbent </th> </tr>' +
            '</table>'
        }
        else if (prop.VOTER_POWER >= 1){
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                        '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
                                    '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
                                    '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.NOM_D + '</td>' + 
                                    '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.NOM_R + '</td>' + 
                                        '</table>'
        }
        else {
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                    '<tr> <th colspan="2"> Not an important district for redistricting</th> </tr>' +
                                    '<tr> <th colspan="2"> *See state redistricing information in sidebar*</th> </tr>' +
                                        '</table>'
        }


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



        var state = prop.DISTRICT
        state = state.substring(0,2)

        $('#sstates').val(state)
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();

        // dropdown.val = [state];
        // //dropdown.trigger('change');

        console.log("state", state);

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

        /* Add state name. */
        let title = clickedStateInfo.appendChild(document.createElement('div'));
        title.className = 'title';
        title.innerHTML = prop.DISTRICT;

        let myCongressionalTable = ''

        if (prop.VOTER_POWER >= 1 & prop.INCUMBENT == 'R'){
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
            '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.NOM_D + '</td>' + 
            '<tr> <th>' + "R Candidate" + '</th> <th>' + prop.NOM_R + ' *' + '</th>' + 
            '<tr> <th colspan="2"> * denotes incumbent </th> </tr>' +
            '</table>'

        }
        else if (prop.VOTER_POWER >= 1 & prop.INCUMBENT == 'D'){
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
            '<tr> <th>' + "D Candidate" + '</th> <th>' + prop.NOM_D + ' *' +'</th>' + 
            '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.NOM_R +  '</td>' + 
            '<tr> <th colspan="2"> * denotes incumbent </th> </tr>' +
            '</table>'
        }
        else if (prop.VOTER_POWER >= 1){
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                        '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.VOTER_POWER.toFixed(2) + '</td>' + 
                                    '<tr> <th>' + "Rating" + '</th> <td>' + prop.LEAN + '</td>' + 
                                    '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.NOM_D + '</td>' + 
                                    '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.NOM_R + '</td>' + 
                                        '</table>'
        }
        else {
            myCongressionalTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.DISTRICT + '</td>' + 
                                    '<tr> <th colspan="2"> Not an important district for redistricting</th> </tr>' +
                                    '<tr> <th colspan="2"> *See state redistricing information in sidebar*</th> </tr>' +
                                        '</table>'
        }



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
