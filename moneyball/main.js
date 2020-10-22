var mbleg4_table;
var mbleg3_table;

d3.json("mapbox-boundaries-leg4-v3.json").then(function(data) {
    mbleg4_table = data;
});
d3.json("mapbox-boundaries-leg3-v3.json").then(function(data) {
    mbleg3_table = data;
});

function getFromHouseLookupTableByFeatureId(id) {
    // uses feature_id
    const rows = mbleg4_table.leg4.data.all;
    for (row in rows) {
        if (rows[row]['feature_id'] === id) {
            return rows[row];
        }
    }
}
function getFromSenateLookupTableByFeatureId(id) {
    // uses feature_id
    const rows = mbleg3_table.leg3.data.all;
    for (row in rows) {
        if (rows[row]['feature_id'] === id) {
            return rows[row];
        }
    }
}
function getMoneyballDataByUnitCode(unit_code) {
    let result = {};
    moneyball_data.forEach(function(row) {
        if (row.geoid === unit_code) {
            result = row;
        }
    });
    return result;
}

function filterHouseTable(table) {
    let data = {};
    const rows = table.leg4.data.all;
    for (row in rows) {
        data[rows[row]['unit_code']] = rows[row];
    }
    return data;
}
function filterSenateTable(table) {
    let data = {};
    const rows = table.leg3.data.all;
    for (row in rows) {
        data[rows[row]['unit_code']] = rows[row];
    }
    return data;
}

var moneyball_data;
d3.json("all_results_10_10_2020-sorted-updated.json").then(function(data) {
    moneyball_data = data;
})

var redist_data;
d3.csv("redistricting summaries.csv").then(function(data) {
    redist_data = data;
});

/**
 * CONSTANTS AND GLOBALS
 * */
const width = window.innerWidth * 0.9, 
      height = window.innerHeight * 0.7, 
      margin = { top: 20, bottom: 50, left: 60, right: 40 };

// mapboxgl.accessToken = 'pk.eyJ1Ijoib3BlbnByZWNpbmN0cyIsImEiOiJjanVqMHJtM3gwMXdyM3lzNmZkbmpxaXpwIn0.ZU772lvU-NeKNFAkukT6hw';

// mdhalee token
// mapboxgl.accessToken = 'pk.eyJ1IjoibWRoYWxsZWUiLCJhIjoiY2tjcWVscWkyMTN6czM0bGJ4eXB1dDNzMSJ9.ZqDUoCfQVWMN_ASDB9Mhdg';

const mbToken = 'pk.eyJ1Ijoib3BlbnByZWNpbmN0cyIsImEiOiJjanVqMHJtM3gwMXdyM3lzNmZkbmpxaXpwIn0.ZU772lvU-NeKNFAkukT6hw';
mapboxgl.accessToken = mbToken;

let house_lookup_data;
let senate_lookup_data;

const zoomThreshold = 2;
const zoomState = 5.2;

var map = new mapboxgl.Map({
    container: 'map-container',
    // style: 'mapbox://styles/mdhallee/ckd9fgs5405tt1iphjqsl6zwk',
    style: 'mapbox://styles/mapbox/light-v10',
    center: [-88, 40],
    zoom: 4.1
});
map.getCanvas().style.cursor = 'pointer';

// const bbox = [[-63.588704947691994, 50.715649574086314], [-127.55862265048071, 22.645896726596078]];
// map.fitBounds(bbox, {
//     padding: {top: 10, bottom:25, left: 15, right: 5},
//     linear: true,
// });

