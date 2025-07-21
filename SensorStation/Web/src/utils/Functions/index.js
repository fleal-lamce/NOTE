import { useEffect } from "react";


export function useStartCheck(callback, params=[]){
	useEffect(() => {
		async function check() {
			await callback();
		}

		check();
	}, params);
}

export function usePeriodicCheck(callback, delay){
	useEffect(() => {
		const intervalId = setInterval(callback, delay);

		return function cleanup() {
			clearInterval(intervalId);
		};
	}, [callback, delay]);
}

export async function sleep(ms){
	await new Promise(resolve => setTimeout(resolve, ms));
}