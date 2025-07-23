import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { sleep, useStartCheck } from "../../functions";
mapboxgl.accessToken = "pk.eyJ1Ijoia2xhdXNzbWFyY2hpIiwiYSI6ImNsbGNsb245dzAyNXkzbm9iZzJ4emt2eWsifQ.HznsI_vVJ-lWe9swvbfT-Q";



export default function RenderMap({data=[]}){
    const map = useRef(null);
    const mapContainer = useRef(null);
	const [lng, setLng] = useState(-50.02);
	const [lat, setLat] = useState(-24.79);
	const [zoom, setZoom] = useState(0);
    useStartCheck(firstRender)
    useStartCheck(updateMarkers, [data])
    
    function firstRender(){
        if(map.current) 
            return;

        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: "mapbox://styles/mapbox/dark-v10",
            center: [lng, lat],
            zoom: zoom,
        });

        map.current.on("move", () => {
            setLng(parseFloat(map.current.getCenter().lng.toFixed(4)));
            setLat(parseFloat(map.current.getCenter().lat.toFixed(4)));
            setZoom(parseFloat(map.current.getZoom().toFixed(2)));
        });
    }

    async function getMarkers() {
		let markers = [];

		for (let x = 0; x < data.length; x++)
			markers.push({
				lng: data[x].lng,
				lat: data[x].lat
			})
		
		return markers;
	}

	async function updateMarkers(){
		const markers = await getMarkers()

		map.current = new mapboxgl.Map({
			container: mapContainer.current,
			style: "mapbox://styles/mapbox/dark-v10",
			center: [lng, lat],
			zoom: zoom,
		});

		map.current.on("move", () => {
			setLng(parseFloat(map.current.getCenter().lng.toFixed(4)));
			setLat(parseFloat(map.current.getCenter().lat.toFixed(4)));
			setZoom(parseFloat(map.current.getZoom().toFixed(2)));
		});

		for (let x = 0; x < markers.length; x++) {
			const el = document.createElement('div');
			el.className = 'marker';
			el.style.width = '10px'; 		  // Define a largura do marcador
			el.style.height = '10px'; 	      // Define a altura do marcador
			el.style.backgroundColor = '#00ff58'; // Define a cor do marcador
			el.style.borderRadius = '50%';

			const marker = new mapboxgl.Marker(el, {
				color: "#00ff58",
				draggable: false,
				clickTolerance: 5,
			})

			marker.setLngLat([markers[x].lng, markers[x].lat])
			marker.addTo(map.current);	

			if (markers.length > 0)
				await changeMapCenter(markers[0].lat, markers[0].lng);
		}
	}

    async function changeMapCenter(newLat, newLng) {
		await sleep(100);

		setLat(newLat);
		setLng(newLng);

		if (map.current) {
			map.current.flyTo({
				center: [newLng, newLat],
				essential: true,
			});
		}
	}

    return (
		<div
			ref={mapContainer}
			style={{ width: "100%", height: "100%", backgroundColor: "#2c2c2c", borderRadius: '5px'}}
		/>
	);
}