map.on('load', function() {
    house_lookup_data = filterHouseTable(mbleg4_table);
    senate_lookup_data = filterSenateTable(mbleg3_table);

    map.addSource('state-senate-boundary', {
        type: 'vector',
        url: 'mapbox://mapbox.boundaries-leg3-v3'
    });
    map.addSource('state-house-boundary', {
        type: 'vector',
        url: 'mapbox://mapbox.boundaries-leg4-v3'
    });

    function setSenate(e) {
        moneyball_data.forEach(function(row) {
            let sanitized_row_geoid = row.geoid;
            if (senate_lookup_data[sanitized_row_geoid] === undefined) {
                if (sanitized_row_geoid.length === 4) {
                    sanitized_row_geoid = "0" + sanitized_row_geoid;
                }
            }
            if (row.chamber === 'SD') {
                map.setFeatureState({
                    source: 'state-senate-boundary',
                    sourceLayer: 'boundaries_legislative_3',
                    id: senate_lookup_data[sanitized_row_geoid].feature_id
                }, {
                    redistricting_voter_power: row.redistricting_voter_power
                })
            }
        });
    }
    function setHouse(e) {
        moneyball_data.forEach(function(row) {
            let sanitized_row_geoid = row.geoid;
            if (house_lookup_data[sanitized_row_geoid] === undefined) {
                if (sanitized_row_geoid.length === 4) {
                    sanitized_row_geoid = "0" + sanitized_row_geoid;
                }
            }
            if (row.chamber === 'HD') {
                map.setFeatureState({
                    source: 'state-house-boundary',
                    sourceLayer: 'boundaries_legislative_4',
                    id: house_lookup_data[sanitized_row_geoid].feature_id
                }, {
                    redistricting_voter_power: row.redistricting_voter_power
                })
            }
        });
    }

    function setHouseAfterLoad(e) {
        if (e.sourceId === 'state-house-boundary' && e.isSourceLoaded) {
            setHouse();
            map.off('state-house-boundary', setHouseAfterLoad)
        }
    }

    function setSenateAfterLoad(e) {
        if (e.sourceId === 'state-senate-boundary' && e.isSourceLoaded) {
            setSenate();
            map.off('state-senate-boundary', setSenateAfterLoad)
        }
    }

    if (map.isSourceLoaded('state-senate-boundary')) {
        setSenate();
    } else {
        map.on('sourcedata', setSenateAfterLoad);
    }

    if (map.isSourceLoaded('state-house-boundary')) {
        setHouse();
    } else {
        map.on('sourcedata', setHouseAfterLoad);
    }

    map.addLayer({
        'id': 'state-senate-boundary',
        'type': 'fill',
        'source': 'state-senate-boundary',
        'source-layer': 'boundaries_legislative_3',
        'paint': {
            'fill-outline-color': '#c4c4c4',
            'fill-opacity': [
                "case",
                [
                    "!=",
                    ["feature-state", "redistricting_voter_power"],
                    null
                ],
                .8,
                0.5
            ],
            'fill-color': [
                "case",
                [
                    "==",
                    ["feature-state", "redistricting_voter_power"],
                    null
                ],
                "hsla(0, 0%, 100%, 1)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  75
                ],
                "hsla(312, 99%, 55%, 1)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  45
                ],
                "hsla(288, 88%, 56%, .9)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  30
                ],
                "hsla(232, 82%, 69%, .8)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  7
                ],
                "hsla(193, 82%, 74%, .7)",
                // ['all', [">=", ["get", "VOTER_POWER"], 7], ["==", ["get", "POSTAL"], "NC"]],
                // "hsla(193, 82%, 74%, 0.75)",
                "hsla(0, 0%, 100%, 0)"
              ]
        },
        'layout': {
            'visibility': 'none'
        }
    });
    map.addLayer({
        'id': 'state-house-boundary',
        'type': 'fill',
        'source': 'state-house-boundary',
        'source-layer': 'boundaries_legislative_4',
        'paint': {
            'fill-outline-color': '#c4c4c4',
            'fill-opacity': [
                "case",
                [
                    "!=",
                    ["feature-state", "redistricting_voter_power"],
                    null
                ],
                .8,
                0.5
            ],
            'fill-color': [
                "case",
                [
                    "==",
                    ["feature-state", "redistricting_voter_power"],
                    null
                ],
                "hsla(0, 0%, 100%, 1)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  75
                ],
                "hsla(312, 99%, 55%, 1)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  45
                ],
                "hsla(288, 88%, 56%, .9)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  30
                ],
                "hsla(232, 82%, 69%, .8)",
                [
                  ">=",
                  ["feature-state", "redistricting_voter_power"],
                  7
                ],
                "hsla(193, 82%, 74%, .7)",
                "hsla(0, 0%, 100%, 1)"
              ]
        },
        'layout': {
            'visibility': 'visible'
        }
    });
});
    // // State-House-layer click and pop-up stuff
    map.on('click', 'state-house-boundary', function(e) {
        // e.originalEvent.cancelBubble = true; 
        let pointInPolygonResponse;
        $.get(`https://api.mapbox.com/v4/mapbox.boundaries-leg4-v3/tilequery/${e.lngLat.lng},${e.lngLat.lat}.json?access_token=${mbToken}`,
            function(data) {
                pointInPolygonResponse = data;
                const houseFeature = getFromHouseLookupTableByFeatureId(data.features[0].id);
                const selectedMoneyballFeature = getMoneyballDataByUnitCode(houseFeature.unit_code);
                if (selectedMoneyballFeature.redistricting_voter_power < 1) {
                    return;
                }
                const state = selectedMoneyballFeature.state;
                
                if (state !== $('#sstates').val()) {
                    $('#sstates').val(state)
                    $('#allstcheckbx').prop( "checked", false );
                    $("#submit").click();
                    
                    updateStateInfoSidebar(state)
                }
                
                let myCongressionalTable = buildDistrictHoverTable(selectedMoneyballFeature)
                
                let el = document.createElement('div');
                el.className = 'marker'
                new mapboxgl.Popup(el)
                    .setLngLat(e.lngLat)
                    .setHTML(myCongressionalTable)
                    .addTo(map);
            }
        )
    });

    // State-Senate-layer click and pop-up stuff
    map.on('click', 'state-senate-boundary', function(e) {
        // e.originalEvent.cancelBubble = true; 
        let pointInPolygonResponse;
        $.get(`https://api.mapbox.com/v4/mapbox.boundaries-leg3-v3/tilequery/${e.lngLat.lng},${e.lngLat.lat}.json?access_token=${mbToken}`,
            function(data) {
                pointInPolygonResponse = data;
                const senateFeature = getFromSenateLookupTableByFeatureId(data.features[0].id);
                const selectedMoneyballFeature = getMoneyballDataByUnitCode(senateFeature.unit_code);
                const state = selectedMoneyballFeature.state;
                
                if (state !== $('#sstates').val()) {
                    $('#sstates').val(state)
                    $('#allstcheckbx').prop( "checked", false );
                    $("#submit").click();
                    
                    updateStateInfoSidebar(state)
                }
                
                let el = document.createElement('div');
                el.className = 'marker'
                let myCongressionalTable = buildDistrictHoverTable(selectedMoneyballFeature)
        
                new mapboxgl.Popup(el)
                    .setLngLat(e.lngLat)
                    .setHTML(myCongressionalTable)
                    .addTo(map);
            }
        )
    });

    map.getCanvas().style.cursor = 'pointer';

    // add "Reset Map" 
    document.getElementById('zoom').addEventListener('click', function() {
        map.zoomTo(zoomThreshold);
        map.fitBounds(bbox, {
            // padding: {top: 10, bottom:25, left: 15, right: 5},
            linear: true,
            });
        map.setLayoutProperty('state-house-boundary', 'visibility', 'visible');
        map.setLayoutProperty('state-senate-boundary', 'visibility', 'none');
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
        // console.log("new selected layer is", this.value);
        clickedLayer = this.value +'-boundary';
        var visibility = map.getLayoutProperty(clickedLayer, 'visibility');
        // toggle layer visibility by changing the layout object's visibility property
        if (clickedLayer === 'state-house-boundary'){
            map.setLayoutProperty('state-house-boundary', 'visibility', 'visible');
            map.setLayoutProperty('state-senate-boundary', 'visibility', 'none');
        } else if (clickedLayer === 'state-senate-boundary'){
            map.setLayoutProperty('state-house-boundary', 'visibility', 'none');
            map.setLayoutProperty('state-senate-boundary', 'visibility', 'visible');
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
    
        if (prop.redistricting_voter_power >= 1 & prop.incumbent == 'R'){
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.district + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.redistricting_voter_power.toFixed(0) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.favored + '</td>' + 
            '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.dem_nominee + '</td>' + 
            '<tr> <th>' + "R Candidate (Incumbent)" + '</th> <th style="text-decoration: underline">' + prop.rep_nominee + '</th>' + 
            '</table>'
    
        }
        else if (prop.redistricting_voter_power >= 1 & prop.incumbent == 'D'){
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.district + '</td>' + 
            '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.redistricting_voter_power.toFixed(0) + '</td>' + 
            '<tr> <th>' + "Rating" + '</th> <td>' + prop.favored + '</td>' + 
            '<tr> <th>' + "D Candidate (Incumbent)" + '</th> <th style="text-decoration: underline">' + prop.dem_nominee +'</th>' + 
            '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.rep_nominee +  '</td>' + 
            '</table>'
        }
        else if (prop.redistricting_voter_power >= 1){
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.district + '</td>' + 
                                        '<tr> <th>' + "Voter Power" + '</th> <td>' + prop.redistricting_voter_power.toFixed(0) + '</td>' + 
                                    '<tr> <th>' + "Rating" + '</th> <td>' + prop.favored + '</td>' + 
                                    '<tr> <th>' + "D Candidate" + '</th> <td>' + prop.dem_nominee + '</td>' + 
                                    '<tr> <th>' + "R Candidate" + '</th> <td>' + prop.rep_nominee + '</td>' + 
                                        '</table>'
        }
        else {
            districtTable = '<table> <tr> <th>' + "District" + '</th> <td>' + prop.district + '</td>' + 
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
        updateStateInfoSidebar('TX');

        window.history.replaceState(null, null, "?key_state=TX");
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
        updateStateInfoSidebar('MN');

        window.history.replaceState(null, null, "?key_state=MN");
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
        updateStateInfoSidebar('KS');

        window.history.replaceState(null, null, "?key_state=KS");
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
        updateStateInfoSidebar('FL');

        window.history.replaceState(null, null, "?key_state=FL");
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
        updateStateInfoSidebar('CT');

        window.history.replaceState(null, null, "?key_state=CT");
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
        updateStateInfoSidebar('NC');

        window.history.replaceState(null, null, "?key_state=NC");
    });
    $("#ne-link").click(function() {
        $('#dropdown').val("state-senate")
        document.querySelector("#dropdown").dispatchEvent(new Event("change"));
        map.flyTo({
            center: [-99.51, 41.31], 
            zoom: 6.2,
            speed: 0.4,
            curve: 1
        })
        $('#sstates').val('NE')
        $( '#allstcheckbx' ).prop( "checked", false );
        $( "#submit").click();
        updateStateInfoSidebar('NE');

        window.history.replaceState(null, null, "?key_state=NE");
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

    // State Url Parameter Handling
    const parsedUrl = new URL(window.location.href);
    url_state_param = parsedUrl.searchParams.get("key_state")
    if (url_state_param !== null){
        url_state_param = url_state_param.toLowerCase()
        // console.log(url_state_param)
        key_states = ['tx','mn','ks','fl','ct','nc', 'ne']
        if (key_states.includes(url_state_param)){
            jquery_string = "#"+ url_state_param + "-link"
            $(jquery_string).click()
        }
    }
// });
